from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models._common import ImportDate


class EarthquakeBuildingItem(BaseModel):
    """地震建築物資料項目"""

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="_id", description="項目 ID")
    import_date: ImportDate = Field(alias="_importdate", description="匯入日期")
    county: str = Field(alias="縣市別", description="縣市別")
    county_code: str = Field(alias="縣市別代碼", description="縣市別代碼")
    district: str = Field(alias="行政區", description="行政區")
    district_code: str = Field(alias="行政區代碼（編碼）", description="行政區代碼")
    building_location: str = Field(alias="建築地點", description="建築地點")
    note: Optional[str] = Field(default=None, alias="備註", description="備註")


class EarthquakeBuildingItemGeoList(BaseModel):
    """地震建築物資料項目經緯度列表"""

    longitude: Optional[float] = Field(default=None, description="經度")
    latitude: Optional[float] = Field(default=None, description="緯度")
    geocoded: bool = Field(default=False, description="是否成功取得經緯度")


class EarthquakeBuildingItemFormat(EarthquakeBuildingItem):
    """地震建築物資料項目（含經緯度）"""

    geo: list[EarthquakeBuildingItemGeoList] = Field(description="經緯度資訊")


class EarthquakeBuildingFormatResponse(BaseModel):
    result: List[EarthquakeBuildingItemFormat] = Field(description="查詢結果列表")


class EarthquakeBuildingResult(BaseModel):
    """地震建築物查詢結果"""

    limit: int = Field(description="查詢限制數量")
    offset: int = Field(description="查詢偏移量")
    count: int = Field(description="總筆數")
    sort: str = Field(description="排序方式")
    results: List[EarthquakeBuildingItem] = Field(description="查詢結果列表")


class EarthquakeBuildingResponse(BaseModel):
    """地震建築物 API 回應"""

    result: EarthquakeBuildingResult = Field(description="查詢結果")
