from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    BOT_TOKEN: str
    BOT_USERNAME: str
    STORAGE_CHANNEL_ID: int
    MONGODB_URI: str
    REDIS_URL: str = "redis://localhost:6379/0"
    WEBHOOK_BASE_URL: str
    PORT: int = 8080
    ADMIN_IDS: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    JWT_SECRET: str
    MAINTENANCE_MODE: bool = False
    MAX_FILE_SIZE_MB: int = 2000
    USER_RATE_LIMIT_PER_MIN: int = 20
    GLOBAL_RATE_LIMIT_RPS: int = 50

    @property
    def admin_ids_list(self) -> List[int]:
        """Parse admin IDs from comma-separated string"""
        return [int(x.strip()) for x in self.ADMIN_IDS.split(',') if x.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
