from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.handlers.chloride_ionized_concrete import ChlorideIonizedConcreteHandler
from app.models.chloride_ionized_concrete import (
    ChlorideIonizedConcreteItem,
    ChlorideIonizedConcreteResponse,
)

router = APIRouter(prefix="/chloride-ionized-concrete", tags=["海砂屋"])
handler = ChlorideIonizedConcreteHandler()


@router.get(
    "",
    response_model=ChlorideIonizedConcreteResponse,
    response_model_by_alias=False,
)
async def get_chloride_ionized_concrete():
    return await handler.fetch_buildings()


@router.get(
    "/county/{county}",
    response_model=List[ChlorideIonizedConcreteItem],
    response_model_by_alias=False,
)
async def get_chloride_ionized_concrete_by_county(county: str):
    result = await handler.fetch_buildings_by_county(county)
    if not result:
        raise HTTPException(status_code=404, detail=f"查無 {county} 的海砂屋建築物資料")
    return result


@router.get(
    "/district/{county}/{district}",
    response_model=List[ChlorideIonizedConcreteItem],
    response_model_by_alias=False,
)
async def get_chloride_ionized_concrete_by_district(county: str, district: str):
    result = await handler.fetch_buildings_by_district(county, district)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"查無 {county}{district} 的海砂屋建築物資料"
        )
    return result


@router.get(
    "/purpose",
    response_model=List[ChlorideIonizedConcreteItem],
    response_model_by_alias=False,
)
async def get_chloride_ionized_concrete_by_purpose(purpose: str = Query(...)):
    result = await handler.fetch_buildings_by_purpose(purpose)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"查無使用目的為「{purpose}」的海砂屋建築物資料",
        )
    return result


@router.get(
    "/organizer",
    response_model=List[ChlorideIonizedConcreteItem],
    response_model_by_alias=False,
)
async def get_chloride_ionized_concrete_by_organizer(organizer: str = Query(...)):
    result = await handler.fetch_buildings_by_organizer(organizer)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"查無主辦單位為「{organizer}」的海砂屋建築物資料",
        )
    return result


@router.get(
    "/{building_id}",
    response_model=ChlorideIonizedConcreteItem,
    response_model_by_alias=False,
)
async def get_chloride_ionized_concrete_by_id(building_id: int):
    result = await handler.fetch_building_by_id(building_id)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"查無 ID 為 {building_id} 的海砂屋建築物"
        )
    return result
