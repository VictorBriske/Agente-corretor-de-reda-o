"""
Rotas de redações (submissão e consulta)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import uuid
from datetime import datetime
import logging

from app.schemas.redacao import RedacaoSubmit, RedacaoResponse
from app.schemas.usuario import TokenData
from app.services.auth_service import get_current_user
from app.database import get_db
from app.models.redacao import Redacao, StatusRedacaoEnum
from app.models.analise import Analise
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/redacoes", response_model=RedacaoResponse, status_code=status.HTTP_201_CREATED)
async def submeter_redacao(
    redacao: RedacaoSubmit,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submete uma redação para análise.
    A redação será processada automaticamente por um worker em background.
    """
    # Validações
    if len(redacao.texto) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O texto deve ter no mínimo 100 caracteres"
        )
    
    if len(redacao.texto) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O texto deve ter no máximo 10.000 caracteres"
        )
    
    # Criar redação no banco de dados
    redacao_id = str(uuid.uuid4())
    
    nova_redacao = Redacao(
        id=redacao_id,
        usuario_id=current_user.usuario_id,
        titulo=redacao.titulo,
        texto=redacao.texto,
        tema=redacao.tema,
        tipo=redacao.tipo,
        status=StatusRedacaoEnum.PENDENTE
    )
    
    db.add(nova_redacao)
    db.commit()
    db.refresh(nova_redacao)
    
    logger.info(f"[REDACAO] Redacao {redacao_id} submetida pelo usuario {current_user.usuario_id}")
    print(f"[REDACAO] Redacao {redacao_id} submetida - status: PENDENTE")
    
    return RedacaoResponse(
        id=nova_redacao.id,
        usuario_id=nova_redacao.usuario_id,
        titulo=nova_redacao.titulo,
        texto=nova_redacao.texto,
        tema=nova_redacao.tema,
        tipo=nova_redacao.tipo,
        data_submissao=nova_redacao.data_submissao,
        status=nova_redacao.status.value,
        nota_enem=None,
        nota_geral=None
    )


@router.get("/redacoes/{redacao_id}", response_model=RedacaoResponse)
async def obter_redacao(
    redacao_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém uma redação específica
    """
    redacao = db.query(Redacao).filter(Redacao.id == redacao_id).first()
    
    if not redacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Redação não encontrada"
        )
    
    # Verificar se é do usuário
    if redacao.usuario_id != current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta redação"
        )
    
    # Se houver análise, anexar nota
    analise = db.query(Analise).filter(Analise.redacao_id == redacao.id).first()
    nota_enem = None
    nota_geral = None
    if analise and analise.avaliacao_final:
        try:
            nota_enem = analise.avaliacao_final.get("nota_enem")
            nota_geral = analise.avaliacao_final.get("nota_geral")
        except Exception:
            pass

    return RedacaoResponse(
        id=redacao.id,
        usuario_id=redacao.usuario_id,
        titulo=redacao.titulo,
        texto=redacao.texto,
        tema=redacao.tema,
        tipo=redacao.tipo,
        data_submissao=redacao.data_submissao,
        status=redacao.status.value,
        nota_enem=nota_enem,
        nota_geral=nota_geral
    )


@router.get("/redacoes", response_model=List[RedacaoResponse])
async def listar_redacoes(
    current_user: TokenData = Depends(get_current_user),
    limite: int = 10,
    db: Session = Depends(get_db)
):
    """
    Lista redações do usuário
    """
    rows = (
        db.query(Redacao, Analise)
        .outerjoin(Analise, Analise.redacao_id == Redacao.id)
        .filter(Redacao.usuario_id == current_user.usuario_id)
        .order_by(Redacao.data_submissao.desc())
        .limit(limite)
        .all()
    )

    resp: List[RedacaoResponse] = []
    for r, a in rows:
        nota_enem = None
        nota_geral = None
        if a and a.avaliacao_final:
            try:
                nota_enem = a.avaliacao_final.get("nota_enem")
                nota_geral = a.avaliacao_final.get("nota_geral")
            except Exception:
                pass

        resp.append(
            RedacaoResponse(
                id=r.id,
                usuario_id=r.usuario_id,
                titulo=r.titulo,
                texto=r.texto,
                tema=r.tema,
                tipo=r.tipo,
                data_submissao=r.data_submissao,
                status=r.status.value,
                nota_enem=nota_enem,
                nota_geral=nota_geral
            )
        )

    return resp

