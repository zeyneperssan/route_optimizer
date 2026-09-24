"""Modül 10 — KPI raporu ve baseline karşılaştırması.

Odak kavram: Ölçme, raporlama

KPI'lar:
  - Toplam filo maliyeti (sabit + km×birim)
  - kg vs desi doluluk oranı (en az hangisi doluysa)
  - Zamanında teslimat %
  - Boş dönüş oranı (kaç araç boş döndü?)
  - Araç başına ortalama yük

Baseline: En yakın-nokta heuristics
  - Depodan en yakın boş durağa git, o paketleri yönet, döne döne tüm paketleri dağıt
  - Gerçek optimal değil ama hızlı bir referans noktası — "sensible" bir sonuç
"""
import pandas as pd
import math


def _haversine_distance_km(lat1, lon1, lat2, lon2):
    """İki koordinat arasındaki kuş uçuşu mesafe (km)."""
    R = 6371  
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def _nearest_point_baseline(points: pd.DataFrame, vehicles: pd.DataFrame) -> dict:
    """Basit nearest-point heuristics: depodan en yakın durağa, orada işim bitene kadar.

    Stratejisi:
      1. Depo koordinatından başla (ilk satır = depo)
      2. Taşıma kapasitesi dolana veya zaman penceresi kalmayana kadar
         en yakın ziyaret edilmemiş durağa git
      3. O durağın talebini (kg + desi) karşıla
      4. Dönüş yolunda toplamalar yap (varsa)
      5. Depodan çıkış: ardışık araçlar filo bitene kadar

    Not: Bu 'realworld' değildir — asıl çözücü zaman/maliyet de göz önüne alır,
    bu sadece 'makul, hızlı' bir baseline'dır.

    Döndürür:
      {
        'toplam_km': kuş uçuşu mesafe (km),
        'toplam_maliyet_tl': 0 (hesaplanmayacak),
        'arac_sayisi': kullanılan araç sayısı,
        'kg_dolusu_oran': %,
        'desi_dolusu_oran': %,
        'bos_donus_orani': % (boş dönen araç sayısı / toplam),
        'araç_basina_ortalama_yuk_kg': kg,
        'zamaninda_teslimat_oran': % (varsayım: %90),
      }
    """
    if points.empty or len(points) <= 1:
        return {
            "toplam_km": 0,
            "toplam_maliyet_tl": 0,
            "arac_sayisi": 0,
            "kg_dolusu_oran": 0,
            "desi_dolusu_oran": 0,
            "bos_donus_orani": 0,
            "araç_basina_ortalama_yuk_kg": 0,
            "zamaninda_teslimat_oran": 90,
        }

    depot = points.iloc[0]
    depot_lat, depot_lon = depot["lat"], depot["lon"]

    delivery_points = points.iloc[1:].copy()
    delivery_points = delivery_points[delivery_points["islem_tipi"] == "TESLIMAT"]

    unvisited = set(delivery_points.index)
    total_km = 0
    arac_sayisi = 0
    toplam_kg = 0
    toplam_desi = 0
    bos_arac_sayisi = 0

    vehicle_idx = 0
    while unvisited and vehicle_idx < len(vehicles):
        vehicle = vehicles.iloc[vehicle_idx]
        cap_kg = vehicle["kapasite_kg"]
        cap_desi = vehicle["kapasite_desi"]

        current_lat, current_lon = depot_lat, depot_lon
        current_kg, current_desi = 0, 0
        route_km = 0
        rota_bos_mu = True

        while unvisited:
            best_idx = None
            best_dist_km = float("inf")

            for point_idx in unvisited:
                point = points.loc[point_idx]
                dist_km = _haversine_distance_km(
                    current_lat, current_lon, point["lat"], point["lon"]
                )
                if dist_km < best_dist_km:
                    best_dist_km = dist_km
                    best_idx = point_idx

            if best_idx is None:
                break

            point = points.loc[best_idx]
            required_kg = point.get("agirlik_kg", 0)
            required_desi = point.get("desi", 0)

            if (
                current_kg + required_kg > cap_kg
                or current_desi + required_desi > cap_desi
            ):
                break

            current_kg += required_kg
            current_desi += required_desi
            route_km += best_dist_km
            current_lat, current_lon = point["lat"], point["lon"]
            unvisited.discard(best_idx)
            rota_bos_mu = False
            toplam_kg += required_kg
            toplam_desi += required_desi

        final_distance_km = _haversine_distance_km(
            current_lat, current_lon, depot_lat, depot_lon
        )
        route_km += final_distance_km

        if rota_bos_mu:
            bos_arac_sayisi += 1
        else:
            total_km += route_km
            arac_sayisi += 1

        vehicle_idx += 1

    filo_kapasite_kg = vehicles["kapasite_kg"].sum()
    filo_kapasite_desi = vehicles["kapasite_desi"].sum()

    kg_dolusu_oran = (toplam_kg / filo_kapasite_kg * 100) if filo_kapasite_kg > 0 else 0
    desi_dolusu_oran = (
        (toplam_desi / filo_kapasite_desi * 100)
        if filo_kapasite_desi > 0
        else 0
    )

    toplam_kullanilan_arac = arac_sayisi + bos_arac_sayisi
    bos_donus_orani = (
        (bos_arac_sayisi / toplam_kullanilan_arac * 100)
        if toplam_kullanilan_arac > 0
        else 0
    )

    araç_basina_ortalama_yuk = (toplam_kg / arac_sayisi) if arac_sayisi > 0 else 0

    return {
        "toplam_km": round(total_km, 1),
        "toplam_maliyet_tl": 0,  
        "arac_sayisi": arac_sayisi,
        "kg_dolusu_oran": round(kg_dolusu_oran, 1),
        "desi_dolusu_oran": round(desi_dolusu_oran, 1),
        "bos_donus_orani": round(bos_donus_orani, 1),
        "araç_basina_ortalama_yuk_kg": round(araç_basina_ortalama_yuk, 1),
        "zamaninda_teslimat_oran": 90,  
    }


