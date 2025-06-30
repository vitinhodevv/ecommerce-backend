# app/schemas/user.py

from pydantic import BaseModel, EmailStr # EmailStr para validação de formato de email

# Schema para criação de usuário (dados que o cliente envia ao criar)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema para visualização de usuário (dados que a API retorna)
# password não deve ser incluído aqui por segurança
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        # Isso permite que o Pydantic leia dados de um objeto ORM (como um objeto User do SQLAlchemy)
        # em vez de apenas de um dicionário. Essencial para mapear do DB para a resposta.
        from_attributes = True # ou orm_mode = True em Pydantic < 2.0