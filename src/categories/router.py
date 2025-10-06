from fastapi import APIRouter, Depends
from auth.models import User
from auth.router import get_current_user
import categories.categories as categories_service
from categories.models import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "/",
    summary="Get all categories",
    response_model=list[CategoryResponse],
    status_code=200,
)
async def get_categories(current_user: User = Depends(get_current_user),):
    return categories_service.get_categories()
