from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models._common import ImportDate


class ChlorideIonizedConcreteItem(BaseModel):
    """氯離子混凝土建築物資料項目"""

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="_id", description="項目 ID")
    import_date: ImportDate = Field(alias="_importdate", description="匯入日期")
    county: str = Field(alias="縣市別", description="縣市別")
    county_code: str = Field(alias="縣市別代碼", description="縣市別代碼")
    item_number: str = Field(alias="項次", description="項次")
    organizer: str = Field(alias="主辦（管）單位", description="主辦(管)單位")
    district: str = Field(alias="行政區", description="行政區")
    district_code: str = Field(alias="行政區代碼（編碼）", description="行政區代碼")
    building_name: str = Field(alias="建築物名稱", description="建築物名稱")
    purpose: str = Field(alias="使用目的", description="使用目的")
    building_location: str = Field(alias="建築地點", description="建築地點")


class ChlorideIonizedConcreteItemFormat(ChlorideIonizedConcreteItem):
    """氯離子混凝土建築物資料項目（含經緯度）"""

    longitude: Optional[float] = Field(default=None, description="經度")
    latitude: Optional[float] = Field(default=None, description="緯度")
    geocoded: bool = Field(default=False, description="是否成功取得經緯度")


class ChlorideIonizedConcreteFormatResponse(BaseModel):
    result: List[ChlorideIonizedConcreteItemFormat] = Field(description="查詢結果列表")


class ChlorideIonizedConcreteResult(BaseModel):
    """氯離子混凝土查詢結果"""

    limit: int = Field(description="查詢限制數量")
    offset: int = Field(description="查詢偏移量")
    count: int = Field(description="總筆數")
    sort: str = Field(description="排序方式")
    results: List[ChlorideIonizedConcreteItem] = Field(description="查詢結果列表")


class ChlorideIonizedConcreteResponse(BaseModel):
    """氯離子混凝土 API 回應"""

    result: ChlorideIonizedConcreteResult = Field(description="查詢結果")
