from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Para funções como now()
from app.database import Base

# Modelo para o Pedido (Order)
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_date = Column(DateTime, default=func.now(), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending", nullable=False) # Ex: pending, processing, shipped, delivered, cancelled

    # Relacionamentos
    # Cada pedido pertence a um usuário
    user = relationship("User", back_populates="orders")
    # Cada pedido pode ter múltiplos itens (produtos)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

# Modelo para o Item de Pedido (OrderItem) - os produtos dentro de um pedido
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False) # Preço do produto no momento da compra

    # Relacionamentos
    # Cada item pertence a um pedido
    order = relationship("Order", back_populates="items")
    # Cada item se refere a um produto
    product = relationship("Product") # Não usamos back_populates aqui, pois um produto pode estar em muitos order_items