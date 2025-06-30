# app/routers/products.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.crud import product as crud_product # Importa as funções CRUD de produto
from app.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User # Para tipagem do current_user

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) # Somente admin pode criar produtos
):
    """
    Cria um novo produto. Requer privilégios de administrador.
    """
    db_product = await crud_product.get_product_by_name(db, name=product.name)
    if db_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto com este nome já existe."
        )
    return await crud_product.create_product(db=db, product=product)

@router.get("/", response_model=List[ProductResponse])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
    # Produtos podem ser listados por qualquer um (não requer autenticação)
):
    """
    Lista todos os produtos com paginação.
    """
    products = await crud_product.get_products(db, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
    # Produtos podem ser vistos por qualquer um (não requer autenticação)
):
    """
    Retorna um produto específico pelo ID.
    """
    db_product = await crud_product.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product_id: int,
    product: ProductUpdate, # Use ProductUpdate para atualização
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) # Somente admin pode atualizar produtos
):
    """
    Atualiza um produto existente pelo ID. Requer privilégios de administrador.
    """
    updated_product = await crud_product.update_product(db, product_id, product)
    if not updated_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")
    return updated_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) # Somente admin pode deletar produtos
):
    """
    Deleta um produto existente pelo ID. Requer privilégios de administrador.
    """
    deleted = await crud_product.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")
    return