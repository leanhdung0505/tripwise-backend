from fastapi import APIRouter

from app.api.routes import private, utils
from app.api.routes.auth import login, register, password
from app.api.routes.email import otp_service
from app.core.config import settings

api_router = APIRouter()


# Auth routes
api_router.include_router(login.router)
api_router.include_router(register.router)
api_router.include_router(password.router)
api_router.include_router(otp_service.router)

# Other utilities
api_router.include_router(utils.router)

# Local-only routes
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
