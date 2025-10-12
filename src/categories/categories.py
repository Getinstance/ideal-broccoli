from database.database import get_db
from sqlalchemy.orm import Session
from categories import models
from sqlalchemy import func
from books import models as book_models
from stats.models import CategoriesStatsResponse


def get_categories(skip: int = 0, limit: int = 100, db: Session = next(get_db())):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories


def add_category(category: models.Category, db: Session = next(get_db())):
    db.add(category)
    db.commit()
    return category


def get_categories_count(db: Session = next(get_db())):
    return db.query(models.Category).count()


def get_categories_stats(db: Session = next(get_db())) -> list[CategoriesStatsResponse]:

    stats = (
        db.query(
            models.Category.id.label("category_id"),
            models.Category.name.label("category_name"),
            func.count(book_models.Book.id).label("total_books"),
            func.avg(book_models.Book.price).label("average_price"),
            func.avg(book_models.Book.rating).label("average_rating"),
        )
        .join(
            book_models.Book,
            book_models.Book.category_id == models.Category.id,
            isouter=True,
        )
        .group_by(models.Category.id)
        .order_by(func.count(book_models.Book.id).desc())   
        .all()
    )

    result = [
        CategoriesStatsResponse(
            category_id=stat.category_id,
            category_name=stat.category_name,
            total_books=stat.total_books,
            average_price=float(stat.average_price),
            average_rating=float(stat.average_rating),
        )
        for stat in stats
    ]

    return result
