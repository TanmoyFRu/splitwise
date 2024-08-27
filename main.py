from typing import AsyncIterator

from fastapi import FastAPI
from sqlmodel import SQLModel

from api import router as api_router
from core import engine


async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
