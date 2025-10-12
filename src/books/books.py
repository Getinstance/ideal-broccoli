from sqlalchemy import and_
from database.database import get_db
from sqlalchemy.orm import Session
from books import models
from sqlalchemy import func


def get_books(
    page: int = 1,
    limit: int = 10,
    title: str = None,
    categoryId: int = None,
    db: Session = next(get_db()),
):
    query = db.query(models.Book)

    and_conditions = []

    if title:
        and_conditions.append(models.Book.title.ilike(f"%{title}%"))

    if categoryId:
        and_conditions.append(models.Book.category_id == categoryId)

    categories = (
        query.filter(and_(*and_conditions))
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return categories


def get_book_by_id(book_id: int, db: Session = next(get_db())):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    return book


def add_book(book: models.Book, db: Session = next(get_db())):
    db.add(book)
    db.commit()
    return book


def get_books_count(db: Session = next(get_db())):
    return db.query(models.Book).count()


def get_average_price_and_rating(db: Session = next(get_db())):
    avg_price = db.query(func.avg(models.Book.price)).scalar() or 0.0
    avg_rating = db.query(func.avg(models.Book.rating)).scalar() or 0.0
    return round(float(avg_price), 2), round(float(avg_rating), 2)


def get_available_books_count(db: Session = next(get_db())):
    return db.query(models.Book).filter(models.Book.available.is_(True)).count()
