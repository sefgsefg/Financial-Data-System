import asyncio
import logging
from datetime import datetime
from app.workers.celery_app import celery_app
from app.schemas.stock import StockPriceData
from app.utils.http_client import fetch_json_data
from app.db.clickhouse import get_clickhouse_client
from app.utils.http_client import fetch_price_with_playwright

logger = logging.getLogger(__name__)

async def etl_stock_price_async(symbol: str):
    # 1. Extract: 改用 Playwright 抓取網頁渲染後的數據
    logger.info(f"啟動無頭瀏覽器採集數據: {symbol}")
    try:
        current_price = await fetch_price_with_playwright(symbol)
    except Exception as e:
        raise ValueError(f"數據抓取失敗: {e}")
    
    # 2. Transform/Validate: Pydantic 數據合約校驗
    try:
        valid_data = StockPriceData(
            symbol=symbol,
            price=current_price,
            timestamp=datetime.utcnow()
        )
        logger.info(f"資料校驗通過: {valid_data.symbol} - ${valid_data.price}")
    except ValueError as e:
        logger.error(f"資料品質異常: {e}")
        raise

    # 3. Load: 寫入 ClickHouse (這部分不變)
    try:
        client = get_clickhouse_client()
        client.insert(
            'stock_prices',
            [[valid_data.symbol, valid_data.price, valid_data.timestamp]],
            column_names=['symbol', 'price', 'timestamp']
        )
        logger.info(f"成功將 {symbol} 的數據寫入 ClickHouse")
    except Exception as e:
        logger.error(f"ClickHouse 寫入失敗: {e}")
        raise

    return valid_data.model_dump_json()

@celery_app.task(bind=True, max_retries=3, acks_late=True)
def fetch_stock_price_task(self, symbol: str):
    """
    Celery 分散式任務。
    acks_late=True 確保 Worker 真的執行完畢才從 Redis 移除任務，防止 Worker 崩潰導致任務遺失。
    """
    try:
        # 在同步的 Celery worker 中執行 async 爬蟲與寫入邏輯
        result = asyncio.run(etl_stock_price_async(symbol))
        return result
    except Exception as exc:
        logger.warning(f"任務執行失敗，準備重試 ({self.request.retries}/3): {exc}")
        # 採用指數退避 (Exponential Backoff) 重試策略：5s, 10s, 15s...
        raise self.retry(exc=exc, countdown=5 * (self.request.retries + 1))