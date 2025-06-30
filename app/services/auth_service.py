# app/services/auth_service.py

from fastapi import HTTPException # Esta importação estava faltando no seu código anterior também!
from datetime import datetime, timedelta, timezone
from typing import Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext # Para hash de senhas <--- NOVO

from app.config import settings
from app.schemas.token import TokenData

# As credenciais e o algoritmo são carregados das configurações
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Inicializa o contexto para hashing de senhas <--- NOVO
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções Auxiliares de Senha --- <--- NOVAS FUNÇÕES
def get_password_hash(password: str) -> str:
    """Hashea a senha fornecida."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha simples corresponde à senha hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    Cria um JSON Web Token (JWT) de acesso.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire}) # Adiciona o tempo de expiração ao payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """
    Verifica a validade de um JWT e retorna seus dados.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") # 'sub' é uma claim padrão para o "subject" (neste caso, o email)
        if email is None:
            raise credentials_exception # Token não tem o email esperado
        token_data = TokenData(email=email)
    except JWTError: # Se o token for inválido, expirado, etc.
        raise credentials_exception
    return token_data