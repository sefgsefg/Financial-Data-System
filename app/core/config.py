from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # PostgreSQL 設定 (用於關聯式資料、股票清單、爬蟲任務狀態)
    POSTGRES_USER: str = "fin_user"
    POSTGRES_PASSWORD: str = "fin_password"
    POSTGRES_DB: str = "fin_data"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # ClickHouse 設定 (用於海量金融時序資料、Tick Data)
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_DB: str = "financial_metrics"

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()