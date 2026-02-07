"""
Middleware para limpar caracteres de controle inválidos do JSON
antes do parsing pelo FastAPI
"""

import re
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
import logging

logger = logging.getLogger(__name__)


def limpar_caracteres_controle(texto: str) -> str:
    """
    Remove caracteres de controle inválidos do texto
    Mantém apenas quebras de linha válidas (\n, \r, \t)
    """
    if not texto:
        return texto
    
    # Remover caracteres de controle inválidos
    # Manter: \n (0x0A), \r (0x0D), \t (0x09)
    # Remover: 0x00-0x08, 0x0B-0x0C, 0x0E-0x1F
    texto_limpo = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', texto)
    
    # Normalizar quebras de linha
    texto_limpo = texto_limpo.replace('\r\n', '\n').replace('\r', '\n')
    
    return texto_limpo


class JSONCleanerMiddleware(BaseHTTPMiddleware):
    """
    Middleware que limpa caracteres de controle inválidos do body JSON
    antes do FastAPI tentar fazer o parse
    """
    
    async def dispatch(self, request: Request, call_next):
        # Apenas processar requisições POST/PUT/PATCH com Content-Type JSON
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type.lower():
                try:
                    # Interceptar o receive ANTES de qualquer leitura
                    original_receive = request._receive
                    body_chunks = []
                    body_consumido = False
                    
                    async def receive_limpo():
                        nonlocal body_consumido, body_chunks
                        
                        if body_consumido:
                            return {"type": "http.request", "body": b""}
                        
                        # Ler mensagem original
                        message = await original_receive()
                        
                        if message.get("type") == "http.request":
                            body = message.get("body", b"")
                            
                            if body:
                                body_chunks.append(body)
                            
                            # Se é a última mensagem (more_body = False), processar
                            if not message.get("more_body", False) and body_chunks:
                                body_consumido = True
                                
                                # Juntar todos os chunks
                                body_bytes = b"".join(body_chunks)
                                
                                # Decodificar
                                try:
                                    body_str = body_bytes.decode('utf-8')
                                except UnicodeDecodeError:
                                    body_str = body_bytes.decode('utf-8', errors='replace')
                                
                                logger.info(f"[JSON_CLEANER] Body recebido: {len(body_str)} caracteres")
                                print(f"[JSON_CLEANER] Body recebido: {len(body_str)} caracteres")
                                
                                # Limpar caracteres de controle
                                body_limpo = limpar_caracteres_controle(body_str)
                                
                                if len(body_limpo) != len(body_str):
                                    logger.info(f"[JSON_CLEANER] Removidos {len(body_str) - len(body_limpo)} caracteres de controle")
                                    print(f"[JSON_CLEANER] Removidos {len(body_str) - len(body_limpo)} caracteres de controle")
                                
                                # Verificar se é JSON válido
                                try:
                                    json_data = json.loads(body_limpo)
                                    
                                    # Limpar caracteres de controle dos campos de string dentro do JSON
                                    if isinstance(json_data, dict):
                                        for key, value in json_data.items():
                                            if isinstance(value, str):
                                                json_data[key] = limpar_caracteres_controle(value)
                                    
                                    # Recriar o JSON limpo
                                    body_limpo_final = json.dumps(json_data, ensure_ascii=False)
                                    body_limpo_bytes = body_limpo_final.encode('utf-8')
                                    
                                    logger.info(f"[JSON_CLEANER] JSON limpo e valido ({len(body_limpo_final)} chars)")
                                    print(f"[JSON_CLEANER] JSON limpo e valido ({len(body_limpo_final)} chars)")
                                    
                                    # Retornar body limpo
                                    return {
                                        "type": "http.request",
                                        "body": body_limpo_bytes,
                                        "more_body": False
                                    }
                                    
                                except json.JSONDecodeError as e:
                                    logger.error(f"[JSON_CLEANER] JSON invalido apos limpeza: {str(e)}")
                                    logger.error(f"[JSON_CLEANER] Posicao: {e.pos}")
                                    print(f"[JSON_CLEANER] JSON invalido apos limpeza: {str(e)}")
                                    print(f"[JSON_CLEANER] Posicao: {e.pos}")
                                    
                                    # Mostrar contexto
                                    if e.pos and e.pos < len(body_limpo):
                                        inicio = max(0, e.pos - 50)
                                        fim = min(len(body_limpo), e.pos + 50)
                                        contexto = body_limpo[inicio:fim]
                                        print(f"[JSON_CLEANER] Contexto: ...{contexto}...")
                                    
                                    # Retornar erro
                                    raise ValueError(f"JSON invalido na posicao {e.pos}: {str(e)}")
                            
                            return message
                        
                        return message
                    
                    # Substituir o receive
                    request._receive = receive_limpo
                    
                except ValueError as e:
                    # Erro de JSON inválido
                    logger.error(f"[JSON_CLEANER] Erro capturado: {str(e)}")
                    print(f"[JSON_CLEANER] Erro capturado: {str(e)}")
                    return JSONResponse(
                        status_code=422,
                        content={
                            "detail": [
                                {
                                    "type": "json_invalid",
                                    "loc": ["body"],
                                    "msg": f"Erro ao decodificar JSON: {str(e)}. "
                                           f"Caracteres de controle foram removidos automaticamente, mas o JSON ainda está inválido.",
                                    "input": {}
                                }
                            ]
                        }
                    )
                except Exception as e:
                    logger.error(f"[JSON_CLEANER] Erro no middleware: {str(e)}")
                    print(f"[JSON_CLEANER] Erro no middleware: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        # Continuar com a requisição
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"[JSON_CLEANER] Erro ao processar request: {str(e)}")
            print(f"[JSON_CLEANER] Erro ao processar request: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

