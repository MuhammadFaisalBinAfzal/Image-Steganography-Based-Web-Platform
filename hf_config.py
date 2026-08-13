import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

_ENV_LOADED = False


def _ensure_env_loaded() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    if load_dotenv is not None:
        env_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(env_path)
    _ENV_LOADED = True


def get_huggingface_api_token() -> str | None:
    """Return the Hugging Face API token from environment variables."""
    _ensure_env_loaded()
    return (
        os.getenv("HUGGINGFACE_API_TOKEN")
        or os.getenv("HF_TOKEN")
        or os.getenv("HUGGINGFACE_HUB_TOKEN")
    )


def get_hf_authorization_header() -> dict[str, str]:
    """Return Authorization header for Hugging Face API requests."""
    token = get_huggingface_api_token()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def get_pollinations_api_key() -> str | None:
    """Return the Pollinations API key from environment variables."""
    _ensure_env_loaded()
    return os.getenv("POLLINATIONS_API_KEY") or os.getenv("POLLINATIONS_KEY")

