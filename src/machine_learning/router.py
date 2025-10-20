from fastapi import APIRouter, Depends
from auth.models import User
from machine_learning import machine_learning as ml_service
from machine_learning.models import BookMLResponse
from machine_learning.models import BookPredictionRequest
from machine_learning.models import BookPredictionResponse
from database.database import get_db
from sqlalchemy.orm import Session
from auth.router import get_current_user

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get(
    "/features",
    description="Get data from books formatted for ml",
    response_model=list[BookMLResponse],
    status_code=200,
)
async def get_ml_books(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return ml_service.get_ml_books(db=db)


@router.get(
    "/training-data",
    description="Get training data for ML model",
    response_model=list[BookMLResponse],
    status_code=200,
)
async def get_training_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    random_state: int = 42,
):
    return ml_service.get_training_data(db=db, random_state=random_state)


@router.post(
    "/predictions/",
    description="Predict book rating based on features",
    response_model=BookPredictionResponse,
    status_code=200,
)
async def predictions(
    current_user: User = Depends(get_current_user),
    request: BookPredictionRequest = None,
):
    return ml_service.predict_book_rating(request)
