# app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import auth_service # Para verificar o token JWT
from app.crud import user as crud_user # Para buscar o usuário pelo email do token
from app.database import get_db
from app.models.user import User

# Instancia o OAuth2PasswordBearer para lidar com tokens Bearer no cabeçalho Authorization
# O tokenUrl é o endpoint onde o cliente obterá o token (ex: /token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependência que retorna o usuário atualmente autenticado.
    Se o token for inválido ou o usuário não for encontrado, levanta uma HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verifica e decodifica o token para obter os dados (email)
    token_data = auth_service.verify_access_token(token, credentials_exception)
    
    # Busca o usuário no banco de dados usando o email do token
    user = await crud_user.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception # Usuário não encontrado, mesmo com token válido
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependência que retorna o usuário atualmente autenticado e ativo.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo.")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependência que retorna o usuário atualmente autenticado, ativo e com permissão de admin.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada. Requer privilégios de administrador.")
    return current_user