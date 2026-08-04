from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    google_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()