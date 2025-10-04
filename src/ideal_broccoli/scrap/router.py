from fastapi import APIRouter, BackgroundTasks
from scrap import scrapinator
from categories import categories as categories_service
from categories import models as categories_models
from books import books as books_service
from books import models as books_models

router = APIRouter(tags=["Scrapping"], prefix="/scrap")

def background_scrap():
    result = scrapinator.extract_from_books_to_scrape() 
    
    for category in result:
        new_category = categories_service.add_category(categories_models.Category(name=category['name']))
        for book in category['books']:
            books_service.add_book(books_models.Book(
                title=book['title'],
                price=book['price'],
                rating=book['rating'],
                available=book['available'],
                image_url=book['image_url'],
                category_id=new_category.id
            ))

@router.get("/trigger", status_code=202, summary="Trigger the scrapping process")
def trigger_scrapping(background_tasks: BackgroundTasks):
    background_tasks.add_task(background_scrap)
    return {"message": "Scrapping process started in the background."}