from fastapi import APIRouter

from app.routers import (
    chloride_ionized_concrete,
    earthquake_buildings,
    geojson,
    health,
    urban_update,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(earthquake_buildings.router)
api_router.include_router(chloride_ionized_concrete.router)
api_router.include_router(geojson.router)
api_router.include_router(urban_update.router)

__all__ = ["api_router"]
