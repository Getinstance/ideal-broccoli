from fastapi import APIRouter

router = APIRouter()

@router.get("/login")
def login():
    return {"access_token": "nope"}