from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any
from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.models import (
    PlacePublic, PlaceResponse, PlaceCreate, PlaceUpdate, 
    PlacePhotoPublic, PlacePhotoResponse, Message, PlacePhotoCreate,
    PaginatedResponse, PaginationMetadata
)
from app.services.places.place_service import place_service

router = APIRouter(prefix="/places", tags=["places"])

@router.get("", response_model=PaginatedResponse[PlacePublic])
def read_places(
    *,
    session: SessionDep,
    city: str = Query(None, description="Filter by city"),
    type: str = Query(None, description="Filter by place type (RESTAURANT, HOTEL, ATTRACTION)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> Dict[str, Any]:
    """
    Get places with optional filters for city and type.
    """
    result = None
    if city and type:
        result = place_service.get_places_by_city_and_type(session=session, city=city, type=type, page=page, limit=limit)
    elif city:
        result = place_service.get_places_by_city(session=session, city=city, page=page, limit=limit)
    elif type:
        result = place_service.get_places_by_type(session=session, type=type, page=page, limit=limit)
    else:
        result = place_service.get_places(session=session, page=page, limit=limit)
    
    return result

@router.get("/{place_id}", response_model=PlaceResponse)
def read_place(
    *,
    session: SessionDep,
    place_id: int
) -> PlaceResponse:
    """
    Get place by ID.
    """
    place = place_service.get_place(session=session, place_id=place_id)
    return PlaceResponse(data=place)

@router.post("", response_model=PlaceResponse)
def create_place(
    *,
    session: SessionDep,
    place_in: PlaceCreate,
    current_user: CurrentUser 
) -> PlaceResponse:
    """
    Create new place (admin only).
    """
    place = place_service.create_place(session=session, place_in=place_in)
    return PlaceResponse(data=place)

@router.put("/{place_id}", response_model=PlaceResponse)
def update_place(
    *,
    session: SessionDep,
    place_id: int,
    place_in: PlaceUpdate,
    current_user: CurrentUser 
) -> PlaceResponse:
    """
    Update place (admin only).
    """
    place = place_service.update_place(session=session, place_id=place_id, place_in=place_in)
    return PlaceResponse(data=place)

@router.delete("/{place_id}", response_model=Message)
def delete_place(
    *,
    session: SessionDep,
    place_id: int,
    current_user: CurrentUser 
) -> Message:
    """
    Delete place (admin only).
    """
    message = place_service.delete_place(session=session, place_id=place_id)
    return Message(data=message)

@router.get("/{place_id}/photos", response_model=PaginatedResponse[PlacePhotoPublic])
def read_place_photos(
    *,
    session: SessionDep,
    place_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> Dict[str, Any]:
    """
    Get photos for a place.
    """
    result = place_service.get_photos(session=session, place_id=place_id, page=page, limit=limit)
    return result

@router.post("/{place_id}/photos", response_model=PlacePhotoResponse)
def add_place_photo(
    *,
    session: SessionDep,
    place_id: int,
    photo_in: PlacePhotoCreate,
    current_user: CurrentUser 
) -> PlacePhotoResponse:
    """
    Add a photo to a place (admin only).
    """
    photo = place_service.add_photo(session=session, place_id=place_id, photo_in=photo_in)
    return PlacePhotoResponse(detail=photo)

@router.delete("/photos/{photo_id}", response_model=Message)
def delete_place_photo(
    *,
    session: SessionDep,
    photo_id: int,
    current_user: CurrentUser 
) -> Message:
    """
    Delete a place photo (admin only).
    """
    message = place_service.delete_photo(session=session, photo_id=photo_id)
    return Message(detail=message)