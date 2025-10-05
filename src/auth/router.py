from fastapi import APIRouter
from fastapi.params import Depends
from auth import auth as auth_service
from auth.models import UserRequest, UserResponse, AccessToken
from database.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["Auth"], prefix="/auth")

@router.post("/login", response_model=AccessToken, description="User login to obtain access and refresh tokens")
def login(db: Session = Depends(get_db), user: UserRequest = None) -> AccessToken:
    accessToken = auth_service.generate_token(db, user.username, user.password)
    return accessToken

@router.post("/register", response_model=UserResponse, status_code=201, description="Register a new user")
def register(db: Session = Depends(get_db), user: UserRequest = None) -> UserResponse:
    auth_service.register_user(db, user.username, user.password)
    return UserResponse(message="User registered successfully")

@router.post("/refresh")
def token_refresh():
    return {"token": "nope"}