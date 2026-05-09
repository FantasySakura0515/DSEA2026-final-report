from pydantic import BaseModel, Field


class ImportDate(BaseModel):
    """匯入日期資訊"""

    date: str = Field(description="匯入日期時間")
    timezone_type: int = Field(description="時區類型")
    timezone: str = Field(description="時區")
