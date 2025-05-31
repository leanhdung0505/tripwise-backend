from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Dict, Any
import uuid
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message, 
    ItineraryShareCreate,
    ItineraryShareUpdate,
    ItinerarySharePublic,
    ItineraryShareResponse,
    ItinerarySharesResponse,
    UserPublicMinimal,
    Itineraries,
    ItineraryPublic,
    PaginationMetadata,
    PaginatedResponse
)
from app.services.itineraries.itinerary_share_service import itinerary_share_service
from app.services.users.user_service import user_service

router = APIRouter(prefix="/itinerary-shares", tags=["itinerary-shares"])
@router.get("/search-users-to-share", response_model=Dict[str, list[UserPublicMinimal]])
def search_users_to_share(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_id: int = Query(..., description="Itinerary ID"),
    query: str = Query(..., min_length=1, description="Search by username or email"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search for users to share itinerary with, excluding users already shared and the owner.
    """
    shared_user_ids = [
        share.shared_with_user_id
        for share in itinerary_share_service.get_shares_by_itinerary(
            session=session,
            itinerary_id=itinerary_id,
            page=1,
            limit=10000  # lấy hết
        )["data"]
    ]
    # Thêm cả chủ sở hữu itinerary vào danh sách loại trừ
    itinerary = session.get(Itineraries, itinerary_id)    
    if itinerary:
        shared_user_ids.append(itinerary.user_id)

    # Tìm user chưa được share
    users = user_service.search_users_exclude_ids(
        session=session,
        query=query,
        exclude_ids=shared_user_ids,
        limit=limit
    )
    return {"data": users}

@router.get("", response_model=ItinerarySharesResponse)
def read_itinerary_shares(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_id: int = Query(None, description="Filter by itinerary ID"),
    shared_with_user_id: str = Query(None, description="Filter by shared user ID"),
    permission: str = Query(None, description="Filter by permission (view, edit)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> ItinerarySharesResponse:
    """
    Get itinerary shares with optional filters.
    """
    result = None
    
    if itinerary_id:
        result = itinerary_share_service.get_shares_by_itinerary(
            session=session, 
            itinerary_id=itinerary_id, 
            page=page, 
            limit=limit
        )
    elif shared_with_user_id:
        try:
            user_uuid = uuid.UUID(shared_with_user_id)
            result = itinerary_share_service.get_shares_by_user(
                session=session, 
                shared_with_user_id=user_uuid, 
                page=page, 
                limit=limit
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid UUID format for shared_with_user_id"
            )
    elif permission:
        if permission not in ["view", "edit"]:
            raise HTTPException(
                status_code=400,
                detail="Permission must be either 'view' or 'edit'"
            )
        result = itinerary_share_service.get_shares_by_permission(
            session=session, 
            permission=permission, 
            page=page, 
            limit=limit
        )
    else:
        result = itinerary_share_service.get_shares(
            session=session, 
            page=page, 
            limit=limit
        )
    
    return result

@router.get("/{share_id}", response_model=ItineraryShareResponse)
def read_itinerary_share(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    share_id: int = Path(..., description="Itinerary share ID")
) -> ItineraryShareResponse:
    """
    Get itinerary share by ID.
    """
    share = itinerary_share_service.get_share(session=session, share_id=share_id)
    return ItineraryShareResponse(data=share)

@router.post("", response_model=ItineraryShareResponse)
def create_itinerary_share(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    share_data: ItineraryShareCreate
) -> ItineraryShareResponse:
    """
    Create new itinerary share.
    """
    if share_data.permission not in ["view", "edit"]:
        raise HTTPException(
            status_code=400,
            detail="Permission must be either 'view' or 'edit'"
        )
    
    share = itinerary_share_service.create_share(
        session=session, 
        itinerary_id=share_data.itinerary_id, 
        shared_with_user_id=share_data.shared_with_user_id, 
        permission=share_data.permission
    )
    return ItineraryShareResponse(data=share)

@router.put("/{share_id}", response_model=ItineraryShareResponse)
def update_itinerary_share(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    share_id: int = Path(..., description="Itinerary share ID"),
    share_update: ItineraryShareUpdate
) -> ItineraryShareResponse:
    """
    Update itinerary share permission.
    """
    if share_update.permission and share_update.permission not in ["view", "edit"]:
        raise HTTPException(
            status_code=400,
            detail="Permission must be either 'view' or 'edit'"
        )
    
    share = itinerary_share_service.update_share_permission(
        session=session, 
        share_id=share_id, 
        permission=share_update.permission,
        user_id=current_user.user_id
    )
    return ItineraryShareResponse(data=share)

@router.delete("/{share_id}", response_model=Message)
def delete_itinerary_share(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    share_id: int = Path(..., description="Itinerary share ID")
) -> Message:
    """
    Delete itinerary share.
    """
    return itinerary_share_service.delete_share(session=session, share_id=share_id, user_id = current_user.user_id)

@router.delete("", response_model=Message)
def delete_itinerary_share_by_itinerary_and_user(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_id: int = Query(..., description="Itinerary ID"),
    shared_with_user_id: str = Query(..., description="User ID to unshare with")
) -> Message:
    """
    Delete itinerary share by itinerary ID and user ID.
    """
    try:
        user_uuid = uuid.UUID(shared_with_user_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format for shared_with_user_id"
        )
    
    return itinerary_share_service.delete_share_by_itinerary_and_user(
        session=session, 
        itinerary_id=itinerary_id, 
        shared_with_user_id=user_uuid,
        user_id=current_user.user_id
    )

@router.get("/itinerary/{itinerary_id}/shares", response_model=ItinerarySharesResponse)
def get_itinerary_shares(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    itinerary_id: int = Path(..., description="Itinerary ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> ItinerarySharesResponse:
    """
    Get all shares for a specific itinerary.
    """
    return itinerary_share_service.get_shares_by_itinerary(
        session=session, 
        itinerary_id=itinerary_id, 
        page=page, 
        limit=limit
    )
@router.get("/me/shared-itineraries", response_model=PaginatedResponse[ItineraryPublic])
def get_shared_itineraries_for_user(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> Dict[str, Any]:
    """
    Get all itineraries shared with a specific user.
    """
    user_uuid = current_user.user_id

    result = itinerary_share_service.get_shared_itineraries_for_user(
        session=session,
        shared_with_user_id=user_uuid,
        page=page,
        limit=limit
    )
    return result

