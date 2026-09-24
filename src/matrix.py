"""Modül 3 — Gerçek yol mesafe/süre matrisi.

OpenRouteService Matrix servisinden noktalar arası gerçek karayolu
mesafe (metre) ve süre (saniye) matrislerini üretir; kotayı korumak için
tüm matrisi tek parça olarak cache'ler ve gerektiğinde isteği parçalara böler.
"""
import hashlib
import json
import math
from pathlib import Path

import openrouteservice
import pandas as pd

MAX_ROUTES_PER_CALL = 2500


def _point_list(orders: pd.DataFrame) -> pd.DataFrame:
    """Matris için nokta sırasını sabitler: DEPO her zaman 0. indekste olur.

    Sıradaki modüller (OR-Tools) depoyu indeks 0 kabul edeceği için bu sıralama
    burada, veri girdiği her yerden garanti edilsin diye matrix.py'de yapılır.
    """
    if orders["lat"].isna().any() or orders["lon"].isna().any():
        eksik = orders[orders["lat"].isna() | orders["lon"].isna()]["kargo_takip_no"].tolist()
        raise ValueError(
            f"Koordinatı olmayan sipariş(ler) var: {eksik}. "
            "Önce Modül 2 (geocode_addresses) çalıştırılmalı."
        )
    depo = orders[orders["islem_tipi"] == "DEPO"]
    digerleri = orders[orders["islem_tipi"] != "DEPO"]
    return pd.concat([depo, digerleri], ignore_index=True)


def _signature(points: pd.DataFrame, profile: str) -> str:
    """Nokta kümesi + profile göre benzersiz bir cache anahtarı üretir.

    Aynı noktalar tekrar sorulursa (ör. programı yeniden çalıştırınca) matris
    ORS'den değil cache'den gelsin diye koordinatların kendisinden hash alınır.
    """
    veri = [
        (row["kargo_takip_no"], round(row["lat"], 6), round(row["lon"], 6))
        for _, row in points.iterrows()
    ]
    ham = json.dumps({"profile": profile, "noktalar": veri}, sort_keys=True)
    return hashlib.md5(ham.encode("utf-8")).hexdigest()


