"""
Socratis - API Principal
Sistema de análise inteligente de redações com método socrático
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
import json
import re

from app.routers import redacao, usuario, analise
from app.config import settings
from app.middleware.asgi_json_cleaner import ASGIJSONCleaner
from app.services.redacao_worker import worker

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log no console
    ]
)

logger = logging.getLogger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    print("Iniciando Socratis...")
    print(f"Modo: {settings.ENVIRONMENT}")
    
    # Iniciar worker de processamento de redações
    logger.info("[MAIN] Iniciando worker de processamento de redações...")
    print("[MAIN] Iniciando worker de processamento de redações...")
    worker.start()
    
    yield
    
    # Parar worker ao encerrar
    logger.info("[MAIN] Parando worker de processamento de redações...")
    print("[MAIN] Parando worker de processamento de redações...")
    worker.stop()
    print("Encerrando aplicacao...")


# Inicialização do FastAPI
app = FastAPI(
    title="Socratis",
    description="API para análise inteligente de redações com método socrático",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
# Em desenvolvimento, permitir todas as origens locais
cors_origins = settings.ALLOWED_ORIGINS
if settings.ENVIRONMENT == "development":
    # Adicionar porta padrão do Angular se não estiver na lista
    if "http://localhost:4200" not in cors_origins:
        cors_origins.append("http://localhost:4200")
    if "http://127.0.0.1:4200" not in cors_origins:
        cors_origins.append("http://127.0.0.1:4200")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handler para HTTPException (incluindo 401)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handler customizado para HTTPException
    Garante que erros HTTP sejam retornados no formato correto
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Exception handler para erros de validação JSON
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler customizado para erros de validação JSON
    Fornece mensagens mais claras sobre caracteres inválidos
    """
    errors = exc.errors()
    
    # Verificar se é erro de JSON inválido
    for error in errors:
        if error.get("type") == "json_invalid":
            error_msg = error.get("ctx", {}).get("error", "Erro ao decodificar JSON")
            error_loc = error.get("loc", [])
            
            logger.error(f"[JSON_ERROR] Erro ao decodificar JSON: {error_msg}")
            logger.error(f"[JSON_ERROR] Localização: {error_loc}")
            print(f"[JSON_ERROR] Erro ao decodificar JSON: {error_msg}")
            print(f"[JSON_ERROR] Localização: {error_loc}")
            
            # Tentar ler o body novamente para debug
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        body_str = body_bytes.decode('utf-8', errors='replace')
                        # Mostrar contexto do erro se possível
                        if len(error_loc) > 1 and isinstance(error_loc[-1], int):
                            pos = error_loc[-1]
                            if pos < len(body_str):
                                inicio = max(0, pos - 100)
                                fim = min(len(body_str), pos + 100)
                                contexto = body_str[inicio:fim]
                                print(f"[JSON_ERROR] Contexto (pos {pos}): ...{contexto}...")
                    except:
                        pass
            except:
                pass
            
            return JSONResponse(
                status_code=422,
                content={
                    "detail": [
                        {
                            "type": "json_invalid",
                            "loc": error_loc,
                            "msg": f"Erro ao decodificar JSON: {error_msg}. "
                                   f"O middleware tentou limpar caracteres de controle automaticamente. "
                                   f"Verifique se o JSON está bem formatado. "
                                   f"Se o problema persistir, tente enviar o JSON novamente.",
                            "input": {}
                        }
                    ]
                }
            )
    
    # Para outros erros de validação, retornar resposta padrão
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

# Rotas principais
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Bem-vindo ao Socratis",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

@app.post("/test-json", tags=["Test"])
async def test_json(request: Request):
    """Endpoint de teste para verificar parsing de JSON"""
    try:
        body = await request.body()
        body_str = body.decode('utf-8', errors='replace')
        
        return {
            "status": "ok",
            "body_length": len(body_str),
            "body_preview": body_str[:200],
            "message": "JSON recebido com sucesso"
        }
    except Exception as e:
        logger.error(f"[TEST] Erro: {str(e)}")
        print(f"[TEST] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar: {str(e)}"
        )

# Inclusão de routers
app.include_router(usuario.router, prefix="/api/v1", tags=["Usuários"])
app.include_router(redacao.router, prefix="/api/v1", tags=["Redações"])
app.include_router(analise.router, prefix="/api/v1", tags=["Análises"])

# Aplicar middleware ASGI de baixo nível (envolve toda a aplicação)
# DEVE ser aplicado DEPOIS de configurar todos os middlewares, rotas e handlers do FastAPI
app = ASGIJSONCleaner(app)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

