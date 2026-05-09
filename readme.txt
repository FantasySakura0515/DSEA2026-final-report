台北市危老建築與都市更新資料分析
==========================================

研究主題：台北市危建最多的地區，都更有在追趕嗎？
作者：江慶于（414580662）


-- 資料夾對照 --

本專案的資料清理橫跨 Python（FastAPI 後端）與 R（分析報告），
與一般 R-only 流程不同，檔案分布對應到課程要求的四類資料夾如下：

RawData（原始資料）
  原始資料來自台北市開放資料平台與台北市都市發展局的公開 API。
  後端在每次呼叫時即時 fetch，未保存靜態 raw 檔。

Code（程式碼）
  - backend/app/      FastAPI 後端：路由、模型、服務分層
  - backend/data/     原始資料抓取與清洗腳本（地址展開、地理編碼）
  - taipei_urban_renewal_hazard_race.Rmd        行政區層級分析報告
  - backend_data_cleaning_technical_report.Rmd  清洗技術說明

Data（清理後資料）
  - backend/data/*_format.json         後端清理後的中間檔
                                       （地震危建、海砂屋；含逐棟地址與經緯度）
  - backend/public/urban-update.json   後端整理後的都市更新資料
  - Data/clean_data_<YYYY-MM-DD>.csv   R 報告合併後的行政區層級乾淨資料
                                       （檔名日期為 knit 當天，由 Sys.Date() 自動帶入）
  - codebook.md                        Data/ 內 CSV 各欄位的意義與計算方式

Results（結果）
  - taipei_urban_renewal_hazard_race.html         分析報告
  - backend_data_cleaning_technical_report.html   後端技術報告
  - final_project_part2_proposal.pdf              專案提案


-- 重現分析的步驟 --

1. 啟動後端（需先安裝 uv）
   cd backend
   uv sync
   uv run uvicorn app.main:app --reload

2. Knit R 報告（後端需在 localhost:8000 上跑）
   Rscript -e "rmarkdown::render('taipei_urban_renewal_hazard_race.Rmd')"

   執行後 Data/clean_data_2026-05-08.csv 會自動產生。


-- 為什麼用 Python 後端清理 --

原始資料的清理門檻並不低。地震危建的地址欄位常在同一筆中
混合多棟建物，例如「天母北路 87 巷 22 弄 2、4、6 號；87 巷 16
至 22 號」，需要解析後展開為每一棟的個別地址；都市更新的空間
資料則為 Polygon / MultiPolygon 巢狀結構，在 R 中處理較為繁瑣。
另外，部分資料只有地址而無座標，必須呼叫 ArcGIS 地理編碼 API
補齊經緯度，並處理請求速率限制。

將上述前置處理交由 Python 後端執行，以 Shapely 處理空間資料、
正則表達式處理地址、httpx 處理 API 呼叫，最後將結果以 JSON API
提供 R 報告端使用。R 端僅負責行政區層級的合併與分析，符合
課程介紹的 dplyr / tidyr 工作流程。
