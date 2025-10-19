from fastapi import APIRouter, Request, HTTPException

def register_routes(app):
    router = APIRouter()

    @router.get("/")
    async def home():
        return {"message": "FastAPI backend is running!"}

    @router.post("/divideByTwo")
    async def divide_by_two(request: Request):
        try:
            number = request.query_params.get("number")
            if not number:
                raise HTTPException(status_code=400, detail="Missing number argument")
            result = float(number) / 2
            return {"result": str(result)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router)
