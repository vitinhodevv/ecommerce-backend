from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext # Para hash de senhas

# Inicializa o contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções Auxiliares de Senha ---
def get_password_hash(password: str) -> str:
    """Hashea a senha fornecida."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha simples corresponde à senha hash."""
    return pwd_context.verify(plain_password, hashed_password)

# --- Funções CRUD para Usuários ---

async def get_user(db: AsyncSession, user_id: int):
    """
    Retorna um usuário pelo ID.
    """
    # select(User).where(User.id == user_id) cria uma query SQL como: SELECT * FROM users WHERE id = :user_id
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none() # Retorna o primeiro resultado ou None

async def get_user_by_email(db: AsyncSession, email: str):
    """
    Retorna um usuário pelo email.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none() # Retorna o primeiro resultado ou None

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Retorna uma lista de usuários com paginação.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all() # Retorna todos os resultados da query

async def create_user(db: AsyncSession, user: UserCreate):
    """
    Cria um novo usuário no banco de dados.
    """
    hashed_password = get_password_hash(user.password) # Hasheia a senha antes de salvar
    db_user = User(email=user.email, hashed_password=hashed_password) # Cria uma instância do modelo DB
    db.add(db_user) # Adiciona o objeto ao sessão do DB
    await db.commit() # Salva as mudanças no DB
    await db.refresh(db_user) # Atualiza o objeto com os dados do DB (ex: ID gerado)
    return db_user

async def update_user(db: AsyncSession, user_id: int, user_update_data: dict):
    """
    Atualiza um usuário existente.
    user_update_data é um dicionário com os campos a serem atualizados.
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    for key, value in user_update_data.items():
        if key == "password": # Se a senha for atualizada, hasheie
            setattr(db_user, "hashed_password", get_password_hash(value))
        else:
            setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    """
    Deleta um usuário pelo ID.
    """
    # Construir a declaração DELETE
    stmt = delete(User).where(User.id == user_id)
    # Executar a declaração
    result = await db.execute(stmt)
    # Commit para persistir a mudança
    await db.commit()
    # Retorna o número de linhas afetadas (0 ou 1)
    return result.rowcount > 0