# app/schemas/order.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# --- Schemas para OrderItem (Item do Pedido) ---

# Schema para o cliente enviar ao adicionar um item ao pedido (apenas product_id e quantity)
class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0, description="ID do produto.")
    quantity: int = Field(gt=0, description="Quantidade do produto no pedido. Deve ser maior que 0.")

# Schema para a API retornar um Item do Pedido
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float # Preço que o produto foi comprado

    class Config:
        from_attributes = True # ou orm_mode = True para Pydantic < 2.0

# --- Schemas para Order (Pedido) ---

# Schema para o cliente criar um Pedido (envia apenas os itens)
class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Lista de itens no pedido.")

# Schema para atualização de Pedido (principalmente para admin mudar o status)
class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Novo status do pedido.")
    # Total amount e order_date não são geralmente atualizáveis via API por cliente/admin
    # Mas você pode adicionar outros campos se necessário, como endereço de entrega.

# Schema para a API retornar um Pedido completo
class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_date: datetime
    total_amount: float
    status: str
    items: List[OrderItemResponse] # Inclui os detalhes dos itens do pedido

    class Config:
        from_attributes = True # ou orm_mode = True para Pydantic < 2.0