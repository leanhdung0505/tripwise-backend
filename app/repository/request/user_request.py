from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import EmailStr
from sqlmodel import SQLModel


class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    profile_picture: Optional[str] = None
    role: Optional[str] = "user"

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    budget_preference: Optional[int] = None

