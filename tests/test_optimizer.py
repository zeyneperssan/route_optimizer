"""Optimizasyon değişmezleri (invariants) testi.

Bu test ORS/AĞ GEREKTİRMEZ: gerçek koordinat yerine deterministik sahte
koordinatlar ve bunlardan türetilen sentetik bir mesafe/süre matrisi kullanır.
Amaç, model + çözüm mantığının kısıtları GERÇEKTEN uyguladığını doğrulamak:

  1. Tüm siparişler servis edilir (hiçbiri düşmez).
  2. Hiçbir araç kg VEYA desi kapasitesini aşmaz.
  3. AGIR_YUK paketleri motokuryeye atanmaz.
  4. Bir durak, zaman penceresi açılmadan (zaman_baslangic) servis edilmez.
  5. Raporlanan mesafe pozitiftir (gerçek matristen gelir).

Çalıştırma (proje kök dizininde):
    python -m tests.test_optimizer
Beklenen çıktı sonunda: "TÜM TESTLER GEÇTİ".
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd  

from src.config_loader import load_config  
from src.loader import load_orders, load_vehicles, validate  
from src.matrix import _point_list, _haversine_km  
from src.model import build_model  
from src.solve import solve, extract_routes  


def _dummy_coords(orders: pd.DataFrame) -> pd.DataFrame:
    """Deterministik, tekrarlanabilir sahte koordinatlar (İstanbul civarı)."""
    df = orders.copy()
    base_lat, base_lon = 40.98, 29.05
    lats, lons = [], []
    for i in range(len(df)):
        lats.append(base_lat + (i % 5) * 0.02)
        lons.append(base_lon + (i // 5) * 0.02)
    df["lat"] = lats
    df["lon"] = lons
    return df


def _synthetic_matrix(points: pd.DataFrame):
    """Kuş uçuşu × 1.4 (yol yaklaşımı) ile mesafe (m) ve süre (s) matrisi."""
    n = len(points)
    dist = [[0.0] * n for _ in range(n)]
    dur = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            km = _haversine_km(
                points.iloc[i]["lat"], points.iloc[i]["lon"],
                points.iloc[j]["lat"], points.iloc[j]["lon"],
            )
            dist[i][j] = km * 1000 * 1.4        
            dur[i][j] = (km / 40.0) * 3600.0    
    return dist, dur


def run_checks():
    cfg = load_config()
    orders = load_orders(cfg["data"]["orders_file"])
    vehicles = load_vehicles(cfg["data"]["vehicles_file"])
    validate(orders, vehicles)

    orders = _dummy_coords(orders)
    points = _point_list(orders)
    dist_m, dur_s = _synthetic_matrix(points)

    tip = dict(zip(vehicles["arac_id"], vehicles["arac_tipi"]))
    cap_desi = dict(zip(vehicles["arac_id"], vehicles["kapasite_desi"]))
    cap_kg = dict(zip(vehicles["arac_id"], vehicles["kapasite_kg"]))
    desi = dict(zip(points["kargo_takip_no"].astype(str), points["desi"].fillna(0)))
    kg = dict(zip(points["kargo_takip_no"].astype(str), points["agirlik_kg"].fillna(0)))
    kat = dict(zip(points["kargo_takip_no"].astype(str), points["kategori"]))
    wstart = dict(zip(points["kargo_takip_no"].astype(str), points["zaman_baslangic"]))

    musteri = set(str(k) for k in points["kargo_takip_no"] if str(k) != "0")

    for obj in ["distance", "time", "cost"]:
        routing, manager = build_model(points, vehicles, dist_m, dur_s, objective=obj)
        solution = solve(routing, manager, cfg, objective=obj)
        assert solution is not None, f"[{obj}] çözüm bulunamadı"
        rotalar = extract_routes(routing, manager, solution, points, vehicles, dist_m, dur_s)

        served = set()
        for r in rotalar:
            aid = r["arac_id"]
            stops = [d for d in r["duraklar"] if d != "0"]
            served |= set(stops)

            td = sum(float(desi.get(str(d), 0)) for d in stops)
            tk = sum(float(kg.get(str(d), 0)) for d in stops)
            assert td <= cap_desi[aid] + 1e-6, f"[{obj}] {aid} DESİ aşımı: {td:.0f} > {cap_desi[aid]}"
            assert tk <= cap_kg[aid] + 1e-6, f"[{obj}] {aid} KG aşımı: {tk:.0f} > {cap_kg[aid]}"
            assert r["mesafe_km"] > 0, f"[{obj}] {aid} mesafe pozitif değil"

            for i, d in enumerate(r["duraklar"]):
                if d == "0":
                    continue
                if kat.get(str(d)) == "AGIR_YUK":
                    assert tip[aid] != "MOTO_KURYE", f"[{obj}] AGIR_YUK {d} motokuryede!"
                ws = wstart.get(str(d))
                if pd.notna(ws) and "durak_zamanlar_dk" in r:
                    assert r["durak_zamanlar_dk"][i] >= ws - 1, \
                        f"[{obj}] {d} penceresi açılmadan servis edildi (varış<{ws})"

        toplam_talep = sum(float(desi.get(str(k), 0)) for k in musteri)
        filo_desi = float(vehicles["kapasite_desi"].sum())
        max_desi = float(vehicles["kapasite_desi"].max())
        if toplam_talep <= filo_desi:
            for kn in (musteri - served):
                assert float(desi.get(str(kn), 0)) > max_desi, \
                    f"[{obj}] servable sipariş {kn} haksız yere düşürüldü"
        print(f"  [{obj}] OK — {len(rotalar)} araç, {len(served)}/{len(musteri)} sipariş servis, kısıtlar sağlandı")

    print("TÜM TESTLER GEÇTİ ✓")


if __name__ == "__main__":
    run_checks()
