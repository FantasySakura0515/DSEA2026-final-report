"""
驗證 UrbanUpdateService 的核心行為：
- _create_polygon 對 Polygon / MultiPolygon / 壞資料的處理
- 行政區查詢命中與不命中
- nearby search 的 distance_km 與排序
"""

import json

from app.services.urban_update_service import UrbanUpdateService, _create_polygon


SAMPLE_POLYGON = [[[121.50, 25.00], [121.51, 25.00], [121.51, 25.01], [121.50, 25.01], [121.50, 25.00]]]
SAMPLE_MULTIPOLYGON = [
    [[[121.52, 25.02], [121.53, 25.02], [121.53, 25.03], [121.52, 25.03], [121.52, 25.02]]],
    [[[121.60, 25.10], [121.61, 25.10], [121.61, 25.11], [121.60, 25.11], [121.60, 25.10]]],
]


def test_create_polygon_handles_polygon_depth_3():
    geom = _create_polygon(SAMPLE_POLYGON)
    assert geom is not None
    assert geom.geom_type == "Polygon"


def test_create_polygon_handles_multipolygon_depth_4():
    geom = _create_polygon(SAMPLE_MULTIPOLYGON)
    assert geom is not None
    assert geom.geom_type == "MultiPolygon"
    assert len(list(geom.geoms)) == 2


def test_create_polygon_returns_none_for_garbage():
    assert _create_polygon(None) is None
    assert _create_polygon([]) is None
    assert _create_polygon("not a list") is None
    assert _create_polygon([[1, 2]]) is None


def _service_with(tmp_path, payload):
    file = tmp_path / "urban-update.json"
    file.write_text(json.dumps(payload), encoding="utf-8")
    svc = UrbanUpdateService()
    svc.file_path = file
    svc._raw_data = None
    svc._tree = None
    return svc


def test_get_urban_update_by_district_hit_and_miss(tmp_path):
    svc = _service_with(
        tmp_path,
        [
            {"districts": "大安區", "records": [{"title": "案A"}]},
            {"districts": "信義區", "records": [{"title": "案B"}]},
        ],
    )
    hit = svc.get_urban_update_by_district("大安區")
    assert hit.status == "success"
    assert hit.record_count == 1

    miss = svc.get_urban_update_by_district("不存在區")
    assert miss.status == "empty"
    assert miss.records == []


def test_record_count_and_case_count_dedup_by_title(tmp_path):
    svc = _service_with(
        tmp_path,
        [
            {
                "districts": "大安區",
                "records": [
                    {"title": "案A"},
                    {"title": "案A"},
                    {"title": "案B"},
                    {"title": None},
                ],
            }
        ],
    )
    resp = svc.get_urban_update_by_district("大安區")
    assert resp.record_count == 4
    assert resp.case_count == 2


def test_search_nearby_inside_polygon_distance_zero(tmp_path):
    svc = _service_with(
        tmp_path,
        [
            {
                "districts": "大安區",
                "records": [{"title": "案A", "coordinates": SAMPLE_POLYGON}],
            }
        ],
    )
    inside_lon, inside_lat = 121.505, 25.005
    results = svc.search_nearby_updates(inside_lat, inside_lon, search_radius_km=0.5)
    assert len(results) == 1
    record, district, distance = results[0]
    assert district == "大安區"
    assert distance == 0.0
    assert record.distance_km == 0.0


def test_search_nearby_far_returns_empty(tmp_path):
    svc = _service_with(
        tmp_path,
        [
            {
                "districts": "大安區",
                "records": [{"title": "案A", "coordinates": SAMPLE_POLYGON}],
            }
        ],
    )
    # 距離超過 100 公里的點
    results = svc.search_nearby_updates(20.0, 110.0, search_radius_km=1.0)
    assert results == []