def _load_cache(cache_path: str) -> dict:
    path = Path(cache_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_cache(cache_path: str, cache: dict) -> None:
    path = Path(cache_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _call_ors_matrix(client: "openrouteservice.Client", locations: list, profile: str):
    """ORS Matrix'i, gerekirse kaynakları parçalara bölerek çağırır.

    # [MİMARİ_BİLGİ]: ORS Matrix API'sinde tek istekte maksimum rota kotası (genelde 2500) bulunur.
    # Bu kısıtlamayı aşmak için Batching (Yığınlama) mekanizması kurulmuştur. 'sources' parametresiyle
    # istekler sadece belirli bir grup nokta kümesi (blok_boyu) hedeflenecek şekilde bölünür.

    ORS'ye TÜM noktaları tek 'locations' listesi olarak gönderiyoruz ama
    'sources' parametresiyle her istekte sadece bir blok satır istiyoruz.
    Böylece koordinatları tekrar tekrar yollamadan, N x N matrisi
    (kaynak_bloğu x tüm_hedefler) parçalar halinde toplarız — çok durak
    olduğunda tek istekte izin verilen rota sayısını aşmamak için gerekli.
    """
    n = len(locations)
    blok_boyu = max(1, MAX_ROUTES_PER_CALL // n)

    dist_m = [[0.0] * n for _ in range(n)]
    dur_s = [[0.0] * n for _ in range(n)]

    for basla in range(0, n, blok_boyu):
        kaynaklar = list(range(basla, min(basla + blok_boyu, n)))
        sonuc = client.distance_matrix(
            locations=locations,
            profile=profile,
            sources=kaynaklar,
            destinations=list(range(n)),
            metrics=["distance", "duration"],
            units="m",
        )
        for yerel_i, gercek_i in enumerate(kaynaklar):
            dist_m[gercek_i] = sonuc["distances"][yerel_i]
            dur_s[gercek_i] = sonuc["durations"][yerel_i]

    return dist_m, dur_s


def build_matrix(
    orders: pd.DataFrame,
    api_key: str,
    cache_path: str = "cache/matrix_cache.json",
    profile: str = "driving-car",
) -> tuple[list, list, pd.DataFrame]:
    """Gerçek yol mesafe (m) ve süre (s) matrislerini üretir; cache kullanır.

    Girdi olarak Modül 2'den (geocode_addresses) geçmiş, 'lat'/'lon' sütunları
    dolu bir orders DataFrame'i bekler. Dönen matrislerin satır/sütun sırası,
    dönen üçüncü değer olan 'points' DataFrame'inin sırasıyla birebir aynıdır
    (0. indeks = DEPO).
    """
    if not api_key:
        raise ValueError("ORS API anahtarı yok; .env dosyasına ORS_API_KEY ekleyin.")

    points = _point_list(orders)
    imza = _signature(points, profile)
    cache = _load_cache(cache_path)

    if imza in cache:
        kayit = cache[imza]
        return kayit["distances_m"], kayit["durations_s"], points

    hedef_points = [(str(row["kargo_takip_no"]), round(float(row["lat"]), 5), round(float(row["lon"]), 5)) for _, row in points.iterrows()]
    hedef_set = set(hedef_points)
    for kayit in cache.values():
        kayitli_pts = [(str(p.get("kargo_takip_no", "")), round(float(p.get("lat", 0)), 5), round(float(p.get("lon", 0)), 5)) for p in kayit.get("noktalar", [])]
        if kayitli_pts and len(kayitli_pts) >= len(hedef_points) and hedef_set.issubset(set(kayitli_pts)):
            idx = {pt: i for i, pt in enumerate(kayitli_pts)}
            sec = [idx[pt] for pt in hedef_points]
            dm, ds = kayit["distances_m"], kayit["durations_s"]
            dist_m = [[dm[i][j] for j in sec] for i in sec]
            dur_s = [[ds[i][j] for j in sec] for i in sec]
            cache[imza] = {
                "kargo_takip_no": [str(x) for x in points["kargo_takip_no"]],
                "noktalar": [{"kargo_takip_no": str(row["kargo_takip_no"]), "lat": float(row["lat"]), "lon": float(row["lon"])} for _, row in points.iterrows()],
                "distances_m": dist_m,
                "durations_s": dur_s
            }
            _save_cache(cache_path, cache)
            return dist_m, dur_s, points

    client = openrouteservice.Client(key=api_key)
    locations = list(zip(points["lon"], points["lat"]))  
    dist_m, dur_s = _call_ors_matrix(client, locations, profile)

    cache[imza] = {
        "kargo_takip_no": [str(x) for x in points["kargo_takip_no"]],
        "noktalar": [{"kargo_takip_no": str(row["kargo_takip_no"]), "lat": float(row["lat"]), "lon": float(row["lon"])} for _, row in points.iterrows()],
        "distances_m": dist_m,
        "durations_s": dur_s,
    }
    _save_cache(cache_path, cache)

    return dist_m, dur_s, points


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    """İki koordinat arası kuş uçuşu mesafe (km) — Haversine formülü."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def summarize_matrix(points: pd.DataFrame, dist_m: list, dur_s: list) -> dict:
    """Matrisi özetler ve gerçek yol mesafesini kuş uçuşuyla kıyaslar.

    Amaç: 'gerçek yol her zaman kuş uçuşundan uzundur, İstanbul gibi bir
    şehirde bu fark ne kadar büyük?' sorusuna somut bir rakam vermek.
    """
    n = len(points)
    mesafeler_km, oranlar = [], []
    en_uzun = (None, None, -1.0)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            yol_km = dist_m[i][j] / 1000.0
            kus_km = _haversine_km(
                points.iloc[i]["lat"], points.iloc[i]["lon"],
                points.iloc[j]["lat"], points.iloc[j]["lon"],
            )
            mesafeler_km.append(yol_km)
            if kus_km > 0.05:  
                oranlar.append(yol_km / kus_km)
            if yol_km > en_uzun[2]:
                en_uzun = (points.iloc[i]["kargo_takip_no"], points.iloc[j]["kargo_takip_no"], yol_km)

    sureler_dk = [s / 60.0 for row in dur_s for s in row if s > 0]

    return {
        "nokta_sayisi": n,
        "ortalama_mesafe_km": sum(mesafeler_km) / len(mesafeler_km),
        "en_uzun_mesafe": en_uzun,
        "ortalama_sure_dk": sum(sureler_dk) / len(sureler_dk) if sureler_dk else 0.0,
        "yol_vs_kus_ucusu_ortalama_oran": sum(oranlar) / len(oranlar) if oranlar else None,
        "yol_vs_kus_ucusu_en_yuksek_oran": max(oranlar) if oranlar else None,
    }
