from typing import Optional, List
from sqlmodel import Session, select
from app.models import AttractionDetails, AttractionDetailCreate, AttractionDetailUpdate

class CRUDAttraction:
    def get_by_id(self, session: Session, attraction_detail_id: int) -> Optional[AttractionDetails]:
        return session.get(AttractionDetails, attraction_detail_id)
    
    def get_by_place_id(self, session: Session, place_id: int) -> Optional[AttractionDetails]:
        return session.exec(select(AttractionDetails).where(AttractionDetails.place_id == place_id)).first()
    
    def get_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[AttractionDetails]:
        return session.exec(select(AttractionDetails).offset(skip).limit(limit)).all()
    
    def create(self, session: Session, place_id: int, attraction_detail_create: AttractionDetailCreate) -> AttractionDetails:
        db_obj = AttractionDetails(
            place_id=place_id,
            subcategory=attraction_detail_create.subcategory,
            subtype=attraction_detail_create.subtype
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(self, session: Session, db_attraction_detail: AttractionDetails, attraction_detail_in: AttractionDetailUpdate) -> AttractionDetails:
        update_data = attraction_detail_in.model_dump(exclude_unset=True)
        db_attraction_detail.sqlmodel_update(update_data)
        session.add(db_attraction_detail)
        session.commit()
        session.refresh(db_attraction_detail)
        return db_attraction_detail
    
    def delete(self, session: Session, attraction_detail_id: int) -> None:
        db_obj = session.get(AttractionDetails, attraction_detail_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
    
    def delete_by_place_id(self, session: Session, place_id: int) -> None:
        db_obj = session.exec(select(AttractionDetails).where(AttractionDetails.place_id == place_id)).first()
        if db_obj:
            session.delete(db_obj)
            session.commit()

# Create and export an instance
crud_attraction = CRUDAttraction()

# Make sure to export the instance
__all__ = ["crud_attraction"]