from fastapi import APIRouter
import categories.categories as categories
router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/")
def get_categories():
    return categories.get_categories()