from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str
    fcm_token: Optional[str] = None
    device: Optional[str] = None
