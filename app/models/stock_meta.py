from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.postgres import Base

class StockMeta(Base):
    __tablename__ = "stock_meta"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    company_name = Column(String(100), nullable=False)
    market_type = Column(String(20))  # 例如: TWSE, OTC, NASDAQ
    is_active = Column(Boolean, default=True) # 是否持續派發爬蟲任務
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())