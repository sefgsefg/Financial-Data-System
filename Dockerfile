# 使用微軟官方包含 Playwright 依賴的 Python 映像檔
FROM mcr.microsoft.com/playwright/python:v1.39.0-jammy

# 設定工作目錄
WORKDIR /app

# 設定環境變數，確保 Python 輸出不被緩衝 (讓 Log 即時顯示)
ENV PYTHONUNBUFFERED=1

# 複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 Playwright 瀏覽器 (雖然基礎映像檔有依賴，但仍需下載實際的瀏覽器執行檔)
RUN playwright install chromium

# 複製專案程式碼
COPY . .

# 預設指令 (這裡會被 docker-compose 覆蓋)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]