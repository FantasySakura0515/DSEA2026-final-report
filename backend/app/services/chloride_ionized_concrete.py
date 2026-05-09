import os

import httpx
from fastapi import HTTPException

from app.models.chloride_ionized_concrete import ChlorideIonizedConcreteResponse
from app.utils.cache import AsyncTTLCache

API_URL = "https://data.taipei/api/v1/dataset/15487e1f-a86e-4481-8ae9-3c331db5e3d4"
UPSTREAM_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
_CACHE_TTL = float(os.getenv("UPSTREAM_CACHE_TTL", "300"))
_cache: AsyncTTLCache[ChlorideIonizedConcreteResponse] = AsyncTTLCache(_CACHE_TTL)


async def _fetch_from_upstream() -> ChlorideIonizedConcreteResponse:
    params = {"limit": 2000, "offset": 0, "scope": "resourceAquire"}
    try:
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
            response = await client.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="上游資料源回應逾時，請稍後再試") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"上游資料源錯誤：{exc}") from exc

    return ChlorideIonizedConcreteResponse.model_validate(data)


async def fetch_chloride_ionized_concrete() -> ChlorideIonizedConcreteResponse:
    return await _cache.get(_fetch_from_upstream)
