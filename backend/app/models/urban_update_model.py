from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, computed_field


PolygonCoords = List[List[List[float]]]
MultiPolygonCoords = List[List[List[List[float]]]]


class UrbanRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: Optional[str] = Field(None, description="資料日期")
    title: Optional[str] = Field(None, description="案件名稱")
    area: Optional[float] = Field(None, description="面積")
    update_type: Optional[str] = Field(
        None, alias="updateType", description="更新地區類型"
    )
    announcement_date: Optional[str] = Field(
        None, alias="announcementDate", description="公告日期"
    )
    update_area_size: Optional[str] = Field(
        None, alias="updateAreaSize", description="更新地區面積"
    )
    coordinates: Optional[Union[PolygonCoords, MultiPolygonCoords]] = Field(
        None, description="地理座標：Polygon 為三層巢狀、MultiPolygon 為四層巢狀"
    )
    distance_km: Optional[float] = Field(
        None,
        description="與查詢座標的距離（公里）；僅 nearby search 端點會填入",
    )


class UrbanUpdateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(..., description="回傳狀態 (success / empty / error)")
    districts: str = Field(..., description="行政區名稱")
    records: List[UrbanRecord] = Field(default_factory=list, description="更新紀錄")

    @computed_field(description="紀錄數量（含同案件多次公告）")  # type: ignore[misc]
    @property
    def record_count(self) -> int:
        return len(self.records)

    @computed_field(description="不重複案件數（依 title 去重）")  # type: ignore[misc]
    @property
    def case_count(self) -> int:
        titles = {r.title for r in self.records if r.title}
        return len(titles)


class UrbanUpdateListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(..., description="回傳狀態 (success / empty / error)")
    data: List[UrbanUpdateResponse] = Field(default_factory=list)

    @computed_field(description="行政區數量")  # type: ignore[misc]
    @property
    def total_count(self) -> int:
        return len(self.data)
