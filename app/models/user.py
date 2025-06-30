from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base # Importa a Base que definimos em database.py

class User(Base):
    __tablename__ = "users" # Define o nome da tabela no banco de dados

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True) # Para ativar/desativar usuários
    is_admin = Column(Boolean, default=False) # Para controle de permissões (opcional)

    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"