from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from core.log import get_logger
import os


logger = get_logger(__name__)

# Inicializa variáveis de ambiente
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://localhost/ideal_broccoli"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def is_database_online(db):
    try:
        db.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, TimeoutError) as e:
        logger.error(f"Database is offline {e}")
        return False
