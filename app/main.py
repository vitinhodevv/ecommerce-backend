# app/main.py

from fastapi import FastAPI
from app.database import engine, Base
import asyncio
from app.models import user
from app.models import product
from app.models import order

from app.routers import users
from app.routers import auth
from app.routers import products
from app.routers import orders # <--- ADICIONE ESTA LINHA para o roteador de pedidos

# Cria uma instância da aplicação FastAPI
app = FastAPI(
    title="E-commerce API",
    description="API para gerenciar produtos, usuários e pedidos de um e-commerce.",
    version="0.1.0",
)

# Inclui os roteadores na aplicação principal
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router) # <--- ADICIONE ESTA LINHA

# Evento de startup para criar as tabelas no banco de dados
@app.on_event("startup")
async def startup_event():
    print("Iniciando a criação das tabelas no banco de dados...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tabelas criadas ou já existentes.")

@app.get("/")
def read_root():
    """
    Endpoint de teste para verificar se a API está funcionando.
    Retorna uma mensagem de boas-vindas.
    """
    return {"message": "Bem-vindo à E-commerce API!"}