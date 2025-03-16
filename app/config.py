from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_sheet_app_id: str
    app_sheet_game_table: str
    app_sheet_app_access_key: str
    use_app_sheet: bool = True
    cors_allow_origin: str = "*"
    websocket_ping_interval: int = 20

    model_config = SettingsConfigDict(env_file = ".env")

@lru_cache
def get_settings():
    return Settings()
