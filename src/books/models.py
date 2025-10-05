from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime
from pydantic import BaseModel
from categories.models import CategoryResponse


class BookResponse(BaseModel):
    id: int
    title: str
    price: float
    rating: int
    available: bool
    image_url: str
    category: CategoryResponse


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    rating = Column(Integer)  # 1-5 stars
    available = Column(Boolean, default=True)
    image_url = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.now)

    category = relationship("Category", back_populates="books")
