import asyncio
import httpx
from app.workers.celery_app import celery_app
from app.schemas.stock import StockPriceData
import logging

logger = logging.getLogger(__name__)

async def fetch_stock_price_async(symbol: str):
    # 這裡模擬非同步 HTTPX 請求，實際可替換為目標 API 或 Playwright
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 模擬打 API (請換成真實網址)
        # response = await client.get(f"https://api.finance.com/v1/quote?symbol={symbol}")
        # 模擬返回資料
        mock_data = {"symbol": symbol, "price": 550.0}
        
        # Pydantic 數據校驗
        try:
            validated_data = StockPriceData(**mock_data)
            logger.info(f"成功擷取並校驗數據: {validated_data}")
            # TODO: 寫入 ClickHouse 或 PostgreSQL
            return validated_data.model_dump_json()
        except ValueError as e:
            logger.error(f"數據品質異常: {str(e)}")
            raise

@celery_app.task(bind=True, max_retries=3)
def fetch_stock_price_task(self, symbol: str):
    """
    Celery task 封裝 async 函數。
    具備自動重試機制 (Error Handling & Retry)
    """
    try:
        # 在同步的 Celery worker 中執行 async 邏輯
        result = asyncio.run(fetch_stock_price_async(symbol))
        return result
    except Exception as exc:
        logger.warning(f"任務執行失敗，準備重試 ({self.request.retries}/3): {exc}")
        raise self.retry(exc=exc, countdown=5 * (self.request.retries + 1))