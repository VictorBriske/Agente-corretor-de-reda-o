"""
Rotas de análise (análise de redações - funcionalidade principal)
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import Optional
import uuid
from datetime import datetime
import traceback
import logging

from app.schemas.redacao import AnaliseCompleta, RedacaoSubmit
from app.schemas.usuario import TokenData, PlanoEnum
from app.services.auth_service import get_current_user
from app.agents.orquestrador import orquestrador
from app.config import settings
from app.database import get_db
from app.models.usuario import Usuario
from app.models.redacao import Redacao, StatusRedacaoEnum
from app.models.analise import Analise
from sqlalchemy.orm import Session

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analises/analisar", response_model=AnaliseCompleta)
async def analisar_redacao(
    redacao: RedacaoSubmit,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analisa uma redação usando o sistema multiagentes
    
    - **Free**: Análise gramatical + Detecção de fuga ao tema + Nota geral
    - **Premium**: Análise completa com todos os agentes + Funcionalidades extras
    """
    try:
        logger.info(f"[ANALISE] Iniciando analise para usuario: {current_user.usuario_id}")
        print(f"[ANALISE] Iniciando analise para usuario: {current_user.usuario_id}")
        
        # Obter dados do usuário
        usuario = db.query(Usuario).filter(Usuario.id == current_user.usuario_id).first()
        
        if not usuario:
            logger.error(f"[ANALISE] Usuario nao encontrado: {current_user.usuario_id}")
            print(f"[ANALISE] Usuario nao encontrado: {current_user.usuario_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar limite diário
        if usuario.correcoes_realizadas_hoje >= usuario.limite_diario:
            logger.warning(f"[ANALISE] Limite diario atingido para usuario: {current_user.usuario_id}")
            print(f"[ANALISE] Limite diario atingido para usuario: {current_user.usuario_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Limite diário de {usuario.limite_diario} análises atingido. "
                       f"Considere fazer upgrade para Premium!"
            )
        
        # Validações
        if len(redacao.texto) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O texto deve ter no mínimo 100 caracteres"
            )
        
        # Criar registro de redação
        redacao_id = str(uuid.uuid4())
        logger.info(f"[ANALISE] Criando redacao: {redacao_id}")
        print(f"[ANALISE] Criando redacao: {redacao_id}")
        
        nova_redacao = Redacao(
            id=redacao_id,
            usuario_id=current_user.usuario_id,
            titulo=redacao.titulo,
            texto=redacao.texto,
            tema=redacao.tema,
            tipo=redacao.tipo,
            status=StatusRedacaoEnum.ANALISANDO
        )
        
        db.add(nova_redacao)
        db.commit()
        db.refresh(nova_redacao)
        
        try:
            # Executar análise
            logger.info(f"[ANALISE] Executando analise da redacao {redacao_id} ({usuario.plano.value})...")
            print(f"[INIT] Iniciando analise da redacao {redacao_id} ({usuario.plano.value})...")
            
            analise_completa = await orquestrador.analisar_redacao(
                redacao=redacao,
                plano_usuario=usuario.plano,
                redacao_id=redacao_id
            )
            
            # Salvar análise no banco
            logger.info(f"[ANALISE] Salvando analise no banco...")
            print(f"[ANALISE] Salvando analise no banco...")
            
            nova_analise = Analise(
                id=redacao_id,
                redacao_id=redacao_id,
                plano_usuario=analise_completa.plano_usuario,
                tempo_processamento=analise_completa.tempo_processamento,
                tokens_utilizados=analise_completa.tokens_utilizados,
                analise_gramatical=analise_completa.analise_gramatical.dict(),
                analise_logica=analise_completa.analise_logica.dict() if analise_completa.analise_logica else None,
                analise_estrutural=analise_completa.analise_estrutural.dict() if analise_completa.analise_estrutural else None,
                repertorio_sociocultural=analise_completa.repertorio_sociocultural.dict() if analise_completa.repertorio_sociocultural else None,
                reescritas_comparativas=[r.dict() for r in analise_completa.reescritas_comparativas] if analise_completa.reescritas_comparativas else None,
                modo_socratico=analise_completa.modo_socratico.dict() if analise_completa.modo_socratico else None,
                avaliacao_final=analise_completa.avaliacao_final.dict(),
                fuga_ao_tema={"fuga": analise_completa.fuga_ao_tema, "aderencia": analise_completa.aderencia_tema, "palavras": analise_completa.palavras_chave_usadas},
                aderencia_tema=analise_completa.aderencia_tema,
                palavras_chave_usadas=analise_completa.palavras_chave_usadas
            )
            
            db.add(nova_analise)
            
            # Atualizar status da redação
            nova_redacao.status = StatusRedacaoEnum.CONCLUIDA
            
            # Incrementar contador de análises
            usuario.correcoes_realizadas_hoje += 1
            
            db.commit()
            
            logger.info(f"[ANALISE] Analise da redacao {redacao_id} concluida!")
            print(f"[OK] Analise da redacao {redacao_id} concluida!")
            
            return analise_completa
            
        except Exception as e:
            # Atualizar status da redação para erro
            nova_redacao.status = StatusRedacaoEnum.ERRO
            db.commit()
            
            logger.error(f"[ANALISE] Erro ao analisar redacao {redacao_id}: {str(e)}")
            logger.error(f"[ANALISE] Traceback: {traceback.format_exc()}")
            print(f"[ERROR] Erro ao analisar redacao {redacao_id}: {str(e)}")
            traceback.print_exc()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar análise: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ANALISE] ERRO geral: {str(e)}")
        logger.error(f"[ANALISE] Traceback: {traceback.format_exc()}")
        print(f"[ANALISE] ERRO geral: {str(e)}")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar análise: {str(e)}"
        )


