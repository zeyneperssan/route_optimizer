"""Modül 9/10 — Kargo KPI'ları ve senaryo karşılaştırması.

Modül 9'da: Her senaryo (distance/time/cost) için KPI'lar hesaplanır:
  - Toplam mesafe (km)
  - Toplam süre (saat)
  - Toplam maliyet (TL)
  - Araç sayısı
  - KG doluluk %
  - Desi doluluk %
  - Zamanında teslimat %
"""
import pandas as pd


def compute_kpis(rotalar, points, vehicles, orders):
    """Rotalardan temel KPI'ları hesaplar.

    Parametreler:
      rotalar: extract_routes() çıktısı (duraklar, mesafe_km, durak_zamanlar_dk)
      points: durak bilgileri (ilk satır depo)
      vehicles: araç filosofu
      orders: orijinal sipariş verisi (kategori, teslimat süresi için)

    Çıktı: KPI sözlüğü
    """
    if not rotalar:
        return {
            "toplam_km": 0,
            "toplam_saat": 0,
            "toplam_maliyet_tl": 0,
            "arac_sayisi": 0,
            "kg_dolusu_oran": 0,
            "desi_dolusu_oran": 0,
            "zamaninda_teslimat_oran": 0,
        }

    toplam_km = 0
    toplam_maliyet_tl = 0
    toplam_saat = 0
    toplam_kg = 0
    toplam_desi = 0
    zamaninda_teslimat_sayisi = 0
    toplam_teslimat_siparis = 0

    for rota in rotalar:
        arac_id = rota["arac_id"]
        arac = vehicles[vehicles["arac_id"] == arac_id].iloc[0]

        mesafe_km = rota["mesafe_km"]
        toplam_km += mesafe_km
        sabit_maliyet = arac["sabit_maliyet"]
        km_maliyet = arac["km_maliyet"]
        rota_maliyet = sabit_maliyet + (mesafe_km * km_maliyet)
        toplam_maliyet_tl += rota_maliyet

        if "sure_dk" in rota:
            toplam_saat += rota["sure_dk"] / 60.0
        elif "durak_zamanlar_dk" in rota and len(rota["durak_zamanlar_dk"]) >= 2:
            toplam_saat += (rota["durak_zamanlar_dk"][-1] - rota["durak_zamanlar_dk"][0]) / 60.0

        duraklar = rota["duraklar"]
        for i, kargo_no in enumerate(duraklar):
            if i == 0 or i == len(duraklar) - 1:
                continue  
            point_row = points[points["kargo_takip_no"] == kargo_no]
            if point_row.empty:
                continue
            point = point_row.iloc[0]
            toplam_kg += float(point.get("agirlik_kg", 0) or 0)
            toplam_desi += float(point.get("desi", 0) or 0)

            if str(point.get("islem_tipi", "")) == "TESLIMAT":
                beklenen_bitis_dk = point.get("zaman_bitis")
                if pd.notna(beklenen_bitis_dk) and "durak_zamanlar_dk" in rota \
                        and i < len(rota["durak_zamanlar_dk"]):
                    toplam_teslimat_siparis += 1
                    if rota["durak_zamanlar_dk"][i] <= beklenen_bitis_dk:
                        zamaninda_teslimat_sayisi += 1

    filo_kapasite_kg = vehicles["kapasite_kg"].sum()
    filo_kapasite_desi = vehicles["kapasite_desi"].sum()

    kg_dolusu_oran = (toplam_kg / filo_kapasite_kg * 100) if filo_kapasite_kg > 0 else 0
    desi_dolusu_oran = (toplam_desi / filo_kapasite_desi * 100) if filo_kapasite_desi > 0 else 0
    zamaninda_teslimat_oran = (zamaninda_teslimat_sayisi / toplam_teslimat_siparis * 100) if toplam_teslimat_siparis > 0 else 100

    toplam_gidis_km = sum(float(r.get("gidis_km", r.get("mesafe_km", 0))) for r in rotalar)
    toplam_donus_km = sum(float(r.get("donus_km", 0)) for r in rotalar)
    toplam_gidis_sure_dk = sum(float(r.get("gidis_sure_dk", 0)) for r in rotalar)
    toplam_donus_sure_dk = sum(float(r.get("donus_sure_dk", 0)) for r in rotalar)
    toplam_sure_dk = sum(float(r.get("sure_dk", 0)) for r in rotalar)

    return {
        "toplam_km": round(toplam_km, 1),
        "toplam_gidis_km": round(toplam_gidis_km, 1),
        "toplam_donus_km": round(toplam_donus_km, 1),
        "toplam_sure_dk": round(toplam_sure_dk, 1),
        "toplam_gidis_sure_dk": round(toplam_gidis_sure_dk, 1),
        "toplam_donus_sure_dk": round(toplam_donus_sure_dk, 1),
        "toplam_saat": round(toplam_sure_dk / 60.0, 1),
        "toplam_maliyet_tl": round(toplam_maliyet_tl, 0),
        "arac_sayisi": len(rotalar),
        "kg_dolusu_oran": round(kg_dolusu_oran, 0),
        "desi_dolusu_oran": round(desi_dolusu_oran, 0),
        "zamaninda_teslimat_oran": round(zamaninda_teslimat_oran, 0),
    }
