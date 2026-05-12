from fastapi import FastAPI
from backend.routes import experiment_router

app = FastAPI()
app.include_router(experiment_router)

@app.get("/health")
def health():
    return {"status": "ok"}
