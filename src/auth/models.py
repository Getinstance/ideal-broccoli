from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, DateTime
from database.database import Base
from datetime import datetime

class UserRequest(BaseModel):
    username: EmailStr
    password: str

class UserResponse(BaseModel):
    message: str

class AccessToken(BaseModel):
    token_type: str = "bearer"
    access_token: str
    refresh_token: str
    expires_in: int  # in seconds

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)