import json
import time
from pathlib import Path

import httpx

from app.models.chloride_ionized_concrete import (
    ChlorideIonizedConcreteFormatResponse,
    ChlorideIonizedConcreteItemFormat,
    ChlorideIonizedConcreteResponse,
)
from data.util import get_geocode_from_arcgis

API_URL = "https://data.taipei/api/v1/dataset/15487e1f-a86e-4481-8ae9-3c331db5e3d4"
OUTPUT_PATH = Path(__file__).with_name("chloride_ionized_concrete_format.json")


def build_chloride_ionized_concrete_dataset() -> None:
    params = {"limit": 2000, "offset": 0, "scope": "resourceAquire"}
    response = httpx.get(API_URL, params=params, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    upstream = ChlorideIonizedConcreteResponse.model_validate(data)

    out_items: list[ChlorideIonizedConcreteItemFormat] = []
    for item in upstream.result.results:
        code = item.county + item.building_location
        coords = get_geocode_from_arcgis(code)
        if coords is None:
            longitude, latitude, geocoded = None, None, False
        else:
            longitude, latitude = coords
            geocoded = True

        out_items.append(
            ChlorideIonizedConcreteItemFormat(
                **item.model_dump(),
                longitude=longitude,
                latitude=latitude,
                geocoded=geocoded,
            )
        )
        print(f"Processed: {item.building_name} (geocoded={geocoded})")
        time.sleep(0.1)

    format_response = ChlorideIonizedConcreteFormatResponse(result=out_items)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            format_response.model_dump(),
            f,
            ensure_ascii=False,
            indent=4,
        )


if __name__ == "__main__":
    build_chloride_ionized_concrete_dataset()
