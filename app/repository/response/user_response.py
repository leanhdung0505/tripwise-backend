from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import EmailStr
from sqlmodel import SQLModel
from app.models import ResponseWrapper

class User(SQLModel):
    user_id: Optional[uuid.UUID] = None  
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None 
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    profile_picture: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    budget_preference: Optional[int] = None
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None


class UserUpdateMe(SQLModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    profile_picture: str | None = None
    preferences: Dict[str, Any] | None = None
    budget_preference: int | None = None
    updated_at: Optional[datetime] = None



class UserResponse(ResponseWrapper[User]):
    pass