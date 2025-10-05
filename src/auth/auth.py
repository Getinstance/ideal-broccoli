from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from auth.models import AccessToken, User

SECRET_KEY = "segredo_secreto_muito_secreto"  # TODO Colocar em variavel de ambiente.
REFRESH_SECRET_KEY = "segredo_secreto_muito_mais_secreto"  # TODO Colocar em variavel de ambiente.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_ACCESS_TOKEN_EXPIRE_DAYS = 14

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "bearer"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, int]:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=REFRESH_ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type" : "refresh"})
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
    except JWTError:
        return None

def generate_token(db, username: str, password: str) -> AccessToken:
    
    db_user = db.query(User).filter(User.username == username).first()

    # TODO Pensar numa exception personalizada
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": username})
    refresh_token, expires_in = create_refresh_token(data={"sub": username})

    return AccessToken(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in
    )

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
    