from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="URL Shortner"
)

app.include_router(router)

