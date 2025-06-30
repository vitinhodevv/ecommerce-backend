# app/schemas/product.py

from pydantic import BaseModel, Field

# Schema para criação de produto (dados que o cliente envia ao criar)
class ProductCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100) # Nome do produto
    description: str | None = None # Pode ser opcional (None)
    price: float = Field(gt=0) # Preço, deve ser maior que zero
    stock: int = Field(ge=0) # Estoque, deve ser maior ou igual a zero
    is_active: bool = True # Ativo por padrão

# Schema para atualização de produto (todos os campos são opcionais, para atualização parcial)
class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    is_active: bool | None = None

# Schema para visualização de produto (dados que a API retorna)
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    is_active: bool

    class Config:
        from_attributes = True # ou orm_mode = True em Pydantic < 2.0