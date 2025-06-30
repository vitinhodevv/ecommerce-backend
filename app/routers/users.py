# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud import user as crud_user
from app.models.user import User # Importe o modelo User para tipagem na dependência
from app.dependencies import get_current_active_user, get_current_admin_user # Importe as dependências de autenticação

# Cria um roteador para agrupar endpoints relacionados a usuários
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria um novo usuário.
    Esta rota não é protegida para permitir o registro de novos usuários.
    """
    db_user = await crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado."
        )
    return await crud_user.create_user(db=db, user=user)

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Requer usuário autenticado e ativo
):
    """
    Lista todos os usuários com paginação. Requer autenticação de um usuário ativo.
    """
    users = await crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Requer usuário autenticado e ativo
):
    """
    Retorna um usuário específico pelo ID. Requer autenticação de um usuário ativo.
    """
    db_user = await crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_existing_user(
    user_id: int,
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) # Requer usuário autenticado e ADMIN
):
    """
    Atualiza um usuário existente pelo ID. Requer privilégios de administrador.
    """
    user_data = user.model_dump(exclude_unset=True) # Pydantic v2
    
    updated_user = await crud_user.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) # Requer usuário autenticado e ADMIN
):
    """
    Deleta um usuário existente pelo ID. Requer privilégios de administrador.
    """
    deleted = await crud_user.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    # Um status 204 No Content não deve ter corpo, mas para testes, pode ser útil:
    # return {"message": "Usuário deletado com sucesso."}
    return