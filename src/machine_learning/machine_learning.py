import books.books as books_service
import os
from machine_learning.models import (
    BookMLResponse,
    BookPredictionRequest,
    BookPredictionResponse,
)
from sqlalchemy.orm import Session
from database.database import get_db
import pandas as pd
import pickle


def get_ml_books(db: Session = next(get_db())):
    books = books_service.get_all_books(db=db)
    books = [BookMLResponse.from_book(book) for book in books]
    return books


def get_training_data(db: Session = next(get_db()), random_state: int = 42):
    books = books_service.get_all_books(db=db)

    # Carrega os dados do banco de dados para um DataFrame do pandas
    df = pd.DataFrame(books)
    sample = df.sample(frac=0.7, random_state=random_state)
    return [BookMLResponse.from_book(book[1]) for book in sample.itertuples()]


def predict_book_rating(request: BookPredictionRequest = None):
    # Carregar modelo treinado (exemplo simplificado)

    with open(os.path.dirname(__file__) + "/ml_model.pkl", "rb") as f:
        model = pickle.load(f)

    # Preparar os dados de entrada
    input_data = [[request.price, request.category_id]]

    # Fazer a previsão
    predicted_rate = model.predict(input_data)[0]

    f.close()

    return BookPredictionResponse(predicted_rate=int(predicted_rate))
