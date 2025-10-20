from fastapi import FastAPI
from .routes import register_routes
import uvicorn

def app():
    app = FastAPI()
    register_routes(app)
    return app

if __name__ == "__main__":
    app = app()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
