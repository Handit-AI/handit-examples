from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "unstructured-to-structured"
    env: str = "dev"
    version: str = "0.1.0"
    outputs_dir: str = "assets/outputs"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # Fija el .env en la raíz del subproyecto: examples/unstructured-to-structured/.env
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")


settings = Settings()


