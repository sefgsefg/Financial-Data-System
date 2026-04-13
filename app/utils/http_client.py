import httpx
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 準備常見的 User-Agent 池，降低被阻擋的機率
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

async def fetch_json_data(url: str, timeout: float = 10.0) -> Optional[dict]:
    """
    非同步獲取 JSON 數據的通用函數，內建反爬基礎機制
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    # 使用 async with 確保連線資源會被正確釋放
    async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status() # 遇到 4xx 或 5xx 會直接拋出例外
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP 狀態錯誤 {exc.response.status_code} 於請求 {exc.request.url}")
            raise # 將錯誤往上拋，交給 Celery 的 Retry 機制處理
        except httpx.RequestError as exc:
            logger.error(f"網路連線錯誤於請求 {exc.request.url}: {exc}")
            raise