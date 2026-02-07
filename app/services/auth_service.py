"""
Serviço de autenticação e autorização
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.schemas.usuario import TokenData, PlanoEnum

# Security
security = HTTPBearer()


class AuthService:
    """Serviço de autenticação"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash da senha usando bcrypt diretamente
        
        Args:
            password: Senha em texto plano (máximo 72 bytes)
            
        Returns:
            Hash da senha (string)
            
        Raises:
            ValueError: Se a senha exceder 72 bytes
        """
        # Verificar tamanho em bytes (bcrypt limita a 72 bytes)
        senha_bytes = password.encode('utf-8')
        if len(senha_bytes) > 72:
            raise ValueError(
                f"Senha muito longa. O máximo é 72 bytes (aproximadamente 72 caracteres ASCII). "
                f"Sua senha tem {len(senha_bytes)} bytes. "
                f"Por favor, use uma senha mais curta."
            )
        
        try:
            # Gerar salt e hash usando bcrypt diretamente
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(senha_bytes, salt)
            # Retornar como string (bcrypt retorna bytes)
            return hashed.decode('utf-8')
        except Exception as e:
            # Re-raise com mensagem mais clara
            if "72 bytes" in str(e).lower() or "longer than 72" in str(e).lower():
                raise ValueError(
                    "Senha muito longa. O máximo permitido é 72 bytes (aproximadamente 72 caracteres ASCII). "
                    "Por favor, use uma senha mais curta."
                )
            raise ValueError(f"Erro ao gerar hash da senha: {str(e)}")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha está correta
        
        Args:
            plain_password: Senha em texto plano
            hashed_password: Hash da senha armazenado
            
        Returns:
            True se a senha estiver correta, False caso contrário
        """
        try:
            # Converter para bytes
            senha_bytes = plain_password.encode('utf-8')
            hash_bytes = hashed_password.encode('utf-8')
            
            # Verificar usando bcrypt
            return bcrypt.checkpw(senha_bytes, hash_bytes)
        except Exception as e:
            # Em caso de erro, retornar False (senha incorreta)
            return False
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Cria token JWT
        
        Args:
            data: Dados a serem codificados no token
            expires_delta: Tempo de expiração
            
        Returns:
            Token JWT
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> TokenData:
        """
        Decodifica token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            Dados do token
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            usuario_id: str = payload.get("sub")
            email: str = payload.get("email")
            plano: str = payload.get("plano")
            
            if usuario_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            return TokenData(
                usuario_id=usuario_id,
                email=email,
                plano=PlanoEnum(plano) if plano else None
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )


# Instância global
auth_service = AuthService()


# Dependency para rotas protegidas
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Dependency que valida o token e retorna o usuário atual
    """
    token = credentials.credentials
    return auth_service.decode_token(token)


async def require_premium(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency que requer plano Premium ou B2B
    """
    if current_user.plano not in [PlanoEnum.PREMIUM, PlanoEnum.B2B]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta funcionalidade requer plano Premium"
        )
    return current_user