@router.get("/analises/{redacao_id}", response_model=AnaliseCompleta)
async def obter_analise(
    redacao_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém uma análise específica
    """
    analise_db = db.query(Analise).filter(Analise.id == redacao_id).first()
    
    if not analise_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )
    
    # Verificar se a redação pertence ao usuário
    redacao = db.query(Redacao).filter(Redacao.id == redacao_id).first()
    if redacao and redacao.usuario_id != current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta análise"
        )
    
    # Converter de dict para AnaliseCompleta
    from app.schemas.redacao import (
        AnaliseGramatical, AnaliseLogica, AnaliseEstrutural,
        RepertorioSociocultural, ReescritaComparativa, ModeSocratico,
        AvaliacaoFinal
    )
    
    # Reconstruir objeto AnaliseCompleta
    analise_completa = AnaliseCompleta(
        redacao_id=analise_db.redacao_id,
        plano_usuario=analise_db.plano_usuario,
        analise_gramatical=AnaliseGramatical(**analise_db.analise_gramatical),
        analise_logica=AnaliseLogica(**analise_db.analise_logica) if analise_db.analise_logica else None,
        analise_estrutural=AnaliseEstrutural(**analise_db.analise_estrutural) if analise_db.analise_estrutural else None,
        repertorio_sociocultural=RepertorioSociocultural(**analise_db.repertorio_sociocultural) if analise_db.repertorio_sociocultural else None,
        reescritas_comparativas=[ReescritaComparativa(**r) for r in analise_db.reescritas_comparativas] if analise_db.reescritas_comparativas else None,
        modo_socratico=ModeSocratico(**analise_db.modo_socratico) if analise_db.modo_socratico else None,
        avaliacao_final=AvaliacaoFinal(**analise_db.avaliacao_final),
        # trechos_melhoria é calculado dinamicamente abaixo (para evitar migração de banco)
        fuga_ao_tema=analise_db.fuga_ao_tema.get("fuga") if analise_db.fuga_ao_tema else False,
        aderencia_tema=analise_db.aderencia_tema,
        palavras_chave_usadas=analise_db.palavras_chave_usadas,
        tempo_processamento=analise_db.tempo_processamento,
        data_analise=analise_db.data_analise,
        tokens_utilizados=analise_db.tokens_utilizados
    )

    # Calcular trechos_melhoria com base no texto original da redação + análises salvas
    if redacao:
        analise_completa.trechos_melhoria = orquestrador._gerar_trechos_melhoria(
            texto=redacao.texto,
            analise_gramatical=analise_completa.analise_gramatical,
            analise_logica=analise_completa.analise_logica
        )
    
    return analise_completa


@router.get("/analises")
async def listar_analises(
    current_user: TokenData = Depends(get_current_user),
    limite: int = 10,
    db: Session = Depends(get_db)
):
    """
    Lista análises do usuário
    """
    # Buscar redações do usuário
    redacoes = db.query(Redacao).filter(Redacao.usuario_id == current_user.usuario_id).all()
    redacao_ids = [r.id for r in redacoes]
    
    # Buscar análises dessas redações
    analises = db.query(Analise).filter(Analise.redacao_id.in_(redacao_ids)).order_by(Analise.data_analise.desc()).limit(limite).all()
    
    resultado = []
    for analise in analises:
        redacao = next((r for r in redacoes if r.id == analise.redacao_id), None)
        if redacao:
            avaliacao = analise.avaliacao_final
            resultado.append({
                "redacao_id": analise.redacao_id,
                "titulo": redacao.titulo,
                "data_analise": analise.data_analise,
                "nota_geral": avaliacao.get("nota_geral", 0) if isinstance(avaliacao, dict) else avaliacao.nota_geral,
                "plano_usado": analise.plano_usuario
            })
    
    return resultado


@router.get("/analises/estatisticas/evolucao")
async def obter_estatisticas_evolucao(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas de evolução do usuário
    
    Premium: Gráfico detalhado de evolução
    Free: Estatísticas básicas
    """
    usuario = db.query(Usuario).filter(Usuario.id == current_user.usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Buscar redações do usuário
    redacoes = db.query(Redacao).filter(Redacao.usuario_id == current_user.usuario_id).all()
    redacao_ids = [r.id for r in redacoes]
    
    # Buscar análises
    analises = db.query(Analise).filter(Analise.redacao_id.in_(redacao_ids)).all()
    
    if not analises:
        return {
            "total_analises": 0,
            "media_geral": 0,
            "mensagem": "Nenhuma análise encontrada ainda"
        }
    
    # Estatísticas básicas
    notas = []
    for analise in analises:
        avaliacao = analise.avaliacao_final
        if isinstance(avaliacao, dict):
            notas.append(avaliacao.get("nota_geral", 0))
        else:
            notas.append(avaliacao.nota_geral)
    
    media_geral = sum(notas) / len(notas) if notas else 0
    
    resultado = {
        "total_analises": len(analises),
        "media_geral": round(media_geral, 2),
        "melhor_nota": max(notas) if notas else 0,
        "pior_nota": min(notas) if notas else 0
    }
    
    # Premium: dados detalhados
    if usuario.plano in [PlanoEnum.PREMIUM, PlanoEnum.B2B]:
        # Evolução ao longo do tempo
        evolucao = []
        for analise in sorted(analises, key=lambda x: x.data_analise):
            avaliacao = analise.avaliacao_final
            nota_geral = avaliacao.get("nota_geral", 0) if isinstance(avaliacao, dict) else avaliacao.nota_geral
            nota_enem = avaliacao.get("nota_enem") if isinstance(avaliacao, dict) else (avaliacao.nota_enem if hasattr(avaliacao, 'nota_enem') else None)
            
            evolucao.append({
                "data": analise.data_analise.isoformat(),
                "nota": nota_geral,
                "nota_enem": nota_enem
            })
        
        resultado["evolucao"] = evolucao
        resultado["premium"] = True
    else:
        resultado["premium"] = False
        resultado["mensagem_upgrade"] = "Faça upgrade para Premium e veja sua evolução detalhada!"
    
    return resultado

