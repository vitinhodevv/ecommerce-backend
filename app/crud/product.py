# app/crud/product.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

async def get_product(db: AsyncSession, product_id: int):
    """Retorna um produto pelo ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()

async def get_product_by_name(db: AsyncSession, name: str):
    """Retorna um produto pelo nome."""
    result = await db.execute(select(Product).where(Product.name == name))
    return result.scalar_one_or_none()

async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Retorna uma lista de produtos com paginação."""
    result = await db.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()

async def create_product(db: AsyncSession, product: ProductCreate):
    """Cria um novo produto."""
    db_product = Product(**product.model_dump()) # Cria uma instância do modelo DB a partir do schema
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate):
    """Atualiza um produto existente."""
    db_product = await get_product(db, product_id)
    if not db_product:
        return None
    
    # Atualiza apenas os campos fornecidos no product_data
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def delete_product(db: AsyncSession, product_id: int):
    """Deleta um produto pelo ID."""
    stmt = delete(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0 # Retorna True se deletou, False caso contrário