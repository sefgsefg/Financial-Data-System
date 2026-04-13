from fastapi import FastAPI, BackgroundTasks
from app.workers.tasks import fetch_stock_price_task
from prometheus_client import make_asgi_app, Counter

app = FastAPI(title="金融數據採集與監控系統 API")

# Prometheus 指標
REQUEST_COUNT = Counter("api_requests_total", "Total requests received")

# 掛載 Prometheus Metrics Endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.post("/jobs/fetch/{symbol}")
async def create_fetch_job(symbol: str):
    REQUEST_COUNT.inc()
    # 非同步將任務推送到 Redis Task Queue
    task = fetch_stock_price_task.delay(symbol)
    return {
        "status": "Task Queued", 
        "task_id": task.id, 
        "symbol": symbol
    }

@app.get("/health")
async def health_check():
    # 這裡未來可以加入檢測 Redis 與 DB 的連線狀態
    return {"status": "healthy", "service": "Producer Watchdog"}