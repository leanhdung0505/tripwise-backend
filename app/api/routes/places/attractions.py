from fastapi import APIRouter, Depends
from typing import List
from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.models import (
    AttractionDetailResponse, AttractionDetailCreate, AttractionDetailUpdate, 
    Message, PaginatedResponse, AttractionDetailPublic
)
from app.services.places.attraction_service import attraction_service

router = APIRouter(prefix="/attractions", tags=["attractions"])

@router.get("", response_model=PaginatedResponse[AttractionDetailPublic])
def read_attraction_details(
    *,
    session: SessionDep,
    page: int = 1,
    limit: int = 10
) -> PaginatedResponse[AttractionDetailPublic]:
    """
    Get all attraction details with pagination.
    """
    attraction_details, pagination = attraction_service.get_attraction_details(
        session=session, 
        page=page, 
        limit=limit
    )
    
    return PaginatedResponse(
        data=attraction_details,
        pagination=pagination
    )

@router.get("/{place_id}", response_model=AttractionDetailResponse)
def read_attraction_detail(
    *,
    session: SessionDep,
    place_id: int
) -> AttractionDetailResponse:
    """
    Get attraction details for a specific place.
    """
    return AttractionDetailResponse(
        data=attraction_service.get_attraction_detail_by_place(session=session, place_id=place_id)
    )

@router.post("/{place_id}", response_model=AttractionDetailResponse)
def create_attraction_detail(
    *,
    session: SessionDep,
    place_id: int,
    attraction_detail_in: AttractionDetailCreate,
    current_user: CurrentUser 
) -> AttractionDetailResponse:
    """
    Create attraction details for a place (admin only).
    """
    return AttractionDetailResponse(
        data=attraction_service.create_attraction_detail(
            session=session, 
            place_id=place_id, 
            attraction_detail_in=attraction_detail_in
        )
    )

@router.put("/{place_id}", response_model=AttractionDetailResponse)
def update_attraction_detail(
    *,
    session: SessionDep,
    place_id: int,
    attraction_detail_in: AttractionDetailUpdate,
    current_user: CurrentUser 
) -> AttractionDetailResponse:
    """
    Update attraction details for a place (admin only).
    """
    return AttractionDetailResponse(
        data=attraction_service.update_attraction_detail(
            session=session, 
            place_id=place_id, 
            attraction_detail_in=attraction_detail_in
        )
    )

@router.delete("/{place_id}", response_model=Message)
def delete_attraction_detail(
    *,
    session: SessionDep,
    place_id: int,
    current_user: CurrentUser 
) -> Message:
    """
    Delete attraction details for a place (admin only).
    """
    return attraction_service.delete_attraction_detail(session=session, place_id=place_id)