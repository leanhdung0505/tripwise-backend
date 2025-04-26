from typing import Optional, List
from sqlmodel import Session, select
from app.models import RestaurantDetails, RestaurantDetailCreate, RestaurantDetailUpdate

class CRUDRestaurant:
    def get_by_id(self, session: Session, restaurant_detail_id: int) -> Optional[RestaurantDetails]:
        return session.get(RestaurantDetails, restaurant_detail_id)
    
    def get_by_place_id(self, session: Session, place_id: int) -> Optional[RestaurantDetails]:
        return session.exec(select(RestaurantDetails).where(RestaurantDetails.place_id == place_id)).first()
    
    def get_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[RestaurantDetails]:
        return session.exec(select(RestaurantDetails).offset(skip).limit(limit)).all()
    
    def create(self, session: Session, place_id: int, restaurant_detail_create: RestaurantDetailCreate) -> RestaurantDetails:
        db_obj = RestaurantDetails(
            place_id=place_id,
            meal_types=restaurant_detail_create.meal_types
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(self, session: Session, db_restaurant_detail: RestaurantDetails, restaurant_detail_in: RestaurantDetailUpdate) -> RestaurantDetails:
        update_data = restaurant_detail_in.model_dump(exclude_unset=True)
        db_restaurant_detail.sqlmodel_update(update_data)
        session.add(db_restaurant_detail)
        session.commit()
        session.refresh(db_restaurant_detail)
        return db_restaurant_detail
    
    def delete(self, session: Session, restaurant_detail_id: int) -> None:
        db_obj = session.get(RestaurantDetails, restaurant_detail_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
    
    def delete_by_place_id(self, session: Session, place_id: int) -> None:
        db_obj = session.exec(select(RestaurantDetails).where(RestaurantDetails.place_id == place_id)).first()
        if db_obj:
            session.delete(db_obj)
            session.commit()

# Create and export an instance
crud_restaurant = CRUDRestaurant()

# Make sure to export the instance
__all__ = ["crud_restaurant"]