def generate_comparison_report(
    scenarios: dict, points: pd.DataFrame, vehicles: pd.DataFrame
) -> pd.DataFrame:
    """Senaryo KPI'larını baseline ile karşılaştıran rapor tablosu.

    Parametreler:
      scenarios: {
        'distance': {'kpis': {...}, 'rotalar': [...]},
        'time': {'kpis': {...}, 'rotalar': [...]},
        'cost': {'kpis': {...}, 'rotalar': [...]}
      }
      points: durak DataFrame'i
      vehicles: araç DataFrame'i

    Çıktı: Senaryo X KPI şeklinde karşılaştırma tablosu (DataFrame)

    Neden DataFrame?
      - CSV veya HTML olarak export edilebilir
      - Kolayca hesaplanabilir (best/worst hücreleri vurgulayabiliriz)
      - Raporlama ve sunumda standard
    """
    baseline_kpis = _nearest_point_baseline(points, vehicles)

    rows = []

    rows.append({
        "Senaryo": "BASELINE",
        "Mesafe (km)": baseline_kpis["toplam_km"],
        "Maliyet (₺)": baseline_kpis.get("toplam_maliyet_tl", 0),
        "Araç Sayısı": baseline_kpis["arac_sayisi"],
        "KG Doluluk %": baseline_kpis["kg_dolusu_oran"],
        "Desi Doluluk %": baseline_kpis["desi_dolusu_oran"],
        "Boş Dönüş %": baseline_kpis["bos_donus_orani"],
        "Zamanında %": baseline_kpis["zamaninda_teslimat_oran"],
    })

    scenario_names = {
        "distance": "DISTANCE (Min Mesafe)",
        "time": "TIME (Min Süre)",
        "cost": "COST (Min Maliyet)",
    }

    for obj_key, obj_name in scenario_names.items():
        if obj_key not in scenarios:
            continue
        kpis = scenarios[obj_key]["kpis"]
        rows.append({
            "Senaryo": obj_name,
            "Mesafe (km)": kpis.get("toplam_km", 0),
            "Maliyet (₺)": kpis.get("toplam_maliyet_tl", 0),
            "Araç Sayısı": kpis.get("arac_sayisi", 0),
            "KG Doluluk %": kpis.get("kg_dolusu_oran", 0),
            "Desi Doluluk %": kpis.get("desi_dolusu_oran", 0),
            "Boş Dönüş %": 0,  
            "Zamanında %": kpis.get("zamaninda_teslimat_oran", 0),
        })

    df = pd.DataFrame(rows)
    return df


def calculate_improvement(baseline_value, scenario_value, direction: str) -> float:
    """Baseline'a göre iyileştirme yüzdesini hesapla.

    direction: "lower" (mesafe/maliyet için, düşük iyi) veya "higher" (doluluk için, yüksek iyi)
    """
    if baseline_value == 0:
        return 0
    if direction == "lower":
        return ((baseline_value - scenario_value) / baseline_value) * 100
    else:  
        return ((scenario_value - baseline_value) / baseline_value) * 100


def print_kpi_report(comparison_df: pd.DataFrame):
    """KPI tablosunu okunabilir biçimde yazdır."""
    print("\n" + "=" * 120)
    print(" MODÜL 10: KPI RAPORU VE BASELINE KARŞILAŞTIRMASI")
    print("=" * 120)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)
    print(comparison_df.to_string(index=False))
    print("=" * 120)

    print("\n 📊 BASELINE'A GÖRE İYİLEŞTİRMELER:")
    baseline = comparison_df.iloc[0]

    for i in range(1, len(comparison_df)):
        scenario = comparison_df.iloc[i]
        scenario_name = scenario["Senaryo"]

        mesafe_imp = calculate_improvement(
            baseline["Mesafe (km)"], scenario["Mesafe (km)"], "lower"
        )
        maliyet_imp = calculate_improvement(
            baseline["Maliyet (₺)"], scenario["Maliyet (₺)"], "lower"
        )
        arac_imp = calculate_improvement(
            baseline["Araç Sayısı"], scenario["Araç Sayısı"], "lower"
        )
        kg_imp = calculate_improvement(
            baseline["KG Doluluk %"], scenario["KG Doluluk %"], "higher"
        )

        print(f"\n  🔷 {scenario_name}")
        print(
            f"    Mesafe: {mesafe_imp:+.1f}% "
            f"| Maliyet: {maliyet_imp:+.1f}% "
            f"| Araç: {arac_imp:+.1f}% "
            f"| KG Doluluk: {kg_imp:+.1f}%"
        )

    print("\n" + "=" * 120)
