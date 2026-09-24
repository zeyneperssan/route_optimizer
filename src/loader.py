"""Modül 1 — Veri okuma, doğrulama ve desi kontrolü.

siparisler.csv ve araclar.csv dosyalarını okur, temel doğrulamayı yapar
ve toplam talep (kg + desi) ile toplam filo kapasitesini karşılaştırır.
"""
import pandas as pd

ORDER_COLUMNS = [
    "kargo_takip_no", "musteri_adi", "adres", "islem_tipi",
    "agirlik_kg", "desi", "kategori",
    "zaman_baslangic", "zaman_bitis", "servis_suresi_dk",
]
VEHICLE_COLUMNS = [
    "arac_id", "arac_tipi", "kapasite_kg", "kapasite_desi",
    "sabit_maliyet", "km_maliyet", "max_calisma_dk", "max_durak_sayisi",
]

VALID_ISLEM = {"TESLIMAT", "TOPLAMA", "DEPO"}
VALID_KATEGORI = {"STANDART", "EXPRESS", "AGIR_YUK", "DEPO"}


def _check_columns(df, required, name):
    """Zorunlu sütunların hepsi var mı?"""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: eksik sütun(lar): {missing}")


def _hhmm_to_min(s):
    """'HH:MM' metnini gün içi dakikaya çevirir (ör. 09:30 -> 570)."""
    h, m = str(s).strip().split(":")
    return int(h) * 60 + int(m)


def load_orders(path: str) -> pd.DataFrame:
    """Sipariş (gönderi) CSV'sini okur ve tiplerini düzeltir."""
    df = pd.read_csv(path, dtype=str).fillna("")
    _check_columns(df, ORDER_COLUMNS, "siparisler.csv")
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    df["agirlik_kg"] = pd.to_numeric(df["agirlik_kg"], errors="coerce")
    df["desi"] = pd.to_numeric(df["desi"], errors="coerce")
    df["servis_suresi_dk"] = pd.to_numeric(df["servis_suresi_dk"], errors="coerce")
    def safe_hhmm_to_min(x):
        if not x or x == "":
            return pd.NA
        try:
            return _hhmm_to_min(x)
        except Exception as e:
            raise ValueError(f"Zaman formatı '{x}' hatalı (HH:MM olmalı): {e}")

    df["zaman_baslangic"] = df["zaman_baslangic"].apply(safe_hhmm_to_min)
    df["zaman_bitis"] = df["zaman_bitis"].apply(safe_hhmm_to_min)
    return df


def load_vehicles(path: str) -> pd.DataFrame:
    """Araç (filo) CSV'sini okur ve tiplerini düzeltir."""
    df = pd.read_csv(path, dtype=str).fillna("")
    _check_columns(df, VEHICLE_COLUMNS, "araclar.csv")
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    for col in ["kapasite_kg", "kapasite_desi", "sabit_maliyet", "km_maliyet",
                "max_calisma_dk", "max_durak_sayisi"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def validate(orders: pd.DataFrame, vehicles: pd.DataFrame) -> dict:
    """Veriyi doğrular; hata varsa yükseltir, uyarı/özet döndürür."""
    # [İŞ_MANTIĞI / GÜVENLİK]: Optimizasyon modelinin ("Infeasible" yani çözümsüz) çökmesini önlemek
    # için veriler modele girmeden önce strict (sıkı) kurallardan geçirilir. 
    # Ters zaman pencereleri, eksik kapasiteler veya yanlış işlem tipleri burada elenir.
    hatalar, uyarilar = [], []

    for i, r in orders.iterrows():
        etiket = r["kargo_takip_no"] or f"satır {i}"
        if r["islem_tipi"] not in VALID_ISLEM:
            hatalar.append(f"{etiket}: geçersiz islem_tipi '{r['islem_tipi']}'")
        if r["kategori"] not in VALID_KATEGORI:
            hatalar.append(f"{etiket}: geçersiz kategori '{r['kategori']}'")
        if pd.isna(r["agirlik_kg"]) or r["agirlik_kg"] < 0:
            hatalar.append(f"{etiket}: agirlik_kg geçersiz")
        if pd.isna(r["desi"]) or r["desi"] < 0:
            hatalar.append(f"{etiket}: desi geçersiz")
        if pd.notna(r["zaman_baslangic"]) and pd.notna(r["zaman_bitis"]):
            if r["zaman_baslangic"] >= r["zaman_bitis"]:
                hatalar.append(f"{etiket}: zaman penceresi hatalı "
                               f"(başlangıç >= bitiş)")

    depo = orders[orders["islem_tipi"] == "DEPO"]
    if len(depo) == 0:
        hatalar.append("Depo satırı yok (islem_tipi=DEPO olan bir satır olmalı).")
    elif len(depo) > 1:
        uyarilar.append("Birden çok DEPO satırı var; ilki kullanılacak.")

    teslimat = orders[orders["islem_tipi"] == "TESLIMAT"]
    toplama = orders[orders["islem_tipi"] == "TOPLAMA"]
    musteri = orders[orders["islem_tipi"] != "DEPO"]
    top_kg, top_desi = musteri["agirlik_kg"].sum(), musteri["desi"].sum()
    filo_kg, filo_desi = vehicles["kapasite_kg"].sum(), vehicles["kapasite_desi"].sum()
    if top_kg > filo_kg:
        uyarilar.append(f"Toplam yük ağırlığı ({top_kg:.0f} kg) "
                        f"filo kapasitesini ({filo_kg:.0f} kg) aşıyor.")
    if top_desi > filo_desi:
        uyarilar.append(f"Toplam yük desisi ({top_desi:.0f}) "
                        f"filo desi kapasitesini ({filo_desi:.0f}) aşıyor.")

    if hatalar:
        raise ValueError("Veri doğrulama hataları:\n  - " + "\n  - ".join(hatalar))

    return {
        "toplam_siparis": len(orders) - len(depo),
        "teslimat": len(teslimat),
        "toplama": len(toplama),
        "toplam_teslimat_kg": top_kg,
        "toplam_teslimat_desi": top_desi,
        "filo_kapasite_kg": filo_kg,
        "filo_kapasite_desi": filo_desi,
        "arac_sayisi": len(vehicles),
        "uyarilar": uyarilar,
    }
