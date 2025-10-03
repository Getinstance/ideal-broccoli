from fastapi import APIRouter
from scrap import scrapinator

router = APIRouter(tags=["Scrapping"], prefix="/scrap")

@router.get("/trigger", status_code=202, summary="Trigger the scrapping process")
def trigger_scrapping():
    scrapinator.extract_from_books_to_scrape() 
    return {"message": "Scrapping process finished."}