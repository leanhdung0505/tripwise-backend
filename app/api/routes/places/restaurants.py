from fastapi import APIRouter, Depends
from typing import List
from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.models import (
    RestaurantDetailResponse, RestaurantDetailCreate, RestaurantDetailUpdate, Message
)
from app.services.places.restaurant_service import restaurant_service

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("", response_model=List[RestaurantDetailResponse])
def read_restaurant_details(
    *,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100
) -> List[RestaurantDetailResponse]:
    """
    Get all restaurant details.
    """
    return restaurant_service.get_restaurant_details(session=session, skip=skip, limit=limit)

@router.get("/{place_id}", response_model=RestaurantDetailResponse)
def read_restaurant_detail(
    *,
    session: SessionDep,
    place_id: int
) -> RestaurantDetailResponse:
    """
    Get restaurant details for a specific place.
    """
    return restaurant_service.get_restaurant_detail_by_place(session=session, place_id=place_id)

@router.post("/{place_id}", response_model=RestaurantDetailResponse)
def create_restaurant_detail(
    *,
    session: SessionDep,
    place_id: int,
    restaurant_detail_in: RestaurantDetailCreate,
    current_user: CurrentUser 
) -> RestaurantDetailResponse:
    """
    Create restaurant details for a place (admin only).
    """
    return restaurant_service.create_restaurant_detail(
        session=session, 
        place_id=place_id, 
        restaurant_detail_in=restaurant_detail_in
    )

@router.put("/{place_id}", response_model=RestaurantDetailResponse)
def update_restaurant_detail(
    *,
    session: SessionDep,
    place_id: int,
    restaurant_detail_in: RestaurantDetailUpdate,
    current_user: CurrentUser 
) -> RestaurantDetailResponse:
    """
    Update restaurant details for a place (admin only).
    """
    return restaurant_service.update_restaurant_detail(
        session=session, 
        place_id=place_id, 
        restaurant_detail_in=restaurant_detail_in
    )

@router.delete("/{place_id}", response_model=Message)
def delete_restaurant_detail(
    *,
    session: SessionDep,
    place_id: int,
    current_user: CurrentUser 
) -> Message:
    """
    Delete restaurant details for a place (admin only).
    """
    return restaurant_service.delete_restaurant_detail(session=session, place_id=place_id)