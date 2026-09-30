from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.routes import authRouter
from src.utils import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("created tables")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    authRouter,
    prefix="/auth",
    tags=["auth"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}