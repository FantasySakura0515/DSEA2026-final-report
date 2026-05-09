import json
import logging
from math import cos, radians
from typing import List, Tuple

from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.strtree import STRtree

from app.config import settings
from app.models.urban_update_model import (
    UrbanRecord,
    UrbanUpdateListResponse,
    UrbanUpdateResponse,
)
from app.utils.geo import calculate_distance_km, radius_to_latitude_degrees

logger = logging.getLogger(__name__)


def _coord_depth(coords) -> int:
    depth = 0
    x = coords
    while isinstance(x, list) and x:
        depth += 1
        x = x[0]
    return depth


def _create_polygon(coords) -> Polygon | MultiPolygon | None:
    """根據 GeoJSON 風格的座標建立 Shapely 幾何。

    Polygon 為三層巢狀（rings → points → [lon, lat]），
    MultiPolygon 為四層巢狀（polygons → rings → points → [lon, lat]）。
    """
    if not coords or not isinstance(coords, list):
        return None

    depth = _coord_depth(coords)
    try:
        if depth == 3:
            return Polygon(coords[0])
        if depth == 4:
            polys = [Polygon(p[0]) for p in coords if p and p[0]]
            return MultiPolygon(polys) if polys else None
    except (ValueError, TypeError) as exc:
        logger.warning("Failed to build polygon (depth=%s): %s", depth, exc)
        return None

    logger.warning("Unsupported coordinate depth: %s", depth)
    return None


class UrbanUpdateService:
    """都市更新資料服務。

    每個 instance 會在第一次需要空間查詢時建立 STRtree 索引並快取，
    避免後續請求重複讀取 7MB JSON。
    """

    def __init__(self):
        self.file_path = settings.public_dir / "urban-update.json"
        self._raw_data: list | None = None
        self._geometries: list[Polygon | MultiPolygon] = []
        self._tree: STRtree | None = None
        self._record_index: dict[int, tuple[str, dict]] = {}

    def _load_raw(self) -> list:
        if self._raw_data is not None:
            return self._raw_data
        if not self.file_path.exists():
            self._raw_data = []
            return self._raw_data
        with open(self.file_path, "r", encoding="utf-8") as f:
            self._raw_data = json.load(f)
        return self._raw_data

    def _ensure_tree(self) -> None:
        if self._tree is not None:
            return
        data = self._load_raw()
        geometries: list[Polygon | MultiPolygon] = []
        record_index: dict[int, tuple[str, int]] = {}

        for district_data in data:
            district = district_data.get("districts", "未知區")
            records = district_data.get("records", [])
            for record_idx, record in enumerate(records):
                polygon = _create_polygon(record.get("coordinates"))
                if polygon is None or polygon.is_empty:
                    continue
                geom_idx = len(geometries)
                geometries.append(polygon)
                record_index[geom_idx] = (district, record)

        self._geometries = geometries
        self._record_index = record_index
        self._tree = STRtree(geometries) if geometries else None

    def get_urban_updates(self) -> UrbanUpdateListResponse:
        """取得所有都市更新資料"""
        data = self._load_raw()
        responses = [
            UrbanUpdateResponse(
                status="success",
                districts=item.get("districts", "未知區"),
                records=item.get("records", []),
            )
            for item in data
        ]
        return UrbanUpdateListResponse(
            status="success" if data else "empty",
            data=responses,
        )

    def get_urban_update_by_district(self, district: str) -> UrbanUpdateResponse:
        """根據行政區取得都市更新資料"""
        data = self._load_raw()
        for record in data:
            if record.get("districts") == district:
                return UrbanUpdateResponse(
                    status="success",
                    districts=record.get("districts", district),
                    records=record.get("records", []),
                )
        return UrbanUpdateResponse(status="empty", districts=district, records=[])

    def search_nearby_updates(
        self, latitude: float, longitude: float, search_radius_km: float = 1.0
    ) -> List[Tuple[UrbanRecord, str, float]]:
        """搜索指定座標附近的都市更新案件。

        Returns:
            List of (record, district, distance_km), 已依距離由近至遠排序。
        """
        self._ensure_tree()
        if self._tree is None:
            return []

        search_point = Point(longitude, latitude)
        lat_offset = radius_to_latitude_degrees(search_radius_km)
        lon_offset = lat_offset / cos(radians(latitude))
        search_box = box(
            longitude - lon_offset,
            latitude - lat_offset,
            longitude + lon_offset,
            latitude + lat_offset,
        )

        results: list[tuple[UrbanRecord, str, float]] = []
        for geom_idx in self._tree.query(search_box):
            geom_idx = int(geom_idx)
            polygon = self._geometries[geom_idx]
            district, record_data = self._record_index[geom_idx]

            if polygon.contains(search_point):
                distance_km = 0.0
            else:
                distance_km = self._point_to_polygon_distance_km(
                    polygon, search_point, latitude, longitude
                )

            if distance_km <= search_radius_km:
                record = UrbanRecord(**record_data)
                record.distance_km = round(distance_km, 4)
                results.append((record, district, distance_km))

        return sorted(results, key=lambda x: x[2])

    @staticmethod
    def _point_to_polygon_distance_km(
        polygon: Polygon | MultiPolygon,
        search_point: Point,
        latitude: float,
        longitude: float,
    ) -> float:
        polys = (
            [polygon] if isinstance(polygon, Polygon) else list(polygon.geoms)
        )
        min_distance = float("inf")
        for poly in polys:
            if poly.is_empty:
                continue
            nearest = poly.exterior.interpolate(poly.exterior.project(search_point))
            dist = calculate_distance_km(
                latitude, longitude, nearest.y, nearest.x
            )
            min_distance = min(min_distance, dist)
        return min_distance

    def get_nearby_updates(
        self, latitude: float, longitude: float, search_radius_km: float = 1.0
    ) -> UrbanUpdateListResponse:
        """取得指定座標附近的都市更新資料,按行政區分組"""
        nearby = self.search_nearby_updates(latitude, longitude, search_radius_km)

        district_records: dict[str, list[UrbanRecord]] = {}
        for record, district, _ in nearby:
            district_records.setdefault(district, []).append(record)

        responses = [
            UrbanUpdateResponse(status="success", districts=district, records=records)
            for district, records in district_records.items()
        ]

        return UrbanUpdateListResponse(
            status="success" if responses else "empty", data=responses
        )
