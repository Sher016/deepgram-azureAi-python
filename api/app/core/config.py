from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
 
 
class Settings(BaseSettings):
    # API
    api_key: str
   
 
    # PostgreSQL
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_port: int = 5432
 
    # Azure OpenAI
    azure_openai_base_url: str
    azure_openai_api_key: str
    azure_openai_model: str
    azure_openai_api_version: str
 
    # Deepgram           
    deepgram_api_key: str
    deepgram_stt_url: str  
    deepgram_tts_url: str 
 
    model_config = SettingsConfigDict(
        env_file="../infra/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
 
 
@lru_cache
def get_settings() -> Settings:
    return Settings()