import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    PROJECT_NAME: str = "Multiverse"
    TAGLINE: str = "One question. Multiple minds."
    VERSION: str = "1.1.0"
    API_V1_PREFIX: str = "/api"

    # NVIDIA Build API configuration
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

    # Optional local inference servers (OpenAI-compatible endpoints)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    LMSTUDIO_BASE_URL: str = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
    LLAMACPP_BASE_URL: str = os.getenv("LLAMACPP_BASE_URL", "http://127.0.0.1:8080/v1")
    MLX_BASE_URL: str = os.getenv("MLX_BASE_URL", "http://127.0.0.1:8081/v1")

    # Request & concurrency defaults
    DEFAULT_TIMEOUT_SECONDS: float = float(os.getenv("DEFAULT_TIMEOUT_SECONDS", "90.0"))
    MAX_CONCURRENT_MODELS: int = int(os.getenv("MAX_CONCURRENT_MODELS", "6"))
    DEFAULT_MAX_CALLS_PER_RUN: int = int(os.getenv("DEFAULT_MAX_CALLS_PER_RUN", "24"))
    LOCAL_ONLY_DEFAULT: bool = os.getenv("LOCAL_ONLY_DEFAULT", "false").lower() == "true"
    FREE_ONLY_DEFAULT: bool = os.getenv("FREE_ONLY_DEFAULT", "true").lower() == "true"

    # Storage & Artifacts
    STORAGE_DIR: Path = Path(os.getenv("MULTIVERSE_STORAGE_DIR", str(BASE_DIR / "storage")))
    ARTIFACTS_DIR: Path = Path(os.getenv("MULTIVERSE_ARTIFACTS_DIR", str(BASE_DIR / "storage" / "artifacts")))
    MAX_UPLOAD_BYTES: int = 25 * 1024 * 1024

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/multiverse.db")

    # CORS
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
