# 台北市危建與都市更新資料分析

本專案以台北市開放資料為基礎，整理「地震危險建築物」、「海砂屋」與「都市更新案件」資料，建立本機 FastAPI 後端，並用 R Markdown 產出 HTML 分析報告。

研究主題：

> 台北市危老建築與都市更新的賽跑：危建最多的地區，都更有在追趕嗎？

專案重點不是單純讀取 JSON，而是把原始資料中混亂的地址、跨區案件、缺漏座標與巢狀空間資料，清洗成可查詢、可定位、可分析的資料服務。

## 專案內容

| 檔案 / 目錄 | 說明 |
| --- | --- |
| `backend/` | FastAPI 後端服務與資料清洗程式 |
| `taipei_urban_renewal_hazard_race.Rmd` | 危建與都市更新追趕率分析報告 |
| `taipei_urban_renewal_hazard_race.html` / `.pdf` | 分析報告輸出（HTML 與 PDF） |
| `backend_data_cleaning_technical_report.Rmd` | 整體技術棧與資料清洗能力說明 |
| `backend_data_cleaning_technical_report.html` / `.pdf` | 技術報告輸出 |
| `Data/clean_data_<YYYY-MM-DD>.csv` | 行政區層級的合併乾淨資料（R 報告輸出，檔名日期由 knit 當天自動帶入） |
| `codebook.md` | CSV 各欄位的意義、單位與計算方式 |
| `readme.txt` | 對應到課程要求的資料夾結構（RawData / Data / Code / Results）說明 |

## 技術棧

後端與資料工程：

- Python 3.12
- FastAPI
- uv / uvicorn
- Pydantic
- httpx
- GeoJSON
- Shapely / STRtree
- ArcGIS Geocoding API
- pytest / ruff

分析報告：

- R Markdown
- httr2
- dplyr
- tidyr
- readr
- ggplot2
- knitr
- scales

地圖視覺化：

- ggplot2 `geom_polygon` + `coord_quickmap`
- 行政區界資料：geoBoundaries TWN ADM2（OpenStreetMap, CC-BY-SA 2.0）
- 標籤位置：Shapely `representative_point` 預先計算

## 資料清洗亮點

原始資料非常髒，主要問題包括：

- 地址欄位同時包含多棟建物。
- 門牌包含範圍，例如 `16至22號`。
- 門牌包含枚舉，例如 `2、4、6號`。
- 地址混入括號備註與樓層文字。
- 都市更新案件可能跨行政區，例如 `士林區,北投區`。
- `台北市` 與 `臺北市` 用字不一致。
- 部分資料只有地址，沒有經緯度。
- 都市更新資料含 Polygon / MultiPolygon 等複雜空間結構。

清洗後資料可用於：

- 本機 API 查詢。
- 行政區彙總統計。
- 危建與都更案件比較。
- 都市更新追趕率計算。
- R Markdown 自動產生 HTML 報告。

## 啟動後端

進入後端目錄：

```bash
cd backend
```

安裝依賴：

```bash
uv sync
```

啟動 FastAPI：

```bash
uv run uvicorn app.main:app --reload
```

啟動後可開啟：

- API 文件：http://127.0.0.1:8000/docs
- API Base URL：http://127.0.0.1:8000/api

## 主要 API

分析報告會呼叫以下本機端點：

| API | 說明 |
| --- | --- |
| `GET /api/earthquake-buildings` | 地震危險建築物清單 |
| `GET /api/chloride-ionized-concrete` | 海砂屋 / 高氯離子混凝土建築 |
| `GET /api/urban-update` | 都市更新案件依行政區彙總 |
| `GET /api/geojson/earthquake-buildings` | 地震危建建物 GeoJSON（地圖用） |
| `GET /api/geojson/chloride-ionized-concrete` | 海砂屋 GeoJSON（地圖用） |
| `GET /api/geojson/taipei-districts` | 台北市 12 行政區界 GeoJSON（地圖底圖） |

完整 API 可至 `/docs` 查看。

## 產生分析報告

請先確認後端已啟動於 `http://localhost:8000`。

在 RStudio 開啟並 Knit：

- `taipei_urban_renewal_hazard_race.Rmd`
- `backend_data_cleaning_technical_report.Rmd`

或用命令列同時產生 HTML 與 PDF：

```bash
Rscript -e "rmarkdown::render('taipei_urban_renewal_hazard_race.Rmd', output_format = 'all')"
Rscript -e "rmarkdown::render('backend_data_cleaning_technical_report.Rmd', output_format = 'all')"
```

PDF 輸出需要 LaTeX 環境（`xelatex`），若未安裝可用 `tinytex::install_tinytex()`。

## R 套件需求

若 RStudio knit 時出現缺套件，可先安裝：

```r
install.packages(c(
  "httr2",
  "dplyr",
  "tidyr",
  "readr",
  "ggplot2",
  "knitr",
  "scales",
  "ragg",
  "rmarkdown",
  "tinytex"  # PDF 輸出需要；首次安裝後執行 tinytex::install_tinytex()
))
```

## 專案報告

### 1. 危建與都市更新分析

`taipei_urban_renewal_hazard_race.Rmd` 會：

- 呼叫本機 FastAPI。
- 清理台北市行政區資料。
- 統一 `台 / 臺` 用字。
- 移除無行政區資料。
- 合併地震危建、海砂屋與都市更新資料。
- 計算 `危建總數` 與 `都更追趕率`。
- 產生 5 張 ggplot2 圖表（含台北市危建分布地圖）。
- 用 inline R 自動帶入結論數字。

### 2. 後端與資料清洗技術報告

`backend_data_cleaning_technical_report.Rmd` 會說明：

- 後端技術棧。
- FastAPI 分層架構。
- 資料清洗流程。
- 地址解析與座標補齊。
- 都市更新空間資料處理。
- 為什麼這批髒資料清洗後才有分析價值。

## 專案價值

本專案將原本難以直接使用的城市開放資料，整理成：

- 可驗證的資料模型。
- 可查詢的 API。
- 可定位的空間資料。
- 可分析的行政區統計。
- 可視覺化的 HTML 報告。

也就是把髒資料從「看得到但不好用」，整理成「可以被後端、分析報告與決策討論重複使用」的資料產品。
