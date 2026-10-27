import socket
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from sqlalchemy import text

from app.database import Base, engine
from app.customers.router import router as customers_router
from app.orders.router import router as orders_router
from app.products.router import router as products_router

# Importar los modelos registra las tablas en Base.metadata
import app.customers.models  # noqa: F401
import app.orders.models  # noqa: F401
import app.products.models  # noqa: F401

HOSTNAME = socket.gethostname()  # en Docker = id del contenedor


@asynccontextmanager
async def lifespan(_: FastAPI):
    with engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            # Varias réplicas arrancan a la vez: el lock evita que creen las
            # tablas al mismo tiempo. Se libera solo al terminar la transacción.
            conn.execute(text("SELECT pg_advisory_xact_lock(42)"))
        Base.metadata.create_all(conn)
    yield


app = FastAPI(title="Mini e-commerce (UT3 TFU)", lifespan=lifespan)


@app.middleware("http")
async def add_served_by(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Served-By"] = HOSTNAME
    return response


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok", "served_by": HOSTNAME}


app.include_router(products_router)
app.include_router(customers_router)
app.include_router(orders_router)
