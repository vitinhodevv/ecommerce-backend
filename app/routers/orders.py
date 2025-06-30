# app/routers/orders.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.crud import order as crud_order # Importa as funções CRUD de pedido
from app.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User # Para tipagem do current_user

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_new_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Qualquer usuário ativo pode criar um pedido
):
    """
    Cria um novo pedido para o usuário logado.
    Requer autenticação de um usuário ativo.
    """
    db_order = await crud_order.create_order(db=db, user_id=current_user.id, order_data=order)
    return db_order

@router.get("/me/", response_model=List[OrderResponse])
async def read_my_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Requer autenticação de um usuário ativo
):
    """
    Lista todos os pedidos do usuário logado.
    Requer autenticação de um usuário ativo.
    """
    orders = await crud_order.get_user_orders(db, user_id=current_user.id, skip=skip, limit=limit)
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def read_single_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Requer autenticação de um usuário ativo
):
    """
    Retorna um pedido específico pelo ID.
    Um usuário só pode ver seus próprios pedidos, a menos que seja admin.
    """
    order = await crud_order.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado."
        )
    # Garante que o usuário só possa ver seus próprios pedidos ou se for admin
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a visualizar este pedido."
        )
    return order

@router.get("/", response_model=List[OrderResponse])
async def read_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) # Somente admin pode ver todos os pedidos
):
    """
    Lista todos os pedidos no sistema (apenas para administradores).
    Requer privilégios de administrador.
    """
    orders = await crud_order.get_all_orders(db, skip=skip, limit=limit)
    return orders

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) # Somente admin pode atualizar o status do pedido
):
    """
    Atualiza o status de um pedido. Requer privilégios de administrador.
    """
    updated_order = await crud_order.update_order_status(db, order_id, order_update)
    if not updated_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado.")
    return updated_order