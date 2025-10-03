from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    books = relationship("Book", back_populates="category")