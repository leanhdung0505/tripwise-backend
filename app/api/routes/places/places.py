from fastapi import APIRouter, Depends, Query
from typing import List
from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.models import (
    PlaceResponse, PlaceCreate, PlaceUpdate, 
    PlacePhotoCreate, PlacePhotoResponse, Message
)
from app.services.places.place_service import place_service

router = APIRouter(prefix="/places", tags=["places"])

@router.get("", response_model=List[PlaceResponse])
def read_places(
    *,
    session: SessionDep,
    city: str = Query(None, description="Filter by city"),
    type: str = Query(None, description="Filter by place type (RESTAURANT, HOTEL, ATTRACTION)"),
    skip: int = 0,
    limit: int = 100
) -> List[PlaceResponse]:
    """
    Get places with optional filters for city and type.
    """
    if city and type:
        return place_service.get_places_by_city_and_type(session=session, city=city, type=type, skip=skip, limit=limit)
    elif city:
        return place_service.get_places_by_city(session=session, city=city, skip=skip, limit=limit)
    elif type:
        return place_service.get_places_by_type(session=session, type=type, skip=skip, limit=limit)
    return place_service.get_places(session=session, skip=skip, limit=limit)

@router.get("/{place_id}", response_model=PlaceResponse)
def read_place(
    *,
    session: SessionDep,
    place_id: int
) -> PlaceResponse:
    """
    Get place by ID.
    """
    return place_service.get_place(session=session, place_id=place_id)

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
    return place_service.create_place(session=session, place_in=place_in)

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
    return place_service.update_place(session=session, place_id=place_id, place_in=place_in)

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
    return place_service.delete_place(session=session, place_id=place_id)

@router.get("/{place_id}/photos", response_model=List[PlacePhotoResponse])
def read_place_photos(
    *,
    session: SessionDep,
    place_id: int
) -> List[PlacePhotoResponse]:
    """
    Get photos for a place.
    """
    return place_service.get_photos(session=session, place_id=place_id)

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
    return place_service.add_photo(session=session, place_id=place_id, photo_in=photo_in)

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
    return place_service.delete_photo(session=session, photo_id=photo_id)