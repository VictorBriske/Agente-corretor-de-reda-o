"""
Modelo de Análise
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Analise(Base):
    """Modelo de Análise de Redação"""
    __tablename__ = "analises"
    
    id = Column(String, primary_key=True)  # Mesmo ID da redação
    redacao_id = Column(String, ForeignKey("redacoes.id", ondelete="CASCADE"), nullable=False)
    
    # Metadados
    plano_usuario = Column(String, nullable=False)
    tempo_processamento = Column(Float)
    tokens_utilizados = Column(Integer)
    
    # Resultados (armazenados como JSON)
    analise_gramatical = Column(JSON, nullable=False)
    analise_logica = Column(JSON)
    analise_estrutural = Column(JSON)
    repertorio_sociocultural = Column(JSON)
    reescritas_comparativas = Column(JSON)
    modo_socratico = Column(JSON)
    avaliacao_final = Column(JSON, nullable=False)
    
    # Detecção de fuga ao tema
    fuga_ao_tema = Column(JSON)
    aderencia_tema = Column(Float)
    palavras_chave_usadas = Column(JSON)

    
    # Timestamps
    data_analise = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    redacao = relationship("Redacao", back_populates="analise")
    
    def __repr__(self):
        return f"<Analise(redacao_id={self.redacao_id}, plano={self.plano_usuario})>"

