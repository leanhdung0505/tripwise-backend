from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Dict, Any
from uuid import UUID
from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.models import (
    ItineraryPublic, ItineraryCreate, ItineraryUpdate,
    ItineraryDayPublic, ItineraryDayCreate, ItineraryDayUpdate,
    ItineraryActivityPublic, ItineraryActivityCreate, ItineraryActivityUpdate,
    Message, PaginatedResponse,ItineraryResponse
)
from app.services.itineraries.itinerary_service import itinerary_service

router = APIRouter(prefix="/itineraries", tags=["itineraries"])

@router.get("", response_model=PaginatedResponse[ItineraryPublic])
def read_itineraries(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    destination: str = Query(None, description="Filter by destination city"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> PaginatedResponse[ItineraryPublic]:
    """
    Get user itineraries with optional filter for destination.
    """
    if destination:
        result = itinerary_service.get_itineraries(
            session=session, 
            user_id=current_user.user_id, 
            destination=destination, 
            page=page, 
            limit=limit
        )
    else:
        result = itinerary_service.get_itineraries(
            session=session, 
            user_id=current_user.user_id, 
            page=page, 
            limit=limit
        )
    return PaginatedResponse(**result)

@router.get("/{itinerary_id}", response_model=ItineraryResponse)
def read_itinerary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_id: int
) -> ItineraryResponse:
    """
    Get itinerary by ID.
    """
    itinerary = itinerary_service.get_itinerary(session=session, itinerary_id=itinerary_id,current_user=current_user.user_id)
    return ItineraryResponse(data=itinerary)

@router.post("", response_model=ItineraryResponse)
def create_itinerary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_in: ItineraryCreate
) -> ItineraryResponse:
    """
    Create new itinerary.
    """
    itinerary = itinerary_service.create_itinerary(
        session=session, 
        user_id=current_user.user_id, 
        itinerary_in=itinerary_in
    )
    return ItineraryResponse(data=itinerary)

@router.patch("/{itinerary_id}", response_model=ItineraryResponse)
def update_itinerary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_id: int,
    itinerary_in: ItineraryUpdate
) -> ItineraryResponse:
    """
    Update itinerary.
    """
    itinerary = itinerary_service.update_itinerary(
        session=session, 
        user_id=current_user.user_id, 
        itinerary_id=itinerary_id, 
        itinerary_in=itinerary_in
    )
    return ItineraryResponse(data=itinerary)

@router.delete("/{itinerary_id}", response_model=Message)
def delete_itinerary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_id: int
) -> Message:
    """
    Delete itinerary.
    """
    return itinerary_service.delete_itinerary(
        session=session, 
        user_id=current_user.user_id, 
        itinerary_id=itinerary_id
    )

# Itinerary Days endpoints
@router.post("/{itinerary_id}/days", response_model=ItineraryDayPublic)
def add_itinerary_day(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_id: int,
    day_in: ItineraryDayCreate
) -> ItineraryDayPublic:
    """
    Add a day to an itinerary.
    """
    return itinerary_service.add_day(
        session=session, 
        user_id=current_user.user_id, 
        itinerary_id=itinerary_id, 
        day_in=day_in
    )

@router.put("/days/{day_id}", response_model=ItineraryDayPublic)
def update_itinerary_day(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    day_id: int,
    day_in: ItineraryDayUpdate
) -> ItineraryDayPublic:
    """
    Update an itinerary day.
    """
    return itinerary_service.update_day(
        session=session, 
        user_id=current_user.user_id, 
        day_id=day_id, 
        day_in=day_in
    )

@router.delete("/days/{day_id}", response_model=Message)
def delete_itinerary_day(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    day_id: int
) -> Message:
    """
    Delete an itinerary day.
    """
    return itinerary_service.delete_day(
        session=session, 
        user_id=current_user.user_id, 
        day_id=day_id
    )

# Itinerary Activities endpoints
@router.post("/days/{day_id}/activities", response_model=ItineraryActivityPublic)
def add_itinerary_activity(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    day_id: int,
    activity_in: ItineraryActivityCreate
) -> ItineraryActivityPublic:
    """
    Add an activity to an itinerary day.
    """
    return itinerary_service.add_activity(
        session=session, 
        user_id=current_user.user_id, 
        day_id=day_id, 
        activity_in=activity_in
    )

@router.patch("/activities/{activity_id}", response_model=ItineraryActivityPublic)
def update_itinerary_activity(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    activity_id: int,
    activity_in: ItineraryActivityUpdate
) -> ItineraryActivityPublic:
    """
    Update an itinerary activity.
    """
    return itinerary_service.update_activity(
        session=session, 
        user_id=current_user.user_id, 
        activity_id=activity_id, 
        activity_in=activity_in
    )

@router.delete("/activities/{activity_id}", response_model=Message)
def delete_itinerary_activity(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    activity_id: int
) -> Message:
    """
    Delete an itinerary activity.
    """
    return itinerary_service.delete_activity(
        session=session, 
        user_id=current_user.user_id, 
        activity_id=activity_id
    )