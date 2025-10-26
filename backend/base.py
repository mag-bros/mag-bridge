from fastapi import FastAPI

from backend.routes import example_router

app = FastAPI()
app.include_router(example_router)
