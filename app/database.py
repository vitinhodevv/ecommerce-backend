from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings # Importa as configurações que acabamos de criar

# A URL de conexão é carregada das configurações
DATABASE_URL = settings.DATABASE_URL

# Cria o engine assíncrono do SQLAlchemy
# O 'echo=True' é útil para depuração, mostrando as queries SQL no console
engine = create_async_engine(DATABASE_URL, echo=True)

# Cria um construtor de sessões assíncronas.
# expire_on_commit=False: Evita que objetos fiquem "desanexados" após o commit.
# Isso é importante para uso em assíncrono.
async_session_maker = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para nossos modelos declarativos do SQLAlchemy
Base = declarative_base()

# Função assíncrona para obter uma sessão de banco de dados.
# Esta função será usada como uma dependência no FastAPI.
async def get_db():
    async with async_session_maker() as session:
        yield session