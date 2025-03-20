from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared_utils.db.session import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    yield

    await close_db()
