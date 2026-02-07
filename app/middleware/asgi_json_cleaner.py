"""
Middleware ASGI de baixo nível para limpar JSON antes do FastAPI processar
"""

import re
import json
import logging

logger = logging.getLogger(__name__)


def limpar_caracteres_controle(texto: str) -> str:
    """Remove caracteres de controle inválidos"""
    if not texto:
        return texto
    # Remover caracteres de controle (exceto \n, \r, \t)
    texto_limpo = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', texto)
    # Normalizar quebras de linha
    texto_limpo = texto_limpo.replace('\r\n', '\n').replace('\r', '\n')
    return texto_limpo


class ASGIJSONCleaner:
    """
    Middleware ASGI que limpa caracteres de controle do JSON
    antes de qualquer processamento
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Apenas processar requisições HTTP
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Verificar se é POST/PUT/PATCH com JSON
        method = scope.get("method", "")
        headers = dict(scope.get("headers", []))
        
        content_type = headers.get(b"content-type", b"").decode("latin-1", errors="ignore").lower()
        
        if method in ["POST", "PUT", "PATCH"] and "application/json" in content_type:
            logger.info(f"[ASGI_CLEANER] Interceptando requisição {method} com Content-Type JSON")
            print(f"[ASGI_CLEANER] Interceptando requisição {method} com Content-Type JSON")
            
            # Interceptar o receive
            body_chunks = []
            body_completo = False
            
            async def receive_limpo():
                nonlocal body_completo, body_chunks
                
                if body_completo:
                    return {"type": "http.request", "body": b""}
                
                message = await receive()
                
                if message.get("type") == "http.request":
                    body = message.get("body", b"")
                    
                    if body:
                        body_chunks.append(body)
                    
                    # Se é a última mensagem, processar
                    if not message.get("more_body", False) and body_chunks:
                        body_completo = True
                        
                        # Juntar chunks
                        body_bytes = b"".join(body_chunks)
                        
                        # Decodificar
                        try:
                            body_str = body_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            body_str = body_bytes.decode('utf-8', errors='replace')
                        
                        logger.info(f"[ASGI_CLEANER] Body: {len(body_str)} chars")
                        print(f"[ASGI_CLEANER] Body recebido: {len(body_str)} caracteres")
                        
                        # Limpar caracteres de controle
                        body_limpo = limpar_caracteres_controle(body_str)
                        
                        if len(body_limpo) != len(body_str):
                            removidos = len(body_str) - len(body_limpo)
                            logger.info(f"[ASGI_CLEANER] Removidos {removidos} caracteres de controle")
                            print(f"[ASGI_CLEANER] Removidos {removidos} caracteres de controle")
                        
                        # Validar JSON
                        try:
                            json_data = json.loads(body_limpo)
                            
                            # Limpar strings dentro do JSON
                            if isinstance(json_data, dict):
                                def limpar_dict(d):
                                    for k, v in d.items():
                                        if isinstance(v, str):
                                            d[k] = limpar_caracteres_controle(v)
                                        elif isinstance(v, dict):
                                            limpar_dict(v)
                                        elif isinstance(v, list):
                                            for i, item in enumerate(v):
                                                if isinstance(item, str):
                                                    v[i] = limpar_caracteres_controle(item)
                                                elif isinstance(item, dict):
                                                    limpar_dict(item)
                                limpar_dict(json_data)
                            
                            # Recriar JSON limpo
                            body_limpo_final = json.dumps(json_data, ensure_ascii=False)
                            body_limpo_bytes = body_limpo_final.encode('utf-8')
                            
                            logger.info(f"[ASGI_CLEANER] JSON valido apos limpeza")
                            print(f"[ASGI_CLEANER] JSON valido apos limpeza")
                            
                            # Retornar body limpo
                            return {
                                "type": "http.request",
                                "body": body_limpo_bytes,
                                "more_body": False
                            }
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"[ASGI_CLEANER] JSON invalido apos limpeza: {str(e)}")
                            logger.error(f"[ASGI_CLEANER] Posicao: {e.pos}")
                            print(f"[ASGI_CLEANER] JSON invalido apos limpeza: {str(e)}")
                            print(f"[ASGI_CLEANER] Posicao: {e.pos}")
                            
                            # Mostrar contexto do erro
                            if e.pos and e.pos < len(body_limpo):
                                inicio = max(0, e.pos - 100)
                                fim = min(len(body_limpo), e.pos + 100)
                                contexto = body_limpo[inicio:fim]
                                print(f"[ASGI_CLEANER] Contexto do erro: ...{contexto}...")
                            
                            # Enviar resposta de erro
                            error_response = {
                                "type": "http.response.start",
                                "status": 422,
                                "headers": [[b"content-type", b"application/json"]],
                            }
                            await send(error_response)
                            
                            error_body = json.dumps({
                                "detail": [
                                    {
                                        "type": "json_invalid",
                                        "loc": ["body", e.pos] if e.pos else ["body"],
                                        "msg": f"Erro ao decodificar JSON na posição {e.pos}: {str(e)}. "
                                               f"Caracteres de controle foram removidos automaticamente. "
                                               f"Verifique se o JSON está bem formatado.",
                                        "input": {}
                                    }
                                ]
                            }).encode('utf-8')
                            
                            await send({
                                "type": "http.response.body",
                                "body": error_body,
                                "more_body": False
                            })
                            return
                        except Exception as e:
                            logger.error(f"[ASGI_CLEANER] Erro ao processar JSON: {str(e)}")
                            print(f"[ASGI_CLEANER] Erro ao processar JSON: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            # Continuar normalmente (deixar FastAPI tratar)
                
                return message
            
            # Usar receive limpo
            try:
                await self.app(scope, receive_limpo, send)
            except Exception as e:
                logger.error(f"[ASGI_CLEANER] Erro ao processar app: {str(e)}")
                print(f"[ASGI_CLEANER] Erro ao processar app: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
        else:
            # Para outras requisições, passar direto
            await self.app(scope, receive, send)

