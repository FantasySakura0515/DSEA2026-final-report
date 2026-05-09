from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.handlers.chloride_ionized_concrete_geojson import (
    ChlorideIonizedConcreteGeoJSONHandler,
)
from app.handlers.earthquake_building_geojson import EarthquakeBuildingGeoJSONHandler
from app.models.chloride_ionized_concrete_geojson import (
    ChlorideIonizedConcreteFeatureCollection,
)
from app.models.earthquake_building_geojson import EarthquakeBuildingFeatureCollection

router = APIRouter(prefix="/geojson")
earthquake_handler = EarthquakeBuildingGeoJSONHandler()
chloride_handler = ChlorideIonizedConcreteGeoJSONHandler()


@router.get(
    "/earthquake-buildings",
    response_model=EarthquakeBuildingFeatureCollection,
    tags=["GeoJSON - 地震建築物"],
)
async def get_earthquake_buildings_geojson():
    return await earthquake_handler.fetch_geojson()


@router.get(
    "/chloride-ionized-concrete",
    response_model=ChlorideIonizedConcreteFeatureCollection,
    tags=["GeoJSON - 海砂屋"],
)
async def get_chloride_ionized_concrete_geojson():
    return await chloride_handler.fetch_geojson()


@router.get("/taipei-districts", tags=["GeoJSON - 行政區界"])
async def get_taipei_districts_geojson():
    path = settings.public_dir / "taipei-districts.geojson"
    if not path.exists():
        raise HTTPException(
            status_code=404, detail="台北市行政區 GeoJSON 檔案不存在"
        )
    return FileResponse(path, media_type="application/geo+json")
