from pydantic import BaseModel, Field, validator
from datetime import datetime

class StockPriceData(BaseModel):
    symbol: str = Field(..., description="股票代號，例如: 2330.TW")
    price: float = Field(..., description="即時股價")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            # 這裡觸發的 ValueError 後續會被 Error Handling 捕捉並寫入 Log/報警
            raise ValueError(f"異常股價檢測: 股價不能小於或等於 0, 收到數值: {v}")
        return v