"""
Modelo de Redação
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class TipoRedacaoEnum(str, enum.Enum):
    """Tipos de redação"""
    ENEM = "enem"
    DISSERTATIVA = "dissertativa"
    ARGUMENTATIVA = "argumentativa"
    CONCURSO = "concurso"


class StatusRedacaoEnum(str, enum.Enum):
    """Status da redação"""
    PENDENTE = "pendente"
    ANALISANDO = "analisando"
    CONCLUIDA = "concluida"
    ERRO = "erro"


class Redacao(Base):
    """Modelo de Redação"""
    __tablename__ = "redacoes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    # Dados da redação
    titulo = Column(String, nullable=False)
    texto = Column(Text, nullable=False)
    tema = Column(String, nullable=False)
    tipo = Column(SQLEnum(TipoRedacaoEnum), default=TipoRedacaoEnum.DISSERTATIVA)
    
    # Status
    status = Column(SQLEnum(StatusRedacaoEnum), default=StatusRedacaoEnum.PENDENTE)
    
    # Timestamps
    data_submissao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="redacoes")
    analise = relationship("Analise", back_populates="redacao", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Redacao(titulo={self.titulo}, status={self.status})>"

