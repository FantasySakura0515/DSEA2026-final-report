import json
from typing import List

from app.config import settings
from app.models._common import ImportDate
from app.models.chloride_ionized_concrete_geojson import (
    ChlorideIonizedConcreteFeature,
    ChlorideIonizedConcreteFeatureCollection,
    ChlorideIonizedConcreteGeometry,
    ChlorideIonizedConcreteProperties,
)


JSON_FILE_PATH = settings.data_dir / "chloride_ionized_concrete_format.json"


def _is_valid_coord(lon, lat) -> bool:
    if lon is None or lat is None:
        return False
    try:
        lon_f, lat_f = float(lon), float(lat)
    except (TypeError, ValueError):
        return False
    return not (lon_f == 0.0 and lat_f == 0.0)


async def load_chloride_ionized_concrete_geojson() -> (
    ChlorideIonizedConcreteFeatureCollection
):
    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    features: List[ChlorideIonizedConcreteFeature] = []

    for item in data["result"]:
        lon = item.get("longitude")
        lat = item.get("latitude")
        # 兼容舊格式（無 geocoded 欄位）：以 (0,0) 為哨兵判定
        geocoded = item.get("geocoded")
        if geocoded is None:
            geocoded = _is_valid_coord(lon, lat)

        properties = ChlorideIonizedConcreteProperties(
            id=item["id"],
            import_date=ImportDate(**item["import_date"]),
            county=item["county"],
            county_code=item["county_code"],
            item_number=item["item_number"],
            organizer=item["organizer"],
            district=item["district"],
            district_code=item["district_code"],
            building_name=item["building_name"],
            purpose=item["purpose"],
            building_location=item["building_location"],
            geocoded=bool(geocoded),
        )

        coords = [float(lon), float(lat)] if geocoded else None
        geometry = ChlorideIonizedConcreteGeometry(coordinates=coords)

        features.append(
            ChlorideIonizedConcreteFeature(properties=properties, geometry=geometry)
        )

    return ChlorideIonizedConcreteFeatureCollection(features=features)
