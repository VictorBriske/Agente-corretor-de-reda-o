"""
Modelo de Usuário
"""

from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class PlanoEnum(str, enum.Enum):
    """Tipos de plano"""
    FREE = "free"
    PREMIUM = "premium"
    B2B = "b2b"


class Usuario(Base):
    """Modelo de Usuário"""
    __tablename__ = "usuarios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    senha_hash = Column(String, nullable=False)
    plano = Column(SQLEnum(PlanoEnum), default=PlanoEnum.FREE, nullable=False)
    
    # Controle de uso
    correcoes_realizadas_hoje = Column(Integer, default=0)
    limite_diario = Column(Integer, default=5)
    
    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    redacoes = relationship("Redacao", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Usuario(email={self.email}, plano={self.plano})>"

