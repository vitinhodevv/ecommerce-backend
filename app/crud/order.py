# app/crud/order.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.orm import relationship, selectinload # <--- Esta linha está correta
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate
from fastapi import HTTPException, status

async def create_order(db: AsyncSession, user_id: int, order_data: OrderCreate):
    """
    Cria um novo pedido para um usuário, processa os itens, calcula o total
    e subtrai o estoque dos produtos.
    """
    total_amount = 0
    order_items_db = []

    for item_data in order_data.items:
        # Busca o produto pelo ID
        product = await db.execute(select(Product).where(Product.id == item_data.product_id))
        product = product.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {item_data.product_id} não encontrado."
            )
        
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produto '{product.name}' não está ativo para compra."
            )

        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para o produto '{product.name}'. Disponível: {product.stock}, Solicitado: {item_data.quantity}."
            )

        # Adiciona ao total e cria o OrderItem
        item_price = product.price
        total_amount += item_price * item_data.quantity
        
        order_item = OrderItem(
            product_id=product.id,
            quantity=item_data.quantity,
            price_at_purchase=item_price
        )
        order_items_db.append(order_item)
        
        # Diminui o estoque do produto
        product.stock -= item_data.quantity
        db.add(product) # Marca o produto para atualização no commit

    # Cria o objeto Order principal
    db_order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status="pending",
        items=order_items_db # Adiciona os itens criados ao pedido
    )

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order) # Atualiza o objeto com os IDs gerados pelo DB
    # Recarrega os itens para garantir que o relacionamento está populado após refresh do order
    await db.refresh(db_order, attribute_names=["items"])
    for item in db_order.items:
        await db.refresh(item, attribute_names=["product"]) # Opcional, para carregar o objeto Product se precisar

    return db_order

async def get_order(db: AsyncSession, order_id: int):
    """Retorna um pedido específico pelo ID, com seus itens."""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            # Carrega os itens do pedido e, para cada item, carrega o produto associado
            selectinload(Order.items).selectinload(OrderItem.product) # <--- CORRIGIDO
        )
    )
    return result.scalar_one_or_none()

async def get_user_orders(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    """Retorna todos os pedidos de um usuário específico."""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product) # <--- CORRIGIDO
        )
        .order_by(Order.order_date.desc()) # Ordena por data mais recente
    )
    return result.scalars().all()

async def get_all_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Retorna todos os pedidos (para admin), com paginação."""
    result = await db.execute(
        select(Order)
        .offset(skip)
        .limit(limit)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product), # <--- CORRIGIDO
            selectinload(Order.user) # Opcional: carregar dados do usuário também <--- CORRIGIDO
        )
        .order_by(Order.order_date.desc())
    )
    return result.scalars().all()

async def update_order_status(db: AsyncSession, order_id: int, order_update: OrderUpdate):
    """Atualiza o status de um pedido."""
    db_order = await get_order(db, order_id)
    if not db_order:
        return None
    
    update_data = order_update.model_dump(exclude_unset=True)
    if "status" in update_data:
        db_order.status = update_data["status"]
    
    await db.commit()
    await db.refresh(db_order)
    # Recarrega os itens e produtos para a resposta completa
    await db.refresh(db_order, attribute_names=["items"])
    for item in db_order.items:
        await db.refresh(item, attribute_names=["product"])
    return db_order

# A função de delete de pedido pode ser adicionada aqui, se desejado.
# Geralmente, pedidos não são deletados, mas sim cancelados.
# async def delete_order(db: AsyncSession, order_id: int):
#     stmt = delete(Order).where(Order.id == order_id)
#     result = await db.execute(stmt)
#     await db.commit()
#     return result.rowcount > 0