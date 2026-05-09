from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.router import api_router


from app.middleware.exception import (
    exception_middleware,
    http_exception_handler,
    validation_exception_handler,
)


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Taipei Urban Renewal Backend",
        description="台北市危建與都市更新資料 API",
        version="1.0.0",
        docs_url="/docs",
    )

    app_.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app_.add_exception_handler(RequestValidationError, validation_exception_handler)

    app_.middleware("http")(exception_middleware)

    origins = settings.cors_origins
    app_.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app_.include_router(api_router, prefix="/api")
    return app_


app = create_app()
