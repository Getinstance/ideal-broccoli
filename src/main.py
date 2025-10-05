from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth.router as auth
import auth.models as auth_models
import books.router as books
import books.models as books_models
import categories.router as categories
import categories.models as categories_models
import scrap.router as scrap
import uvicorn
from database.database import engine

# Importa os modelos para criar as tabelas
auth_models.Base.metadata.create_all(bind=engine)
books_models.Base.metadata.create_all(bind=engine)
categories_models.Base.metadata.create_all(bind=engine)

# Setup FastAPI app
app = FastAPI(
    title="Ideal Broccoli",
    description="Excelente para gestão de livros.",
    version="0.1.0",    
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui base routers
base_prefix = "/api/v1" #TODO mudar para variavel de ambiente
app.include_router(auth.router, prefix=base_prefix)
app.include_router(books.router, prefix=base_prefix)
app.include_router(categories.router, prefix=base_prefix)
app.include_router(scrap.router, prefix=base_prefix)

# Health check endpoint
@app.get("/health", tags=["Health"], description="Health check endpoint", openapi_extra={
    "responses": {
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "ok"}
                }
            }
        }
    }
})
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)