from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List, Optional, Tuple
from app.models import (
    HotelDetails, HotelDetailCreate, HotelDetailUpdate, 
    HotelDetailResponse, Message, PaginationMetadata
)
from app.crud.places.crud_hotel import crud_hotel_detail
from app.services.places.place_service import place_service

class HotelService:
    def get_hotel_detail(self, session: Session, hotel_detail_id: int) -> HotelDetails:
        hotel_detail = crud_hotel_detail.get_by_id(session=session, hotel_detail_id=hotel_detail_id)
        if not hotel_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel detail not found"
            )
        return hotel_detail
    
    def get_hotel_detail_by_place(self, session: Session, place_id: int) -> HotelDetails:
        # First check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        hotel_detail = crud_hotel_detail.get_by_place_id(session=session, place_id=place_id)
        if not hotel_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel detail not found for this place"
            )
        return hotel_detail
    
    def get_hotel_details(
        self, 
        session: Session, 
        page: int = 1, 
        limit: int = 10
    ) -> Tuple[List[HotelDetails], PaginationMetadata]:
        # Calculate skip value based on page and limit
        skip = (page - 1) * limit
        
        # Get total count
        total_count = crud_hotel_detail.get_count(session=session)
        
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit if limit else 1
        
        # Get hotel details for the current page
        hotel_details = crud_hotel_detail.get_multi(session=session, skip=skip, limit=limit)
        
        # Create pagination metadata
        has_prev = page > 1
        has_next = (page * limit) < total_count
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=has_prev,
            has_next=has_next,
            total_pages=total_pages
        )
        
        return hotel_details, pagination
    
    def create_hotel_detail(self, session: Session, place_id: int, hotel_detail_in: HotelDetailCreate) -> HotelDetails:
        # Check if place exists and is a hotel
        place = place_service.get_place(session=session, place_id=place_id)
        if place.type != "HOTEL":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Place is not a hotel"
            )
        
        # Check if hotel detail already exists
        existing = crud_hotel_detail.get_by_place_id(session=session, place_id=place_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hotel detail already exists for this place"
            )
        
        return crud_hotel_detail.create(
            session=session, 
            place_id=place_id, 
            hotel_detail_create=hotel_detail_in
        )
    
    def update_hotel_detail(self, session: Session, place_id: int, hotel_detail_in: HotelDetailUpdate) -> HotelDetails:
        # Check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        # Get existing hotel detail
        db_hotel_detail = crud_hotel_detail.get_by_place_id(session=session, place_id=place_id)
        if not db_hotel_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel detail not found for this place"
            )
        
        return crud_hotel_detail.update(
            session=session, 
            db_hotel_detail=db_hotel_detail, 
            hotel_detail_in=hotel_detail_in
        )
    
    def delete_hotel_detail(self, session: Session, place_id: int) -> Message:
        # Check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        # Get existing hotel detail
        db_hotel_detail = crud_hotel_detail.get_by_place_id(session=session, place_id=place_id)
        if not db_hotel_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel detail not found for this place"
            )
        
        crud_hotel_detail.delete_by_place_id(session=session, place_id=place_id)
        return Message(detail="Hotel detail deleted successfully")

hotel_service = HotelService()