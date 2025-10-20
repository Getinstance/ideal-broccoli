from pydantic import BaseModel
from books.models import Book


class BookMLResponse(BaseModel):
    id: int
    price: int
    rating: int
    available: int
    category_id: int

    def from_book(book: Book) -> "BookMLResponse":
        return BookMLResponse(
            id=book.id,
            price=int(book.price * 100),  # Converte para centavos
            rating=book.rating,
            available=1 if book.available else 0,
            category_id=book.category_id,
        )


class BookPredictionRequest(BaseModel):
    price: int
    category_id: int


class BookPredictionResponse(BaseModel):
    predicted_rate: int
