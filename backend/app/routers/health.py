from fastapi import APIRouter

router = APIRouter(tags=["系統"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
    }
