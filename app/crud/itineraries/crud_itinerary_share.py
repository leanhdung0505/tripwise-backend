from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy import func
import uuid
from app.models import ItineraryShares

class CRUDItineraryShare:
    def get_by_id(self, session: Session, share_id: int) -> Optional[ItineraryShares]:
        return session.get(ItineraryShares, share_id)
    
    def get_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[ItineraryShares]:
        return session.exec(select(ItineraryShares).offset(skip).limit(limit)).all()
    
    def get_by_itinerary_id(self, session: Session, itinerary_id: int, skip: int = 0, limit: int = 100) -> List[ItineraryShares]:
        return session.exec(
            select(ItineraryShares)
            .where(ItineraryShares.itinerary_id == itinerary_id)
            .offset(skip)
            .limit(limit)
        ).all()
    
    def get_by_shared_user_id(self, session: Session, shared_with_user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[ItineraryShares]:
        return session.exec(
            select(ItineraryShares)
            .where(ItineraryShares.shared_with_user_id == shared_with_user_id)
            .offset(skip)
            .limit(limit)
        ).all()
    
    def get_by_itinerary_and_user(self, session: Session, itinerary_id: int, shared_with_user_id: uuid.UUID) -> Optional[ItineraryShares]:
        return session.exec(
            select(ItineraryShares)
            .where(
                ItineraryShares.itinerary_id == itinerary_id,
                ItineraryShares.shared_with_user_id == shared_with_user_id
            )
        ).first()
    
    def get_by_permission(self, session: Session, permission: str, skip: int = 0, limit: int = 100) -> List[ItineraryShares]:
        return session.exec(
            select(ItineraryShares)
            .where(ItineraryShares.permission == permission)
            .offset(skip)
            .limit(limit)
        ).all()
    
    def create(self, session: Session, itinerary_id: int, shared_with_user_id: uuid.UUID, permission: str = "view") -> ItineraryShares:
        db_obj = ItineraryShares(
            itinerary_id=itinerary_id,
            shared_with_user_id=shared_with_user_id,
            permission=permission
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update_permission(self, session: Session, db_share: ItineraryShares, permission: str) -> ItineraryShares:
        db_share.permission = permission
        session.add(db_share)
        session.commit()
        session.refresh(db_share)
        return db_share
    
    def delete(self, session: Session, share_id: int) -> None:
        db_obj = session.get(ItineraryShares, share_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
    
    def delete_by_itinerary_and_user(self, session: Session, itinerary_id: int, shared_with_user_id: uuid.UUID) -> None:
        db_obj = self.get_by_itinerary_and_user(session, itinerary_id, shared_with_user_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
    
    def get_count(self, session: Session) -> int:
        result = session.exec(select(func.count()).select_from(ItineraryShares))
        return result.one()
    
    def get_count_by_itinerary_id(self, session: Session, itinerary_id: int) -> int:
        result = session.exec(
            select(func.count())
            .select_from(ItineraryShares)
            .where(ItineraryShares.itinerary_id == itinerary_id)
        )
        return result.one()
    
    def get_count_by_shared_user_id(self, session: Session, shared_with_user_id: uuid.UUID) -> int:
        result = session.exec(
            select(func.count())
            .select_from(ItineraryShares)
            .where(ItineraryShares.shared_with_user_id == shared_with_user_id)
        )
        return result.one()
    
    def get_count_by_permission(self, session: Session, permission: str) -> int:
        result = session.exec(
            select(func.count())
            .select_from(ItineraryShares)
            .where(ItineraryShares.permission == permission)
        )
        return result.one()

# Create and export an instance
crud_itinerary_share = CRUDItineraryShare()

# Make sure to export the instance
__all__ = ["crud_itinerary_share"]