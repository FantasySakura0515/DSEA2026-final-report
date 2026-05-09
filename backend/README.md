# Backend

基於 **uv** 與 **FastAPI** 的後端專案，提供台北市地震危險建築物、海砂屋與都市更新相關 API。

## 建立虛擬環境

```bash
uv venv
```

> 若需指定 Python 版本：
>
> ```bash
> uv venv --python 3.12
> ```

## 安裝依賴

```bash
uv sync
```

或新增新套件：

```bash
uv add <package>
```

## 執行伺服器

請於 `backend/` 目錄執行：

```bash
uv run uvicorn app.main:app --reload
```

瀏覽器開啟：

- [http://127.0.0.1:8000](http://127.0.0.1:8000)
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 品質檢查

```bash
uv run ruff check .
uv run pytest
```

## 專案結構

```text
backend/
├─ app/
│  ├─ main.py              # FastAPI app factory and middleware setup
│  ├─ router.py            # API router aggregator
│  ├─ routers/             # Domain-specific route modules
│  ├─ handlers/            # Request use-case orchestration
│  ├─ services/            # External APIs, file loading, spatial search
│  ├─ models/              # Pydantic request/response/data models
│  ├─ middleware/          # Exception handling middleware
│  ├─ utils/               # Shared utilities (cache, geo helpers)
│  └─ config.py            # Centralized paths and runtime settings
├─ data/                   # Data cleaning scripts and generated JSON
├─ public/                 # Runtime static JSON data
├─ test/                   # Pytest unit, model, router and parsing tests
├─ pyproject.toml
└─ uv.lock
```

## 分層原則

- `routers/` 只負責 HTTP path、query parameters、response model 與 HTTP error。
- `handlers/` 負責組合 use case，例如篩選、查無資料轉成 404。
- `services/` 負責外部資料來源、檔案讀取、座標與空間查詢；對 data.taipei 的呼叫包了 TTL 快取（環境變數 `UPSTREAM_CACHE_TTL`，預設 300 秒）。
- `models/` 負責資料契約、欄位 alias 與序列化格式；共用結構（如 `ImportDate`）置於 `_common.py`。
- `config.py` 集中管理路徑、CORS 來源（`CORS_ORIGINS`）與 runtime flags，避免相對路徑依啟動目錄而壞掉。

## 環境變數

| 變數 | 預設 | 用途 |
| --- | --- | --- |
| `APP_DEBUG` | unset | 設為 `1`/`true` 時，500 回應夾帶 traceback，方便本機 debug。 |
| `CORS_ORIGINS` | `*` | 逗號分隔的允許來源；非 `*` 時自動啟用 `allow_credentials`。 |
| `UPSTREAM_CACHE_TTL` | `300` | 對 data.taipei 上游的 TTL 快取秒數。 |

## 必要 VS Code 擴充套件

| Extension | ID                         |
| --------- | -------------------------- |
| Python    | `ms-python.python`         |
| Pylance   | `ms-python.vscode-pylance` |
| Ruff      | `charliermarsh.ruff`       |

快速安裝：

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
```

## uv 安裝文件

如尚未安裝 `uv`，請參考官方文件：

[https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
