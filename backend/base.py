from fastapi import FastAPI

from backend.routes import math_router
from backend.routes import files_router

app = FastAPI()
app.include_router(math_router)
app.include_router(files_router)


@app.get("/health")
def health():
    return {"status": "ok"}
