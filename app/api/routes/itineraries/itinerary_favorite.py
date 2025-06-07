from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func

from app.api.deps import SessionDep, CurrentUser
from app.models import Itineraries, ItineraryShares, Message, ItineraryPublic, PaginatedResponse, PaginationMetadata
from app.crud.itineraries.crud_favorite import crud_favorite

router = APIRouter(prefix="/api", tags=["Itinerary Favorite"])

@router.get("/favorite-itineraries", response_model=PaginatedResponse[ItineraryPublic])
def get_favorite_itineraries(
    session: SessionDep,
    current_user: CurrentUser,
    page: int = 1,
    limit: int = 10
):
    favorites = crud_favorite.get_favorites(session, current_user.user_id)
    itinerary_ids = [fav.itinerary_id for fav in favorites]
    if not itinerary_ids:
        return PaginatedResponse[ItineraryPublic](
            data=[],
            pagination=PaginationMetadata(
                page=page,
                limit=limit,
                total_pages=0,
                has_prev=False,
                has_next=False
            )
        )
    itineraries_query = select(Itineraries).where(Itineraries.itinerary_id.in_(itinerary_ids))
    
    # Đếm tổng số itinerary yêu thích
    count_query = select(func.count()).select_from(Itineraries).where(Itineraries.itinerary_id.in_(itinerary_ids))
    total = session.exec(count_query).one()

    total_pages = (total + limit - 1) // limit
    has_prev = page > 1
    has_next = page < total_pages

    itineraries = session.exec(
        itineraries_query.offset((page - 1) * limit).limit(limit)
    ).all()
  
    # Nếu bạn muốn trả về dạng ItineraryPublic:
    data = []
    for i in itineraries:
        item = ItineraryPublic.model_validate(i).model_dump()
        item["days"] = None
        item["is_favorite"] = True
        data.append(item)
    return PaginatedResponse[ItineraryPublic](
        data=data,
        pagination=PaginationMetadata(
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_prev=has_prev,
            has_next=has_next
        )
    )

@router.post("/itineraries/{itinerary_id}/favorite", response_model=Message)
def add_favorite_itinerary(
    itinerary_id: int,
    session: SessionDep,
    current_user: CurrentUser
):
    itinerary = session.get(Itineraries, itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    # Chủ sở hữu hoặc người được share mới được thêm
    if str(itinerary.user_id) != str(current_user.user_id):
        share = session.exec(
            select(ItineraryShares).where(
                (ItineraryShares.itinerary_id == itinerary_id) &
                (ItineraryShares.shared_with_user_id == current_user.user_id)
            )
        ).first()
        if not share:
            raise HTTPException(status_code=403, detail="You do not have permission to favorite this itinerary")
    crud_favorite.add(session, current_user.user_id, itinerary_id)
    return Message(detail="Added to favorites")

@router.delete("/itineraries/{itinerary_id}/favorite", response_model=Message)
def remove_favorite_itinerary(
    itinerary_id: int,
    session: SessionDep,
    current_user: CurrentUser
):
    fav = crud_favorite.remove(session, current_user.user_id, itinerary_id)
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return Message(detail="Removed from favorites")