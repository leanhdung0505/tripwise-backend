# app/services/otp_token_service.py
import random
from datetime import datetime, timedelta, timezone
import jwt  # pyjwt
from fastapi import HTTPException

from app.core.config import settings

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices("0123456789", k=length))

def create_otp_token(email: str, otp_code: str, expire_minutes: int = 5) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {
        "email": email,
        "otp_code": otp_code,
        "exp": expire
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)   

def verify_otp_token(token: str, otp_code: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload["otp_code"] != otp_code:
            raise HTTPException(status_code=400, detail="Invalid OTP code")
        return payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="OTP has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")
