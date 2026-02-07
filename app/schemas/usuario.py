"""
Schemas para usuários
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from enum import Enum
from datetime import datetime


class PlanoEnum(str, Enum):
    """Tipos de plano disponíveis"""
    FREE = "free"
    PREMIUM = "premium"
    B2B = "b2b"


class UsuarioBase(BaseModel):
    """Schema base de usuário"""
    email: EmailStr
    nome: str = Field(..., min_length=3, max_length=100)
    plano: PlanoEnum = PlanoEnum.FREE


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário"""
    senha: str = Field(..., min_length=6, max_length=72)
    
    @field_validator('senha')
    @classmethod
    def validar_tamanho_senha(cls, v: str) -> str:
        """Valida que a senha não exceda 72 bytes (limite do bcrypt)"""
        senha_bytes = v.encode('utf-8')
        if len(senha_bytes) > 72:
            raise ValueError(
                f"Senha muito longa. O máximo é 72 bytes (aproximadamente 72 caracteres ASCII). "
                f"Sua senha tem {len(senha_bytes)} bytes."
            )
        return v


class UsuarioLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    senha: str = Field(..., min_length=1, max_length=72)
    
    @field_validator('senha')
    @classmethod
    def validar_tamanho_senha(cls, v: str) -> str:
        """Valida que a senha não exceda 72 bytes (limite do bcrypt)"""
        senha_bytes = v.encode('utf-8')
        if len(senha_bytes) > 72:
            raise ValueError(
                f"Senha muito longa. O máximo é 72 bytes (aproximadamente 72 caracteres ASCII). "
                f"Sua senha tem {len(senha_bytes)} bytes."
            )
        return v


class UsuarioResponse(UsuarioBase):
    """Schema de resposta de usuário"""
    id: str
    data_criacao: datetime
    correcoes_realizadas_hoje: int = 0
    limite_diario: int
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class TokenData(BaseModel):
    """Dados do token"""
    usuario_id: Optional[str] = None
    email: Optional[str] = None
    plano: Optional[PlanoEnum] = None

