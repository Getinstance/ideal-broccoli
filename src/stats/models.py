from pydantic import BaseModel


class OverviewResponse(BaseModel):
    total_books: int
    total_categories: int
    average_price: float
    average_rating: float
    available_books: int
    unavailable_books: int


class CategoriesStatsResponse(BaseModel):
    category_id: int
    category_name: str
    total_books: int
    average_price: float
    average_rating: float
