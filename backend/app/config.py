import os
from pathlib import Path


class Settings:
    backend_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = backend_dir / "data"
    public_dir: Path = backend_dir / "public"
    show_tracebacks: bool = os.getenv("APP_DEBUG", "").lower() in {
        "1",
        "true",
        "yes",
    }

    @property
    def cors_origins(self) -> list[str]:
        raw = os.getenv("CORS_ORIGINS", "*")
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
