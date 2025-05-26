from fastapi import APIRouter

from app.api.routes import private, utils
from app.api.routes.auth import login, register, password,login_google
from app.api.routes.email import otp_service
from app.core.config import settings
from app.api.routes.users import admin, users
from app.api.routes.places import places,attractions,hotels,restaurants
from app.api.routes.itineraries import itinerary,ai_itinerary
api_router = APIRouter()


# Auth routes
api_router.include_router(login.router)
api_router.include_router(register.router)
api_router.include_router(password.router)
api_router.include_router(otp_service.router)
api_router.include_router(login_google.router)

#User route
api_router.include_router(admin.router)
api_router.include_router(users.router)

#Place route
api_router.include_router(places.router)

#Attraction route 
api_router.include_router(attractions.router)

#Hotel route
api_router.include_router(hotels.router)

#Restaurant route
api_router.include_router(restaurants.router)

#Itinerary route
api_router.include_router(itinerary.router)
api_router.include_router(ai_itinerary.router)

# Other utilities
api_router.include_router(utils.router)

# Local-only routes
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
