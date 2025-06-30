# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Para o formulário de login
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.token import Token # Schema para o token de resposta
from app.schemas.user import UserResponse # <--- ADICIONE ESTA LINHA!
from app.crud import user as crud_user
from app.services import auth_service # Para criar tokens e verificar senhas
from app.dependencies import get_current_user # <--- ADICIONE ESTA LINHA!

router = APIRouter(
    tags=["Authentication"], # Agrupa na documentação
    responses={404: {"description": "Not found"}},
)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), # Pega username (email) e password do formulário
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para login de usuário. Retorna um token de acesso JWT.
    """
    user = await crud_user.get_user_by_email(db, email=form_data.username) # O username aqui é o email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciais incorretas."
        )
    
    # Verifica a senha hasheada
    if not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciais incorretas."
        )
    
    # Se a senha estiver correta, cria o token
    access_token = auth_service.create_access_token(
        data={"sub": user.email} # O "sub" (subject) do token será o email do usuário
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Exemplo de rota protegida que retorna o usuário autenticado
@router.get("/users/me/", response_model=UserResponse) # <--- Mude para UserResponse aqui
async def read_users_me(current_user: crud_user.User = Depends(get_current_user)): # <--- Mude de auth_service.get_current_user para get_current_user
    """
    Retorna os dados do usuário logado. Requer autenticação.
    """
    # UserResponse é o schema seguro para retornar informações do usuário
    return current_user