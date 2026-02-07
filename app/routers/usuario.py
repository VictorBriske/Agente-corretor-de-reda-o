"""
Rotas de usuários (cadastro, login, perfil)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
import uuid
import traceback
import logging

from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioLogin,
    UsuarioResponse,
    Token,
    PlanoEnum,
    TokenData
)
from app.services.auth_service import auth_service, get_current_user
from app.config import settings
from app.database import get_db
from app.models.usuario import Usuario
from sqlalchemy.orm import Session

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/usuarios/cadastro", response_model=Token, status_code=status.HTTP_201_CREATED)
async def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Cadastra um novo usuário
    """
    try:
        logger.info(f"[CADASTRO] Iniciando cadastro de usuario: {usuario.email}")
        print(f"[CADASTRO] Iniciando cadastro de usuario: {usuario.email}")
        
        # Verificar se email já existe
        logger.info(f"[CADASTRO] Verificando se email ja existe: {usuario.email}")
        print(f"[CADASTRO] Verificando se email ja existe: {usuario.email}")
        
        usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
        if usuario_existente:
            logger.warning(f"[CADASTRO] Email ja cadastrado: {usuario.email}")
            print(f"[CADASTRO] Email ja cadastrado: {usuario.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        logger.info(f"[CADASTRO] Email disponivel, criando usuario...")
        print(f"[CADASTRO] Email disponivel, criando usuario...")
        
        # Criar usuário
        usuario_id = str(uuid.uuid4())
        logger.info(f"[CADASTRO] Gerando hash da senha...")
        print(f"[CADASTRO] Gerando hash da senha...")
        print(f"[CADASTRO] Tamanho da senha: {len(usuario.senha.encode('utf-8'))} bytes")
        
        try:
            hashed_password = auth_service.hash_password(usuario.senha)
        except ValueError as e:
            logger.error(f"[CADASTRO] Erro ao gerar hash: {str(e)}")
            print(f"[CADASTRO] Erro ao gerar hash: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        limite_diario = (
            settings.FREE_TIER_DAILY_LIMIT if usuario.plano == PlanoEnum.FREE
            else settings.PREMIUM_TIER_DAILY_LIMIT
        )
        
        logger.info(f"[CADASTRO] Criando objeto Usuario no banco...")
        print(f"[CADASTRO] Criando objeto Usuario no banco...")
        
        novo_usuario = Usuario(
            id=usuario_id,
            email=usuario.email,
            nome=usuario.nome,
            plano=usuario.plano,
            senha_hash=hashed_password,
            correcoes_realizadas_hoje=0,
            limite_diario=limite_diario
        )
        
        logger.info(f"[CADASTRO] Salvando usuario no banco de dados...")
        print(f"[CADASTRO] Salvando usuario no banco de dados...")
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        logger.info(f"[CADASTRO] Usuario salvo com sucesso. ID: {usuario_id}")
        print(f"[CADASTRO] Usuario salvo com sucesso. ID: {usuario_id}")
        
        # Gerar token
        logger.info(f"[CADASTRO] Gerando token JWT...")
        print(f"[CADASTRO] Gerando token JWT...")
        
        access_token = auth_service.create_access_token(
            data={
                "sub": usuario_id,
                "email": usuario.email,
                "plano": usuario.plano.value
            }
        )
        
        logger.info(f"[CADASTRO] Token gerado com sucesso")
        print(f"[CADASTRO] Token gerado com sucesso")
        
        usuario_response = UsuarioResponse(
            id=novo_usuario.id,
            email=novo_usuario.email,
            nome=novo_usuario.nome,
            plano=novo_usuario.plano,
            data_criacao=novo_usuario.data_criacao,
            correcoes_realizadas_hoje=novo_usuario.correcoes_realizadas_hoje,
            limite_diario=novo_usuario.limite_diario
        )
        
        logger.info(f"[CADASTRO] Cadastro concluido com sucesso para: {usuario.email}")
        print(f"[CADASTRO] Cadastro concluido com sucesso para: {usuario.email}")
        
        return Token(
            access_token=access_token,
            usuario=usuario_response
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (erros esperados)
        raise
    except Exception as e:
        logger.error(f"[CADASTRO] ERRO ao cadastrar usuario: {str(e)}")
        logger.error(f"[CADASTRO] Traceback: {traceback.format_exc()}")
        print(f"[CADASTRO] ERRO ao cadastrar usuario: {str(e)}")
        print(f"[CADASTRO] Traceback completo:")
        traceback.print_exc()
        
        # Rollback em caso de erro
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar usuário: {str(e)}"
        )


@router.post("/usuarios/login", response_model=Token)
async def login(credenciais: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Realiza login e retorna token JWT
    """
    try:
        logger.info(f"[LOGIN] Tentativa de login: {credenciais.email}")
        print(f"[LOGIN] Tentativa de login: {credenciais.email}")
        
        # Buscar usuário por email
        usuario = db.query(Usuario).filter(Usuario.email == credenciais.email).first()
        
        if not usuario:
            logger.warning(f"[LOGIN] Usuario nao encontrado: {credenciais.email}")
            print(f"[LOGIN] Usuario nao encontrado: {credenciais.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ou senha inválidos"
            )
        
        # Verificar senha
        if not auth_service.verify_password(credenciais.senha, usuario.senha_hash):
            logger.warning(f"[LOGIN] Senha incorreta para: {credenciais.email}")
            print(f"[LOGIN] Senha incorreta para: {credenciais.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ou senha inválidos"
            )
        
        # Gerar token
        access_token = auth_service.create_access_token(
            data={
                "sub": usuario.id,
                "email": usuario.email,
                "plano": usuario.plano.value
            }
        )
        
        usuario_response = UsuarioResponse(
            id=usuario.id,
            email=usuario.email,
            nome=usuario.nome,
            plano=usuario.plano,
            data_criacao=usuario.data_criacao,
            correcoes_realizadas_hoje=usuario.correcoes_realizadas_hoje,
            limite_diario=usuario.limite_diario
        )
        
        logger.info(f"[LOGIN] Login bem-sucedido: {credenciais.email}")
        print(f"[LOGIN] Login bem-sucedido: {credenciais.email}")
        
        return Token(
            access_token=access_token,
            usuario=usuario_response
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[LOGIN] ERRO ao fazer login: {str(e)}")
        logger.error(f"[LOGIN] Traceback: {traceback.format_exc()}")
        print(f"[LOGIN] ERRO ao fazer login: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer login: {str(e)}"
        )


@router.get("/usuarios/me", response_model=UsuarioResponse)
async def get_usuario_atual(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna dados do usuário logado
    """
    try:
        logger.info(f"[PERFIL] Buscando usuario: {current_user.usuario_id}")
        print(f"[PERFIL] Buscando usuario: {current_user.usuario_id}")
        
        usuario = db.query(Usuario).filter(Usuario.id == current_user.usuario_id).first()
        
        if not usuario:
            logger.warning(f"[PERFIL] Usuario nao encontrado: {current_user.usuario_id}")
            print(f"[PERFIL] Usuario nao encontrado: {current_user.usuario_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return UsuarioResponse(
            id=usuario.id,
            email=usuario.email,
            nome=usuario.nome,
            plano=usuario.plano,
            data_criacao=usuario.data_criacao,
            correcoes_realizadas_hoje=usuario.correcoes_realizadas_hoje,
            limite_diario=usuario.limite_diario
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PERFIL] ERRO ao buscar usuario: {str(e)}")
        logger.error(f"[PERFIL] Traceback: {traceback.format_exc()}")
        print(f"[PERFIL] ERRO ao buscar usuario: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar usuário: {str(e)}"
        )

