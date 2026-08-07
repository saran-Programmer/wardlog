from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from api.routes import router
from db.connection import close_driver, verify_connection
from db.postgres import create_tables
from discovery.eureka_registration import start_eureka_client, stop_eureka_client
from messaging.timesheet_consumer import start_timesheet_consumer, stop_timesheet_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    verify_connection()
    start_timesheet_consumer()
    await start_eureka_client()
    yield
    await stop_eureka_client()
    stop_timesheet_consumer()
    close_driver()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
