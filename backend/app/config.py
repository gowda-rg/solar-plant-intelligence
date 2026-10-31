# SEMANTIC — configuration boundary
# IN:  environment variables and optional `backend/.env` file on disk
# OUT: a Settings object used by database and API code (never commit real `.env`)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = (
        "postgresql+psycopg2://solar_app:solar_dev@localhost:5432/solar_plant_intelligence"
    )


settings = Settings()
