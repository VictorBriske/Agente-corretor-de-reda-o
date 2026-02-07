"""
Worker para processar redações pendentes automaticamente
"""

import asyncio
import logging
import traceback
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.redacao import Redacao, StatusRedacaoEnum
from app.models.analise import Analise
from app.models.usuario import Usuario
from app.schemas.redacao import RedacaoSubmit
from app.agents.orquestrador import orquestrador

logger = logging.getLogger(__name__)


class RedacaoWorker:
    """Worker que processa redações pendentes em background"""
    
    def __init__(self):
        """Inicializa o worker"""
        self.running = False
        self.task = None
        self.check_interval = 5  # Verificar a cada 5 segundos
    
    async def processar_redacao_pendente(self, redacao: Redacao, db: Session):
        """
        Processa uma redação pendente
        
        Args:
            redacao: Objeto Redacao a ser processado
            db: Sessão do banco de dados
        """
        try:
            logger.info(f"[WORKER] Processando redacao {redacao.id} do usuario {redacao.usuario_id}")
            print(f"[WORKER] Processando redacao {redacao.id} do usuario {redacao.usuario_id}")
            
            # Buscar usuário
            usuario = db.query(Usuario).filter(Usuario.id == redacao.usuario_id).first()
            
            if not usuario:
                logger.error(f"[WORKER] Usuario {redacao.usuario_id} nao encontrado")
                redacao.status = StatusRedacaoEnum.ERRO
                db.commit()
                return
            
            # Verificar limite diário
            if usuario.correcoes_realizadas_hoje >= usuario.limite_diario:
                logger.warning(f"[WORKER] Limite diario atingido para usuario {usuario.id}")
                print(f"[WORKER] Limite diario atingido para usuario {usuario.id}")
                # Manter como pendente para processar depois
                return
            
            # Atualizar status para analisando
            redacao.status = StatusRedacaoEnum.ANALISANDO
            db.commit()
            db.refresh(redacao)
            
            # Criar objeto RedacaoSubmit para o orquestrador
            redacao_submit = RedacaoSubmit(
                titulo=redacao.titulo,
                texto=redacao.texto,
                tema=redacao.tema,
                tipo=redacao.tipo
            )
            
            # Executar análise
            logger.info(f"[WORKER] Executando analise da redacao {redacao.id} ({usuario.plano.value})...")
            print(f"[WORKER] Executando analise da redacao {redacao.id} ({usuario.plano.value})...")
            
            analise_completa = await orquestrador.analisar_redacao(
                redacao=redacao_submit,
                plano_usuario=usuario.plano,
                redacao_id=redacao.id
            )
            
            # Salvar análise no banco
            logger.info(f"[WORKER] Salvando analise no banco...")
            print(f"[WORKER] Salvando analise no banco...")
            
            nova_analise = Analise(
                id=redacao.id,
                redacao_id=redacao.id,
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
            redacao.status = StatusRedacaoEnum.CONCLUIDA
            
            # Incrementar contador de análises
            usuario.correcoes_realizadas_hoje += 1
            
            db.commit()
            
            logger.info(f"[WORKER] Analise da redacao {redacao.id} concluida!")
            print(f"[WORKER] Analise da redacao {redacao.id} concluida!")
            
        except Exception as e:
            # Atualizar status da redação para erro
            redacao.status = StatusRedacaoEnum.ERRO
            db.commit()
            
            logger.error(f"[WORKER] Erro ao processar redacao {redacao.id}: {str(e)}")
            logger.error(f"[WORKER] Traceback: {traceback.format_exc()}")
            print(f"[WORKER] Erro ao processar redacao {redacao.id}: {str(e)}")
            traceback.print_exc()
    
    async def processar_pendentes(self):
        """Processa todas as redações pendentes"""
        db = SessionLocal()
        try:
            # Buscar redações pendentes (ordenadas por data de submissão)
            redacoes_pendentes = db.query(Redacao).filter(
                Redacao.status == StatusRedacaoEnum.PENDENTE
            ).order_by(Redacao.data_submissao.asc()).limit(1).all()  # Processar uma por vez
            
            if redacoes_pendentes:
                for redacao in redacoes_pendentes:
                    await self.processar_redacao_pendente(redacao, db)
                    # Pequena pausa entre processamentos
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"[WORKER] Erro ao processar pendentes: {str(e)}")
            logger.error(f"[WORKER] Traceback: {traceback.format_exc()}")
            print(f"[WORKER] Erro ao processar pendentes: {str(e)}")
            traceback.print_exc()
        finally:
            db.close()
    
    async def run(self):
        """Loop principal do worker"""
        self.running = True
        logger.info("[WORKER] Worker iniciado")
        print("[WORKER] Worker de processamento de redações iniciado")
        
        while self.running:
            try:
                await self.processar_pendentes()
            except Exception as e:
                logger.error(f"[WORKER] Erro no loop do worker: {str(e)}")
                print(f"[WORKER] Erro no loop do worker: {str(e)}")
            
            # Aguardar antes da próxima verificação
            await asyncio.sleep(self.check_interval)
    
    def start(self):
        """Inicia o worker em background"""
        if not self.running:
            self.task = asyncio.create_task(self.run())
            logger.info("[WORKER] Worker iniciado em background")
            print("[WORKER] Worker iniciado em background")
    
    def stop(self):
        """Para o worker"""
        self.running = False
        if self.task:
            self.task.cancel()
        logger.info("[WORKER] Worker parado")
        print("[WORKER] Worker parado")


# Instância global do worker
worker = RedacaoWorker()

