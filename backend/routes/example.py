from fastapi import APIRouter, HTTPException, Request

example_router = APIRouter()


@example_router.get("/")
async def home():
    return {"message": "FastAPI backend is running!"}


@example_router.post("/divideByTwo")
async def divide_by_two(request: Request):
    try:
        number = request.query_params.get("number")
        if not number:
            raise HTTPException(status_code=400, detail="Missing number argument")
        result = float(number) / 2
        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
