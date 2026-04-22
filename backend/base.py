from fastapi import FastAPI
from backend.routes import submit_router

app = FastAPI()
app.include_router(submit_router)

@app.get("/health")
def health():
    return {"status": "ok"}
