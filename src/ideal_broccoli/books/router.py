from fastapi import APIRouter
import books.books as books
router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/")
def get_books():
    return books.get_books()