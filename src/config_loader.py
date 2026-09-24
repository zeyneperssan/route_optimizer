"""Ortak yapılandırma yükleyici.

config.yaml ve .env dosyalarını tek yerden okur; böylece her modül
aynı ayarları ve API anahtarını tutarlı şekilde kullanır.
"""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

PLACEHOLDER = "senin_api_anahtarin_buraya"


def load_config(path: str = "config.yaml") -> dict:
    """config.yaml'ı okuyup sözlük olarak döndürür."""
    cfg_path = ROOT / path
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_api_key() -> str | None:
    """.env'den ORS API anahtarını okur.

    Anahtar yoksa veya hâlâ şablon değerindeyse None döner.
    """
    load_dotenv(ROOT / ".env")
    key = os.getenv("ORS_API_KEY")
    if not key or key.strip() in ("", PLACEHOLDER):
        return None
    return key.strip()
