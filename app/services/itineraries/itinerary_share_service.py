from fastapi import HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
import uuid
from app.models import (
    Message, ItineraryShares, Users, Itineraries,
    PaginationMetadata, ItinerarySharePublic, ItineraryPublic,Places,UserPublicMinimal
)
from app.services.places.place_service import place_service
from app.crud.itineraries.crud_itinerary_share import crud_itinerary_share


class ItineraryShareService:
    def _get_share_with_details(self, session: Session, share: ItineraryShares) -> ItinerarySharePublic:
        """Helper method to get share with itinerary and user details"""
        itinerary = session.get(Itineraries, share.itinerary_id)
        
        # Get shared user details
        shared_user = session.get(Users, share.shared_with_user_id)
        
        return ItinerarySharePublic(
            share_id=share.share_id,
            itinerary_id=share.itinerary_id,
            shared_with_user_id=share.shared_with_user_id,
            permission=share.permission,
            created_at=share.created_at,
            updated_at=share.updated_at,
            itinerary=itinerary,
            shared_with_user=shared_user
        )

    def get_share(self, session: Session, share_id: int) -> ItinerarySharePublic:
        share = crud_itinerary_share.get_by_id(session=session, share_id=share_id)
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary share not found"
            )
        
        return self._get_share_with_details(session=session, share=share)
    
    def get_shares(self, session: Session, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit

        # Get one more item than the requested limit to check if there's a next page
        shares = crud_itinerary_share.get_multi(session=session, skip=skip, limit=limit + 1)
        total_items = crud_itinerary_share.get_count(session=session)
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(shares) > limit
        if has_next:
            shares = shares[:limit]

        shares_with_details = []
        for share in shares:
            shares_with_details.append(self._get_share_with_details(session=session, share=share))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": shares_with_details,
            "pagination": pagination
        }
    
    def get_shares_by_itinerary(self, session: Session, itinerary_id: int, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        # Check if itinerary exists
        itinerary = session.get(Itineraries, itinerary_id)
        if not itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found"
            )
        
        skip = (page - 1) * limit
        shares = crud_itinerary_share.get_by_itinerary_id(session=session, itinerary_id=itinerary_id, skip=skip, limit=limit + 1)
        total_items = crud_itinerary_share.get_count_by_itinerary_id(session=session, itinerary_id=itinerary_id)
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(shares) > limit
        if has_next:
            shares = shares[:limit]

        shares_with_details = []
        for share in shares:
            shares_with_details.append(self._get_share_with_details(session=session, share=share))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": shares_with_details,
            "pagination": pagination
        }
    
    def get_shares_by_user(self, session: Session, shared_with_user_id: uuid.UUID, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        # Check if user exists
        user = session.get(Users, shared_with_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        skip = (page - 1) * limit
        shares = crud_itinerary_share.get_by_shared_user_id(session=session, shared_with_user_id=shared_with_user_id, skip=skip, limit=limit + 1)
        total_items = crud_itinerary_share.get_count_by_shared_user_id(session=session, shared_with_user_id=shared_with_user_id)
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(shares) > limit
        if has_next:
            shares = shares[:limit]

        shares_with_details = []
        for share in shares:
            shares_with_details.append(self._get_share_with_details(session=session, share=share))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": shares_with_details,
            "pagination": pagination
        }
    
    def get_shares_by_permission(self, session: Session, permission: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit
        shares = crud_itinerary_share.get_by_permission(session=session, permission=permission, skip=skip, limit=limit + 1)
        total_items = crud_itinerary_share.get_count_by_permission(session=session, permission=permission)
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(shares) > limit
        if has_next:
            shares = shares[:limit]

        shares_with_details = []
        for share in shares:
            shares_with_details.append(self._get_share_with_details(session=session, share=share))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": shares_with_details,
            "pagination": pagination
        }
    
    def create_share(self, session: Session, itinerary_id: int, shared_with_user_id: uuid.UUID, permission: str = "view") -> ItinerarySharePublic:
        # Check if itinerary exists
        itinerary = session.get(Itineraries, itinerary_id)
        if not itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found"
            )
        
        # Check if user exists
        user = session.get(Users, shared_with_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if share already exists
        existing_share = crud_itinerary_share.get_by_itinerary_and_user(
            session=session, 
            itinerary_id=itinerary_id, 
            shared_with_user_id=shared_with_user_id
        )
        if existing_share:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Itinerary is already shared with this user"
            )
        
        share = crud_itinerary_share.create(
            session=session, 
            itinerary_id=itinerary_id, 
            shared_with_user_id=shared_with_user_id, 
            permission=permission
        )
        
        return self._get_share_with_details(session=session, share=share)
    
    def update_share_permission(self, session: Session, share_id: int, permission: str, user_id: uuid.UUID) -> ItinerarySharePublic:
        share = crud_itinerary_share.get_by_id(session=session, share_id=share_id)
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary share not found"
            )

        # Lấy itinerary để kiểm tra quyền
        itinerary = session.get(Itineraries, share.itinerary_id)
        if not itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found"
            )

        # Chỉ cho phép chủ sở hữu itinerary thay đổi quyền
        if user_id != itinerary.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can update share permission"
            )

        if permission not in ["view", "edit"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission must be either 'view' or 'edit'"
            )
        
        updated_share = crud_itinerary_share.update_permission(
            session=session, 
            db_share=share, 
            permission=permission
        )
        
        return self._get_share_with_details(session=session, share=updated_share)
    
    def delete_share(self, session: Session, share_id: int, user_id: uuid.UUID) -> Message:
        share = crud_itinerary_share.get_by_id(session=session, share_id=share_id)
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary share not found"
            )

        itinerary = session.get(Itineraries, share.itinerary_id)
        if not itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found"
            )

        # Chỉ cho phép chủ sở hữu itinerary xóa share
        if user_id != itinerary.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can delete itinerary share"
            )

        crud_itinerary_share.delete(session=session, share_id=share_id)
        return Message(detail="Itinerary share deleted successfully")
    
    def delete_share_by_itinerary_and_user(self, session: Session, itinerary_id: int, shared_with_user_id: uuid.UUID, user_id: uuid.UUID) -> Message:
        itinerary = session.get(Itineraries, itinerary_id)
        if not itinerary:
            raise HTTPException(status_code=404, detail="Itinerary not found")
        if itinerary.user_id != user_id:
            raise HTTPException(status_code=403, detail="Only the owner can delete itinerary share")

        share = crud_itinerary_share.get_by_itinerary_and_user(
            session=session, 
            itinerary_id=itinerary_id, 
            shared_with_user_id=shared_with_user_id
        )
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary share not found"
            )
        
        crud_itinerary_share.delete_by_itinerary_and_user(
            session=session, 
            itinerary_id=itinerary_id, 
            shared_with_user_id=shared_with_user_id
        )
        return Message(detail="Itinerary share deleted successfully")
    
    def get_shared_itineraries_for_user(
        self, session: Session, shared_with_user_id: uuid.UUID, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        # Check if user exists
        user = session.get(Users, shared_with_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        skip = (page - 1) * limit
        shares = crud_itinerary_share.get_by_shared_user_id(
            session=session, shared_with_user_id=shared_with_user_id, skip=skip, limit=limit + 1
        )
        total_items = crud_itinerary_share.get_count_by_shared_user_id(
            session=session, shared_with_user_id=shared_with_user_id
        )
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(shares) > limit
        if has_next:
            shares = shares[:limit]

        itineraries = []
        for share in shares:
            itinerary = session.get(Itineraries, share.itinerary_id)
            if itinerary:
                itinerary_data = itinerary.dict()
                itinerary_data["days"] = []
                share_objs = session.exec(
                    select(ItineraryShares).where(ItineraryShares.itinerary_id == itinerary.itinerary_id)
                ).all()
                shared_users = []
                for s in share_objs:
                    user_obj = session.get(Users, s.shared_with_user_id)
                    if user_obj:
                        shared_user_with_permission = UserPublicMinimal(
                            user_id=user_obj.user_id,
                            username=user_obj.username,
                            full_name=user_obj.full_name,
                            email=user_obj.email,
                            profile_picture=user_obj.profile_picture,
                            permissions=s.permission 
                        )
                    shared_users.append(shared_user_with_permission)
                itinerary_data["shared_users"] = shared_users
                
                # Lấy thông tin hotel nếu có
                if itinerary.hotel_id:
                    hotel_place = session.get(Places, itinerary.hotel_id)
                    if hotel_place:
                        itinerary_data["hotel"] = place_service._get_place_with_details(session, hotel_place)
                    else:
                        itinerary_data["hotel"] = None
                else:
                    itinerary_data["hotel"] = None        
                # Lấy thông tin chủ sở hữu itinerary
                owner = session.get(Users, itinerary.user_id)
                if owner:
                    itinerary_data["owner"] = UserPublicMinimal(
                        user_id=owner.user_id,
                        username=owner.username,
                        full_name=owner.full_name,
                        email=owner.email,
                        profile_picture=owner.profile_picture,
                        permissions="owner"  
                    )
                else:
                    itinerary_data["owner"] = None
            
                itineraries.append(ItineraryPublic(**itinerary_data))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": itineraries,
            "pagination": pagination.model_dump()
        }

itinerary_share_service = ItineraryShareService()