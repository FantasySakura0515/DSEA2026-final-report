from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from app.models._common import ImportDate


class EarthquakeBuildingProperties(BaseModel):
    """地震建築物屬性"""

    id: int = Field(description="項目 ID")
    import_date: ImportDate = Field(description="匯入日期")
    county: str = Field(description="縣市別")
    county_code: str = Field(description="縣市別代碼")
    district: str = Field(description="行政區")
    district_code: str = Field(description="行政區代碼")
    building_location: str = Field(description="建築地點")
    note: Optional[str] = Field(default=None, description="備註")
    geocoded_count: int = Field(
        default=0, description="該筆原始資料成功取得經緯度的點位數量"
    )


class EarthquakeBuildingGeometry(BaseModel):
    """GeoJSON 幾何資訊"""

    type: Literal["MultiPoint"] = "MultiPoint"
    coordinates: List[List[float]] = Field(
        default_factory=list,
        description="座標列表 [[經度, 緯度], ...]，僅包含成功取得經緯度的點位",
    )


class EarthquakeBuildingFeature(BaseModel):
    """地震建築物 GeoJSON Feature"""

    type: Literal["Feature"] = "Feature"
    properties: EarthquakeBuildingProperties
    geometry: EarthquakeBuildingGeometry


class EarthquakeBuildingFeatureCollection(BaseModel):
    """地震建築物 GeoJSON FeatureCollection"""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[EarthquakeBuildingFeature]
