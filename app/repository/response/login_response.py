from sqlmodel import SQLModel

from app.models import ResponseWrapper


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str | None = None
    exp: int | None = None
    type: str | None = None 

class LoginResponse(ResponseWrapper[Token]):
    pass
    