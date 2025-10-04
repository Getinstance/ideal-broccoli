from fastapi import APIRouter

router = APIRouter(tags=["Auth"], prefix="/auth")

@router.get("/login")
def login():
    return {"access_token": "nope"}