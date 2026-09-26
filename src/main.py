from fastapi import FastAPI
from routers import router , session_router
app = FastAPI()

app.include_router(router)
app.include_router(session_router)