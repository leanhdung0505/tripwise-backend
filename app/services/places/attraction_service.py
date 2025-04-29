from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List, Optional, Tuple
from app.models import (
    AttractionDetails, AttractionDetailCreate, AttractionDetailUpdate, 
    AttractionDetailResponse, AttractionDetailPublic, Message, PaginatedResponse, PaginationMetadata
)
from app.crud.places.crud_attraction import crud_attraction
from app.services.places.place_service import place_service

class AttractionService:
    def get_attraction_detail(self, session: Session, attraction_detail_id: int) -> AttractionDetails:
        attraction_detail = crud_attraction.get_by_id(session=session, attraction_detail_id=attraction_detail_id)
        if not attraction_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attraction detail not found"
            )
        return attraction_detail
    
    def get_attraction_detail_by_place(self, session: Session, place_id: int) -> AttractionDetails:
        # First check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        attraction_detail = crud_attraction.get_by_place_id(session=session, place_id=place_id)
        if not attraction_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attraction detail not found for this place"
            )
        return attraction_detail
    
    def get_attraction_details(
        self, 
        session: Session, 
        page: int = 1, 
        limit: int = 10
    ) -> Tuple[List[AttractionDetails], PaginationMetadata]:
        # Calculate skip value based on page and limit
        skip = (page - 1) * limit
        
        # Get total count
        total_count = crud_attraction.get_count(session=session)
        
        # Get attraction details for the current page
        attraction_details = crud_attraction.get_multi(session=session, skip=skip, limit=limit)
        
        # Create pagination metadata
        has_prev = page > 1
        has_next = (page * limit) < total_count
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=has_prev,
            has_next=has_next
        )
        
        return attraction_details, pagination
    
    def create_attraction_detail(self, session: Session, place_id: int, attraction_detail_in: AttractionDetailCreate) -> AttractionDetails:
        # Check if place exists and is an attraction
        place = place_service.get_place(session=session, place_id=place_id)
        if place.type != "ATTRACTION":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Place is not an attraction"
            )
        
        # Check if attraction detail already exists
        existing = crud_attraction.get_by_place_id(session=session, place_id=place_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attraction detail already exists for this place"
            )
        
        return crud_attraction.create(
            session=session, 
            place_id=place_id, 
            attraction_detail_create=attraction_detail_in
        )
    
    def update_attraction_detail(self, session: Session, place_id: int, attraction_detail_in: AttractionDetailUpdate) -> AttractionDetails:
        # Check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        # Get existing attraction detail
        db_attraction_detail = crud_attraction.get_by_place_id(session=session, place_id=place_id)
        if not db_attraction_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attraction detail not found for this place"
            )
        
        return crud_attraction.update(
            session=session, 
            db_attraction_detail=db_attraction_detail, 
            attraction_detail_in=attraction_detail_in
        )
    
    def delete_attraction_detail(self, session: Session, place_id: int) -> Message:
        # Check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        # Get existing attraction detail
        db_attraction_detail = crud_attraction.get_by_place_id(session=session, place_id=place_id)
        if not db_attraction_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attraction detail not found for this place"
            )
        
        crud_attraction.delete_by_place_id(session=session, place_id=place_id)
        return Message(detail="Attraction detail deleted successfully")

attraction_service = AttractionService()