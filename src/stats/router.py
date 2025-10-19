from fastapi import APIRouter, Depends
from auth.models import User
import books.books as books_service
import categories.categories as cateogries_service
from database.database import get_db
from sqlalchemy.orm import Session
from auth.router import get_current_user
from stats.models import OverviewResponse, CategoriesStatsResponse

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get(
    "/overview",
    description="Retrieve useful statistics",
    response_model=OverviewResponse,
    status_code=200,
)
async def overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_books = books_service.get_books_count(db=db)
    total_categories = cateogries_service.get_categories_count(db=db)
    average_price, average_rating = books_service.get_average_price_and_rating(db=db)
    available_books = books_service.get_available_books_count(db=db)
    return OverviewResponse(
        total_books=total_books,
        total_categories=total_categories,
        average_price=average_price,
        average_rating=average_rating,
        available_books=available_books,
        unavailable_books=total_books - available_books,
    )


@router.get(
    "/categories",
    description="Get statistics about book categories",
    response_model=list[CategoriesStatsResponse],
    status_code=200,
)
async def statys_by_categories(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    categories_stats = cateogries_service.get_categories_stats(db=db)
    return categories_stats
