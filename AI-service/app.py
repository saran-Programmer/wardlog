from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from api.routes import router
from db.connection import close_driver, verify_connection
from db.postgres import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    verify_connection()
    yield
    close_driver()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
