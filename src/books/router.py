from fastapi import APIRouter, Depends, HTTPException
import books.books as books_service
from books.models import BookResponse
from database.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/books", tags=["Books"])


@router.get(
    "/", description="Get all books", response_model=list[BookResponse], status_code=200
)
async def get_books(db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    return books_service.get_books(db=db, page=page, limit=limit)


@router.get(
    "/{book_id}",
    description="Get a book by id",
    response_model=BookResponse,
    status_code=200,
)
async def get_book_by_id(db: Session = Depends(get_db), book_id: int = None):

    book = books_service.get_book_by_id(db=db, book_id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.get(
    "/search/",
    description="Filter books by title or category ID",
    response_model=list[BookResponse],
    status_code=200,
)
async def get_books(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
    title: str = None,
    categoryId: int = None,
):
    return books_service.get_books(
        db=db, page=page, limit=limit, title=title, categoryId=categoryId
    )
