from fastapi import APIRouter, Depends, Query
from typing import List
from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.models import (
    HotelDetailResponse, HotelDetailCreate, HotelDetailUpdate, Message
)
from app.services.places.hotel_service import hotel_service

router = APIRouter(prefix="/hotels", tags=["hotels"])

@router.get("", response_model=List[HotelDetailResponse])
def read_hotel_details(
    *,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100
) -> List[HotelDetailResponse]:
    """
    Get all hotel details with optional star rating filter.
    """
    return hotel_service.get_hotel_details(session=session, skip=skip, limit=limit)

@router.get("/{place_id}", response_model=HotelDetailResponse)
def read_hotel_detail(
    *,
    session: SessionDep,
    place_id: int
) -> HotelDetailResponse:
    """
    Get hotel details for a specific place.
    """
    return hotel_service.get_hotel_detail_by_place(session=session, place_id=place_id)

@router.post("/{place_id}", response_model=HotelDetailResponse)
def create_hotel_detail(
    *,
    session: SessionDep,
    place_id: int,
    hotel_detail_in: HotelDetailCreate,
    current_user: CurrentUser 
) -> HotelDetailResponse:
    """
    Create hotel details for a place (admin only).
    """
    return hotel_service.create_hotel_detail(
        session=session, 
        place_id=place_id, 
        hotel_detail_in=hotel_detail_in
    )

@router.put("/{place_id}", response_model=HotelDetailResponse)
def update_hotel_detail(
    *,
    session: SessionDep,
    place_id: int,
    hotel_detail_in: HotelDetailUpdate,
    current_user: CurrentUser 
) -> HotelDetailResponse:
    """
    Update hotel details for a place (admin only).
    """
    return hotel_service.update_hotel_detail(
        session=session, 
        place_id=place_id, 
        hotel_detail_in=hotel_detail_in
    )

@router.delete("/{place_id}", response_model=Message)
def delete_hotel_detail(
    *,
    session: SessionDep,
    place_id: int,
    current_user: CurrentUser 
) -> Message:
    """
    Delete hotel details for a place (admin only).
    """
    return hotel_service.delete_hotel_detail(session=session, place_id=place_id)