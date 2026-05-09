"""
Router smoke test：確認路由註冊與基本錯誤行為，不打外部 API。
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.chloride_ionized_concrete import ChlorideIonizedConcreteResponse
from app.models.earthquakes_building import EarthquakeBuildingResponse


_EARTHQUAKE_FIXTURE = {
    "result": {
        "limit": 1,
        "offset": 0,
        "count": 1,
        "sort": "",
        "results": [
            {
                "_id": 1,
                "_importdate": {
                    "date": "2025-10-09 17:41:10",
                    "timezone_type": 3,
                    "timezone": "Asia/Taipei",
                },
                "縣市別": "臺北市",
                "縣市別代碼": "63000",
                "行政區": "士林區",
                "行政區代碼（編碼）": "111",
                "建築地點": "天母北路87巷2號",
                "備註": "測試",
            }
        ],
    }
}

_CHLORIDE_FIXTURE = {
    "result": {
        "limit": 1,
        "offset": 0,
        "count": 1,
        "sort": "",
        "results": [
            {
                "_id": 1,
                "_importdate": {
                    "date": "2025-10-09 17:41:12",
                    "timezone_type": 3,
                    "timezone": "Asia/Taipei",
                },
                "縣市別": "臺北市",
                "縣市別代碼": "63000",
                "項次": "1",
                "主辦（管）單位": "臺北市政府衛生局",
                "行政區": "南港區",
                "行政區代碼（編碼）": "115",
                "建築物名稱": "忠孝院區醫療大樓",
                "使用目的": "醫院",
                "建築地點": "南港區同德路87號",
            }
        ],
    }
}


client = TestClient(app)


def test_health_endpoint():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_earthquake_buildings_returns_data():
    fake = EarthquakeBuildingResponse.model_validate(_EARTHQUAKE_FIXTURE)
    with patch(
        "app.services.earthquake_building._fetch_from_upstream",
        new=AsyncMock(return_value=fake),
    ):
        # 清掉 TTL 快取避免污染
        from app.services import earthquake_building as eb_service
        eb_service._cache.invalidate()

        r = client.get("/api/earthquake-buildings")
        assert r.status_code == 200
        body = r.json()
        assert body["result"]["count"] == 1


def test_earthquake_building_by_id_404():
    fake = EarthquakeBuildingResponse.model_validate(_EARTHQUAKE_FIXTURE)
    with patch(
        "app.services.earthquake_building._fetch_from_upstream",
        new=AsyncMock(return_value=fake),
    ):
        from app.services import earthquake_building as eb_service
        eb_service._cache.invalidate()

        r = client.get("/api/earthquake-buildings/999999")
        assert r.status_code == 404


def test_chloride_ionized_concrete_returns_data():
    fake = ChlorideIonizedConcreteResponse.model_validate(_CHLORIDE_FIXTURE)
    with patch(
        "app.services.chloride_ionized_concrete._fetch_from_upstream",
        new=AsyncMock(return_value=fake),
    ):
        from app.services import chloride_ionized_concrete as ci_service
        ci_service._cache.invalidate()

        r = client.get("/api/chloride-ionized-concrete")
        assert r.status_code == 200


def test_taipei_districts_geojson_served():
    r = client.get("/api/geojson/taipei-districts")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/geo+json")


def test_nearby_search_invalid_radius_rejected():
    r = client.get("/api/urban-update/nearby/search", params={
        "latitude": 25.0,
        "longitude": 121.5,
        "radius": 0.0,
    })
    assert r.status_code == 422
