"""Modül 2 — Geocoding (adres -> koordinat).

Koordinatı olmayan adresleri OpenRouteService (Pelias search) ile
enlem/boylama çevirir. Sonuçları cache'e (JSON) yazar ki aynı adres
iki kez sorulmasın — ücretsiz ORS planının günlük/aylık kotasını korur.
"""
import json
import time
from pathlib import Path

import openrouteservice
import pandas as pd

REQUEST_DELAY_SEC = 0.2


def _load_cache(cache_path: str) -> dict:
    """Diskteki geocode cache'ini okur; dosya yoksa boş sözlükle başlar."""
    path = Path(cache_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_cache(cache_path: str, cache: dict) -> None:
    """Cache sözlüğünü diske yazar (klasör yoksa oluşturur)."""
    path = Path(cache_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _geocode_one(
    client: "openrouteservice.Client",
    address: str,
    country_code: str | None,
    focus_point: tuple[float, float] | None,
):
    """Tek adresi ORS Pelias search ile koordinata çevirir.

    focus_point (lon, lat) verilirse, sonuçlar bu noktaya yakınlığa göre
    de puanlanır — Türkiye'de aynı isimli birçok mahalle olduğundan
    (ör. "Barbaros", "Merkez"), bu şubeye yakın olanı öne çıkarmaya yardım eder.
    Sonuç bulunamazsa None döner (ör. yazım hatası, çok belirsiz adres).
    """
    result = client.pelias_search(
        text=address, size=1, country=country_code, focus_point=focus_point
    )
    features = result.get("features", [])
    if not features:
        return None
    feature = features[0]
    lon, lat = feature["geometry"]["coordinates"]
    confidence = feature.get("properties", {}).get("confidence", 0.0)
    location_name = feature.get("properties", {}).get("name", "")
    return {
        "lat": lat,
        "lon": lon,
        "confidence": confidence,
        "location_name": location_name,
    }


def geocode_addresses(
    orders: pd.DataFrame,
    api_key: str,
    cache_path: str = "cache/geocode_cache.json",
    country_code: str | None = "TUR",
    focus_point: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """Sipariş adreslerini koordinata çevirir; cache'i önceliklendirir.

    Akış: her benzersiz adres için önce cache'e bakılır; orada yoksa ORS'ye
    sorulur ve sonuç (bulunsa da bulunamasa da) cache'e yazılır — böylece
    hatalı/bulunamayan bir adres için tekrar tekrar kota harcanmaz.
    Döndürülen DataFrame'e 'lat' ve 'lon' sütunları eklenir; bulunamayan
    adreslerde bu alanlar NaN kalır.
    """
    if not api_key:
        raise ValueError("ORS API anahtarı yok; .env dosyasına ORS_API_KEY ekleyin.")

    cache = _load_cache(cache_path)
    client = openrouteservice.Client(key=api_key)

    yeni_sorgu = 0
    for address in orders["adres"].unique():
        if address in cache:
            continue
        cache[address] = _geocode_one(client, address, country_code, focus_point)
        yeni_sorgu += 1
        time.sleep(REQUEST_DELAY_SEC)

    if yeni_sorgu:
        _save_cache(cache_path, cache)

    df = orders.copy()
    df["lat"] = df["adres"].map(lambda a: (cache.get(a) or {}).get("lat"))
    df["lon"] = df["adres"].map(lambda a: (cache.get(a) or {}).get("lon"))
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    return df


def summarize_geocode(df: pd.DataFrame) -> dict:
    """Geocoding sonucunu özetler: kaç adres başarılı/başarısız oldu."""
    basarisiz = df[df["lat"].isna() | df["lon"].isna()]
    return {
        "toplam": len(df),
        "basarili": len(df) - len(basarisiz),
        "basarisiz": len(basarisiz),
        "basarisiz_adresler": basarisiz["adres"].tolist(),
    }


def save_verification_map(df: pd.DataFrame, out_path: str = "cache/geocode_kontrol.html") -> str:
    """Geocode edilen noktaları basit bir haritaya koyar (gözle doğrulama).

    Modül 11'deki rota haritasından farkı: burada rota değil, sadece
    noktaların doğru konumda düşüp düşmediğini kontrol ederiz.
    """
    import folium

    gecerli = df.dropna(subset=["lat", "lon"])
    if gecerli.empty:
        raise ValueError("Haritaya konacak geçerli koordinat yok.")

    merkez = [gecerli["lat"].mean(), gecerli["lon"].mean()]
    harita = folium.Map(location=merkez, zoom_start=11)

    renkler = {"DEPO": "black", "TESLIMAT": "blue", "TOPLAMA": "orange"}
    for _, row in gecerli.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"{row['kargo_takip_no']} — {row['musteri_adi']}<br>{row['adres']}",
            tooltip=row["kargo_takip_no"],
            icon=folium.Icon(color=renkler.get(row["islem_tipi"], "gray")),
        ).add_to(harita)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    harita.save(str(out))
    return str(out)
