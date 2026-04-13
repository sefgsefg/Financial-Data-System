import asyncio
import logging
from datetime import datetime
from app.workers.celery_app import celery_app
from app.schemas.stock import StockPriceData
from app.utils.http_client import fetch_json_data
from app.db.clickhouse import get_clickhouse_client

logger = logging.getLogger(__name__)

async def etl_stock_price_async(symbol: str):
    """
    完整的 ETL 流程：Extract (HTTPX) -> Transform (Pydantic) -> Load (ClickHouse)
    """
    # 這裡以 Yahoo Finance 的非公開 API 作為範例 (實務上請依目標調整)
    # 注意：金融 API 網址結構可能會變，此為演示高可靠架構
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m"
    
    # 1. Extract: 抓取原始數據
    logger.info(f"開始採集數據: {symbol}")
    raw_data = await fetch_json_data(url)
    
    try:
        # 解析 Yahoo API 的深層 JSON 結構
        result = raw_data['chart']['result'][0]
        current_price = result['meta']['regularMarketPrice']
        
        # 2. Transform/Validate: Pydantic 數據合約校驗
        valid_data = StockPriceData(
            symbol=symbol,
            price=current_price,
            timestamp=datetime.utcnow()
        )
        logger.info(f"資料校驗通過: {valid_data.symbol} - ${valid_data.price}")
        
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"資料解析失敗，API 結構可能已改變: {e}")
        raise ValueError("Data extraction failed")
    except ValueError as e:
        # 捕捉 Pydantic 拋出的異常股價 (例如 <= 0)
        logger.error(f"資料品質異常，拒絕寫入: {e}")
        raise

    # 3. Load: 寫入 ClickHouse 海量時序資料庫
    try:
        # 取得連線 (實務上若有極高併發，可考慮改為定期 Batch Insert)
        client = get_clickhouse_client()
        
        # ClickHouse Insert 語法
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