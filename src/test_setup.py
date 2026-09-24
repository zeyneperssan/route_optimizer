import os
import sys
import yaml
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def test_setup():
    print("=" * 50)
    print("[TEST] LOJISTIK ROTA OPTIMIZASYONU - MODUL 0 TESTI")
    print("=" * 50)

    packages = ["ortools", "openrouteservice", "pandas", "folium", "yaml", "dotenv"]
    print("\n1. Kutuphane Kontrolleri:")
    all_packages_ok = True
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"  [OK] {pkg} basariyla yuklendi.")
        except ImportError as e:
            print(f"  [HATA] {pkg} bulunamadi: {e}")
            all_packages_ok = False

    print("\n2. Yapilandirma (config.yaml) Kontrolu:")
    config_path = "config.yaml"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            print(f"  [OK] config.yaml basariyla okundu.")
            print(f"     - Hedef: {config.get('objective')}")
            print(f"     - Siparis dosyasi: {config.get('data', {}).get('orders_file')}")
            print(f"     - Arac dosyasi: {config.get('data', {}).get('vehicles_file')}")
        except Exception as e:
            print(f"  [HATA] config.yaml okunurken hata olustu: {e}")
    else:
        print(f"  [HATA] {config_path} dosyasi bulunamadi!")

    print("\n3. API Anahtari (.env) Kontrolu:")
    load_dotenv()
    api_key = os.getenv("ORS_API_KEY")
    if not api_key or api_key == "senin_api_anahtarin_buraya":
        print("  [BILGI] ORS_API_KEY henuz ayarlanmamis (Varsayilan sablon degerinde).")
        print("     -> Gercek yol matrisi icin openrouteservice.org uzerinden anahtar alip .env dosyasina yazabilirsiniz.")
    else:
        print(f"  [OK] ORS_API_KEY algilandi: {api_key[:6]}... (toplam {len(api_key)} karakter)")

    print("\n" + "=" * 50)
    if all_packages_ok:
        print(">>> TEBRIKLER: Modul 0 (Kurulum ve Iskelet) basariyla tamamlandi! <<<")
    else:
        print(">>> Bazi kutuphaneler eksik, lutfen gereksinimleri kontrol edin. <<<")
    print("=" * 50)

if __name__ == "__main__":
    test_setup()
