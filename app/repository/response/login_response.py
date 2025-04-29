from sqlmodel import SQLModel

from app.models import ResponseWrapper


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None

class LoginResponse(ResponseWrapper[Token]):
    pass
    