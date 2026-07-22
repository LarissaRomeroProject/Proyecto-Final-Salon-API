from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_tables
from routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="API Salón de Belleza",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "mensaje": "API del Salón de Belleza funcionando correctamente"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
