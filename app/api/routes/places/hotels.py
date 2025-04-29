from fastapi import APIRouter, Depends, Query
from typing import List
from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.models import (
    HotelDetailPublic, HotelDetailResponse, HotelDetailCreate, HotelDetailUpdate, Message, PaginatedResponse
)
from app.services.places.hotel_service import hotel_service

router = APIRouter(prefix="/hotels", tags=["hotels"])

@router.get("", response_model=PaginatedResponse[HotelDetailPublic])
def read_hotel_details(
    *,
    session: SessionDep,
    page: int = 1,
    limit: int = 10
) -> PaginatedResponse[HotelDetailPublic]:
    """
    Get all hotel details with optional star rating filter.
    """
    hotel_details, pagination = hotel_service.get_hotel_details(
        session=session, 
        page=page, 
        limit=limit
    )
    return PaginatedResponse(
        data=hotel_details,
        pagination=pagination
    )

@router.get("/{place_id}", response_model=HotelDetailResponse)
def read_hotel_detail(
    *,
    session: SessionDep,
    place_id: int
) -> HotelDetailResponse:
    """
    Get hotel details for a specific place.
    """
    return HotelDetailResponse(
        data=hotel_service.get_hotel_detail_by_place(session=session, place_id=place_id)
    )

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
    return HotelDetailResponse(
        data=hotel_service.create_hotel_detail(
            session=session, 
            place_id=place_id, 
            hotel_detail_in=hotel_detail_in
        )
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
    return HotelDetailResponse(
        data=hotel_service.update_hotel_detail(
            session=session, 
            place_id=place_id, 
            hotel_detail_in=hotel_detail_in
        )
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