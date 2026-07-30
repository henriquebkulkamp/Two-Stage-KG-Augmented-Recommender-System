from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.endpoints import router
from services import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events for database connections.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    database.init_db()
    yield
    database.close_db()


app = FastAPI(
    title="RecSys Hybrid API",
    description="API híbrida com busca vetorial (Neo4j) e consulta indexada em O(1) (PostgreSQL)",
    lifespan=lifespan,
)

app.include_router(router)