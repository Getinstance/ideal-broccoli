from database.database import get_db
from sqlalchemy.orm import Session
from categories import models   

def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = next(get_db())
):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

def add_category(
    category: models.Category,
    db: Session = next(get_db())
):
    db.add(category)
    db.commit()
    return category