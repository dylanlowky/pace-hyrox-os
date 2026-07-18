from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

def _secret(name: str, default: str = "") -> str:
    try:
        import streamlit as st
        return str(st.secrets.get(name, os.getenv(name, default)))
    except Exception:
        return os.getenv(name, default)

@dataclass(frozen=True)
class Settings:
    app_env: str = _secret("APP_ENV", "development")
    demo_mode: bool = _as_bool(_secret("DEMO_MODE", "true"), True)
    supabase_url: str = _secret("SUPABASE_URL")
    supabase_anon_key: str = _secret("SUPABASE_ANON_KEY")
    openai_api_key: str = _secret("OPENAI_API_KEY")
    openai_model: str = _secret("OPENAI_MODEL", "gpt-4.1-mini")

    @property
    def supabase_ready(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)

    @property
    def ai_ready(self) -> bool:
        return bool(self.openai_api_key)

settings = Settings()
