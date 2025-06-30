from pydantic import BaseModel

# Schema para o token de acesso retornado após o login
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" # Tipo do token, geralmente "bearer"

# Schema para os dados do token decodificado (payload)
class TokenData(BaseModel):
    email: str | None = None # O email do usuário dentro do token