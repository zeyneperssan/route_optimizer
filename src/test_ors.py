"""Modül 0 — Gerçek ORS bağlantı testi.

.env dosyasına gerçek API anahtarını girdikten sonra çalıştır:
    python src/test_ors.py

Örnek bir adresi koordinata çevirerek (geocoding) bağlantının
ve anahtarın gerçekten çalıştığını doğrular.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config_loader import get_api_key  


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    key = get_api_key()
    if not key:
        print("[DUR] ORS_API_KEY .env dosyasında ayarlı değil (hâlâ şablon).")
        print("      openrouteservice.org/dev üzerinden ücretsiz anahtar alıp")
        print("      .env içine ORS_API_KEY=... olarak yazın, sonra tekrar çalıştırın.")
        return

    try:
        import openrouteservice
    except ImportError:
        print("[HATA] openrouteservice yüklü değil. 'pip install -r requirements.txt' çalıştırın.")
        return

    client = openrouteservice.Client(key=key)
    address = "Bağdat Caddesi, Kadıköy, İstanbul"
    print(f"[TEST] Geocoding deneniyor: {address}")
    try:
        res = client.pelias_search(text=address, size=1)
    except Exception as e:
        print(f"[HATA] ORS çağrısı başarısız: {e}")
        print("       Anahtarı ve internet bağlantısını kontrol edin.")
        return

    feats = res.get("features", [])
    if not feats:
        print("[HATA] Sonuç dönmedi. Anahtar/kotayı kontrol edin.")
        return

    lon, lat = feats[0]["geometry"]["coordinates"]
    print(f"[OK] Bağlantı başarılı! Koordinat: enlem={lat:.5f}, boylam={lon:.5f}")
    print(">>> Modül 0 TAMAMLANDI: gerçek ORS çağrısı çalışıyor. <<<")


if __name__ == "__main__":
    main()
