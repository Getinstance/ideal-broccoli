from database.database import get_db
from sqlalchemy.orm import Session
from books import models   

def get_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = next(get_db())
):
    categories = db.query(models.Book).offset(skip).limit(limit).all()
    return categories

def add_book(
    book: models.Book,
    db: Session = next(get_db())
):
    db.add(book)
    db.commit()
    return book