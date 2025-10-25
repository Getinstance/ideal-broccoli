from fastapi import FastAPI
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
import auth.router as auth
import auth.models as auth_models
import books.router as books
import books.models as books_models
import categories.router as categories
import categories.models as categories_models
import stats.router as stats
import scrap.router as scrap
import machine_learning.router as machine_learning
import uvicorn
from sqlalchemy.orm import Session
from database.database import engine
from database.database import get_db
from database.database import is_database_online
from core.metrics import make_asgi_sec_app

# from prometheus_fastapi_instrumentator import Instrumentator

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

# Prometheus
# Instrumentator().instrument(app).expose(app)
# Usando o endpoint /metrics com autenticação básica
# ao inves do padrão /metrics do Instrumentator
metrics_app = make_asgi_sec_app()
app.mount("/metrics", metrics_app)

# Inclui base routers
base_prefix = "/api/v1"
app.include_router(auth.router, prefix=base_prefix)
app.include_router(books.router, prefix=base_prefix)
app.include_router(categories.router, prefix=base_prefix)
app.include_router(scrap.router, prefix=base_prefix)
app.include_router(stats.router, prefix=base_prefix)
app.include_router(machine_learning.router, prefix=base_prefix)


# Health check endpoint
@app.get("/", include_in_schema=False)
@app.get(
    "/health",
    tags=["Health"],
    description="Health check endpoint",
    openapi_extra={
        "responses": {
            200: {
                "description": "Service is healthy",
                "content": {"application/json": {"example": {"status": "ok"}}},
            }
        }
    },
)
async def health_check(db: Session = Depends(get_db)):
    return (
        {"status": "ok"}
        if await is_database_online(db)
        else {"status": "NOK", "reason": "database offline"}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
