import clickhouse_connect
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_clickhouse_client():
    """
    獲取 ClickHouse 客戶端。
    注意：實務上金融高頻寫入通常採用 Batch Insert (批次寫入)。
    """
    try:
        client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            database=settings.CLICKHOUSE_DB
        )
        return client
    except Exception as e:
        logger.error(f"ClickHouse 連線失敗: {e}")
        raise

def init_clickhouse_tables(client):
    """
    初始化 ClickHouse 的時序資料表。
    使用 MergeTree 引擎，並以 timestamp 和 symbol 作為排序鍵，極大化查詢效能。
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS stock_prices (
        symbol String,
        price Float64,
        timestamp DateTime('Asia/Taipei')
    ) ENGINE = MergeTree()
    ORDER BY (symbol, timestamp)
    """
    client.command(create_table_query)
    logger.info("ClickHouse 表格初始化完成")