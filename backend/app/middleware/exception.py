import traceback

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings


async def exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        if isinstance(exc, (StarletteHTTPException, RequestValidationError)):
            raise

        error_detail = {
            "error": type(exc).__name__,
            "message": str(exc),
        }

        if settings.show_tracebacks and hasattr(exc, "__traceback__"):
            error_detail["traceback"] = traceback.format_exc()

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_detail,
        )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
        },
        headers=exc.headers if hasattr(exc, "headers") else None,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Starlette ≥ 0.40 改名為 HTTP_422_UNPROCESSABLE_CONTENT，舊常數仍可用但會警告
    code = getattr(
        status,
        "HTTP_422_UNPROCESSABLE_CONTENT",
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
    return JSONResponse(
        status_code=code,
        content={
            "error": "ValidationError",
            "message": "Invalid request data",
            "details": exc.errors(),
        },
    )
