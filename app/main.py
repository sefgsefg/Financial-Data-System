import time
from fastapi import FastAPI, BackgroundTasks, Request
from app.workers.tasks import fetch_stock_price_task
from prometheus_client import make_asgi_app, Counter, Histogram

app = FastAPI(title="金融數據採集與監控系統 API")

# 定義 Prometheus 業務指標
REQUEST_COUNT = Counter(
    "api_requests_total", 
    "Total requests received by endpoint", 
    ["method", "endpoint"]
)
TASK_DISPATCH_COUNT = Counter(
    "task_dispatch_total", 
    "Total celery tasks dispatched", 
    ["status"]
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", 
    "Request latency in seconds",
    ["endpoint"]
)

# 掛載 Prometheus Metrics Endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# 建立 Middleware 來攔截並計算 API 延遲
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # 紀錄請求數量與延遲
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(process_time)
    
    return response

@app.post("/jobs/fetch/{symbol}")
async def create_fetch_job(symbol: str):
    try:
        # 非同步推送任務
        task = fetch_stock_price_task.delay(symbol)
        TASK_DISPATCH_COUNT.labels(status="success").inc()
        return {"status": "Task Queued", "task_id": task.id, "symbol": symbol}
    except Exception as e:
        TASK_DISPATCH_COUNT.labels(status="failed").inc()
        return {"status": "Dispatch Failed", "error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Producer Watchdog"}