from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from auth.models import AccessToken, User
from dotenv import load_dotenv
import os

# Inicializa variáveis de ambiente
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "segredo_secreto_muito_secreto")
REFRESH_SECRET_KEY = os.getenv(
    "REFRESH_SECRET_KEY", "segredo_secreto_muito_mais_secreto"
)
ALGORITHM = os.getenv("SECRET_KEY", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
REFRESH_ACCESS_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_ACCESS_TOKEN_EXPIRE_DAYS", 14)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "bearer"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> tuple[str, int]:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=REFRESH_ACCESS_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({"exp": expire, "type": "refresh"})
    expires_at = int(expire.timestamp())
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expires_at


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError as e:
        print(f"Token inválido JWTError: {e}")
        return None


def generate_token(db, username: str, password: str) -> AccessToken:

    db_user = db.query(User).filter(User.username == username).first()

    # TODO Pensar numa exception personalizada
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": username})
    refresh_token, expires_in = create_refresh_token(data={"sub": username})

    return AccessToken(
        access_token=access_token, refresh_token=refresh_token, expires_in=expires_in
    )


def refresh_token(token: str) -> AccessToken:
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        access_token = create_access_token(data={"sub": username})
        refresh_token, expires_in = create_refresh_token(data={"sub": username})

        return AccessToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )
    except JWTError as e:
        print(f"Token inválido JWTError: {e}")
        return None


def register_user(db, username: str, password: str):

    db_user = db.query(User).filter(User.username == username).first()

    # TODO Pensar numa exception personalizada
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()
