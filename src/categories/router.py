from fastapi import APIRouter
import categories.categories as categories_service
from categories.models import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "/",
    summary="Get all categories",
    response_model=list[CategoryResponse],
    status_code=200,
)
async def get_categories():
    return categories_service.get_categories()
