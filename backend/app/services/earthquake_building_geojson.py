import json
from typing import List

from app.config import settings
from app.models._common import ImportDate
from app.models.earthquake_building_geojson import (
    EarthquakeBuildingFeature,
    EarthquakeBuildingFeatureCollection,
    EarthquakeBuildingGeometry,
    EarthquakeBuildingProperties,
)


JSON_FILE_PATH = settings.data_dir / "earthquake_building_format.json"


def _is_valid_coord(lon, lat) -> bool:
    if lon is None or lat is None:
        return False
    try:
        lon_f, lat_f = float(lon), float(lat)
    except (TypeError, ValueError):
        return False
    return not (lon_f == 0.0 and lat_f == 0.0)


async def load_earthquake_buildings_geojson() -> EarthquakeBuildingFeatureCollection:
    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    features: List[EarthquakeBuildingFeature] = []

    for item in data["result"]:
        coordinates = []
        for geo in item.get("geo", []):
            lon = geo.get("longitude")
            lat = geo.get("latitude")
            geocoded = geo.get("geocoded")
            if geocoded is None:
                geocoded = _is_valid_coord(lon, lat)
            if geocoded:
                coordinates.append([float(lon), float(lat)])

        properties = EarthquakeBuildingProperties(
            id=item["id"],
            import_date=ImportDate(**item["import_date"]),
            county=item["county"],
            county_code=item["county_code"],
            district=item["district"],
            district_code=item["district_code"],
            building_location=item["building_location"],
            note=item.get("note"),
            geocoded_count=len(coordinates),
        )

        geometry = EarthquakeBuildingGeometry(coordinates=coordinates)

        features.append(
            EarthquakeBuildingFeature(properties=properties, geometry=geometry)
        )

    return EarthquakeBuildingFeatureCollection(features=features)
