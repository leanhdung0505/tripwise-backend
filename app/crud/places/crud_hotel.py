from typing import Optional, List
from sqlalchemy import func
from sqlmodel import Session, select
from app.models import HotelDetails, HotelDetailCreate, HotelDetailUpdate

class CRUDHotel:
    def get_by_id(self, session: Session, hotel_detail_id: int) -> Optional[HotelDetails]:
        return session.get(HotelDetails, hotel_detail_id)
    
    def get_by_place_id(self, session: Session, place_id: int) -> Optional[HotelDetails]:
        return session.exec(select(HotelDetails).where(HotelDetails.place_id == place_id)).first()
    
    def get_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[HotelDetails]:
        return session.exec(select(HotelDetails).offset(skip).limit(limit)).all()
     
    def create(self, session: Session, place_id: int, hotel_detail_create: HotelDetailCreate) -> HotelDetails:
        db_obj = HotelDetails(
            place_id=place_id,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(self, session: Session, db_hotel_detail: HotelDetails, hotel_detail_in: HotelDetailUpdate) -> HotelDetails:
        update_data = hotel_detail_in.model_dump(exclude_unset=True)
        db_hotel_detail.sqlmodel_update(update_data)
        session.add(db_hotel_detail)
        session.commit()
        session.refresh(db_hotel_detail)
        return db_hotel_detail
    
    def delete(self, session: Session, hotel_detail_id: int) -> None:
        db_obj = session.get(HotelDetails, hotel_detail_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
    
    def delete_by_place_id(self, session: Session, place_id: int) -> None:
        db_obj = session.exec(select(HotelDetails).where(HotelDetails.place_id == place_id)).first()
        if db_obj:
            session.delete(db_obj)
            session.commit()
    def get_count(self, session: Session) -> int:
        result = session.exec(select(func.count()).select_from(HotelDetails))
        return result.one()
# Create and export an instance
crud_hotel_detail = CRUDHotel()

# Make sure to export the instance
__all__ = ["crud_hotel"]