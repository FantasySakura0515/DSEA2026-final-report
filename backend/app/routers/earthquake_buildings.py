from typing import List

from fastapi import APIRouter, HTTPException

from app.handlers.earthquake_building import EarthquakeBuildingHandler
from app.models.earthquakes_building import (
    EarthquakeBuildingItem,
    EarthquakeBuildingResponse,
)

router = APIRouter(prefix="/earthquake-buildings", tags=["地震建築物"])
handler = EarthquakeBuildingHandler()


@router.get(
    "",
    response_model=EarthquakeBuildingResponse,
    response_model_by_alias=False,
)
async def get_earthquake_buildings():
    return await handler.fetch_buildings()


@router.get(
    "/{building_id}",
    response_model=EarthquakeBuildingItem,
    response_model_by_alias=False,
)
async def get_earthquake_building_by_id(building_id: int):
    result = await handler.fetch_building_by_id(building_id)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"查無 ID 為 {building_id} 的地震建築物"
        )
    return result


@router.get(
    "/county/{county}",
    response_model=List[EarthquakeBuildingItem],
    response_model_by_alias=False,
)
async def get_earthquake_buildings_by_county(county: str):
    result = await handler.fetch_buildings_by_county(county)
    if not result:
        raise HTTPException(status_code=404, detail=f"查無 {county} 的地震建築物資料")
    return result


@router.get(
    "/district/{county}/{district}",
    response_model=List[EarthquakeBuildingItem],
    response_model_by_alias=False,
)
async def get_earthquake_buildings_by_district(county: str, district: str):
    result = await handler.fetch_buildings_by_district(county, district)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"查無 {county}{district} 的地震建築物資料"
        )
    return result
