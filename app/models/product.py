# app/models/product.py

from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.database import Base # Importa a base declarativa do SQLAlchemy

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True) # Text para descrições mais longas
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0) # Quantidade em estoque
    is_active = Column(Boolean, default=True) # Se o produto está ativo/visível