import logging
from app.db.clickhouse import get_clickhouse_client, init_clickhouse_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("正在連線至 ClickHouse...")
        client = get_clickhouse_client()
        init_clickhouse_tables(client)
        logger.info("ClickHouse stock_prices 資料表初始化成功！")
    except Exception as e:
        logger.error(f"初始化失敗: {e}")

if __name__ == "__main__":
    main()