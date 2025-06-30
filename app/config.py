from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Configurações do banco de dados
    DATABASE_URL: str

    # Configurações de segurança para JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignora variáveis de ambiente que não estão definidas aqui
    )

# Cria uma instância das configurações para ser importada em outros lugares
settings = Settings()