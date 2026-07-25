from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_tables
from routers import auth, salones
from routers import horarios
from routers import reservas
from routers import servicios

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="API de Salones de Belleza",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(auth.router)
app.include_router(salones.router)
app.include_router(servicios.router)
app.include_router(horarios.router)
app.include_router(reservas.router)

@app.get("/")
def root():
    return {
        "mensaje": "API del Salón de Belleza funcionando correctamente"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }