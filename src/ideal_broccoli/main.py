from fastapi import FastAPI
import auth.router as auth
import uvicorn

app = FastAPI(
    title="Ideal Broccoli",
    description="Excelente para gestão de livros.",
    version="0.1.0",
)   

base_prefix = "/api/v1" #TODO mudar para variavel de ambiente

app.include_router(auth.router, prefix=base_prefix, tags=["auth"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)