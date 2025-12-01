import os

from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    database_url: str
    diagrams_path: str
    templates: str
    pdf_path: str
    api_key: str
    grpc_host: str
    grpc_port: int
    msys2_dll_path: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
