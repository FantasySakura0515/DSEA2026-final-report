from fastapi import APIRouter, Query

from app.handlers.urban_update import UrbanUpdateHandler
from app.models.urban_update_model import UrbanUpdateListResponse, UrbanUpdateResponse

router = APIRouter(prefix="/urban-update", tags=["都市更新"])
handler = UrbanUpdateHandler()


@router.get("", response_model=UrbanUpdateListResponse)
async def urban_update():
    return handler.get_urban_updates()


@router.get("/nearby/search", response_model=UrbanUpdateListResponse)
async def urban_update_nearby(
    latitude: float = Query(..., description="緯度", examples=[25.0330], ge=-90, le=90),
    longitude: float = Query(..., description="經度", examples=[121.5654], ge=-180, le=180),
    radius: float = Query(1.0, description="搜索半徑（公里）", ge=0.1, le=50),
):
    return handler.get_nearby_updates(latitude, longitude, radius)


@router.get("/{district}", response_model=UrbanUpdateResponse)
async def urban_update_by_district(district: str):
    return handler.get_urban_update_by_district(district)
