"""Route Optimizer Backend Service — API ve Optimizasyon Entegrasyonu.

Bu modül, Flask web uygulaması ile optimizasyon motoru arasındaki köprüyü kurar.
Canlı verileri yükler, optimizasyonu çalıştırır, yeni sipariş ekler ve API formatına dönüştürür.
"""
import os
import json
import pandas as pd
from pathlib import Path
from src.config_loader import load_config, get_api_key
from src.loader import load_orders, load_vehicles, validate
from src.geocode import geocode_addresses, summarize_geocode, save_verification_map
from src.matrix import build_matrix
from src.model import build_model
from src.solve import solve, extract_routes
from src.evaluate import compute_kpis
from src.visualize import draw_scenario_maps

BASE_DIR = Path(__file__).resolve().parent.parent

class OptimizationService:
    def __init__(self):
        self.config = load_config()
        self.api_key = get_api_key()
        self.orders_path = BASE_DIR / self.config['data']['orders_file']
        self.vehicles_path = BASE_DIR / self.config['data']['vehicles_file']
        self.cache_dir = BASE_DIR / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.last_results = {}
        self.active_scenario = "distance"
        self.custom_weights = {"cost": 50, "time": 40, "distance": 10}
        
    def run_full_pipeline(self, force_geocode=False):
        """Tüm optimizasyon sürecini çalıştırır ve senaryo sonuçlarını üretir."""
        self.config = load_config()
        orders = load_orders(str(self.orders_path))
        vehicles = load_vehicles(str(self.vehicles_path))
        validation = validate(orders, vehicles)
        
        ors_cfg = self.config.get('ors', {})
        focus_point = None
        if ors_cfg.get('focus_lon') is not None and ors_cfg.get('focus_lat') is not None:
            focus_point = (ors_cfg['focus_lon'], ors_cfg['focus_lat'])
            
        geocode_cache_file = str(self.cache_dir / 'geocode_cache.json')
        if force_geocode and os.path.exists(geocode_cache_file):
            try:
                os.remove(geocode_cache_file)
            except Exception:
                pass

        if self.api_key:
            orders = geocode_addresses(
                orders,
                self.api_key,
                cache_path=geocode_cache_file,
                country_code=ors_cfg.get('country_code', 'TUR'),
                focus_point=focus_point,
            )
            dist_m, dur_s, points = build_matrix(
                orders,
                self.api_key,
                cache_path=str(self.cache_dir / 'matrix_cache.json'),
                profile=ors_cfg.get('profile', 'driving-car'),
            )
        else:
            raise ValueError(
                "ORS API anahtarı bulunamadı (.env → ORS_API_KEY). Gerçek yol "
                "verisi olmadan optimizasyon çalıştırılamaz. Anahtarı ekleyip "
                "sunucuyu yeniden başlatın."
            )

        scenarios = {}
        objectives = ["distance", "time", "cost", "custom"]
        if len(points) <= 1:
            for objective in objectives:
                scenarios[objective] = {
                    "rotalar": [],
                    "kpis": {
                        "toplam_km": 0, "toplam_saat": 0, "toplam_maliyet_tl": 0,
                        "arac_sayisi": 0, "kg_dolusu_oran": 0, "desi_dolusu_oran": 0,
                        "zamaninda_teslimat_oran": 100
                    }
                }
        else:
            for objective in objectives:
                try:
                    routing, manager = build_model(
                        points, vehicles, dist_m, dur_s,
                        objective=objective,
                        custom_weights=self.custom_weights if objective == "custom" else None
                    )
                    solution = solve(routing, manager, self.config, objective=objective)
                    rotalar = extract_routes(routing, manager, solution, points, vehicles, dist_m, dur_s)
                    kpis = compute_kpis(rotalar, points, vehicles, orders)
                    scenarios[objective] = {
                        "rotalar": rotalar,
                        "kpis": kpis,
                    }
                except Exception as e:
                    print(f"[HATA] {objective} optimizasyonu başarısız: {e}")
                    scenarios[objective] = {
                        "rotalar": [],
                        "kpis": {
                            "toplam_km": 0, "toplam_saat": 0, "toplam_maliyet_tl": 0,
                            "arac_sayisi": 0, "kg_dolusu_oran": 0, "desi_dolusu_oran": 0,
                            "zamaninda_teslimat_oran": 0
                        }
                    }

        self.last_results = {
            "scenarios": scenarios,
            "points": points,
            "vehicles": vehicles,
            "orders": orders,
            "validation": validation,
        }
        return self.last_results

    def compute_custom_scenario(self, weights: dict):
        """Özel kullanıcı ağırlıklarıyla (maliyet %, süre %, mesafe %) optimizasyonu anında çözer."""
        if not self.last_results:
            self.run_full_pipeline()

        cost_w = max(0, float(weights.get("cost", 50)))
        time_w = max(0, float(weights.get("time", 40)))
        dist_w = max(0, float(weights.get("distance", 10)))
        total_w = cost_w + time_w + dist_w
        if total_w <= 0:
            cost_w, time_w, dist_w = 50.0, 40.0, 10.0
            total_w = 100.0

        self.custom_weights = {
            "cost": round((cost_w / total_w) * 100, 1),
            "time": round((time_w / total_w) * 100, 1),
            "distance": round((dist_w / total_w) * 100, 1)
        }

        points = self.last_results["points"]
        vehicles = self.last_results["vehicles"]
        orders = self.last_results["orders"]
        
        matrix_cache_file = str(self.cache_dir / 'matrix_cache.json')
        dist_m, dur_s, _ = build_matrix(
            orders,
            self.api_key,
            cache_path=matrix_cache_file,
            profile=self.config.get('ors', {}).get('profile', 'driving-car'),
        )

        if len(points) > 1:
            try:
                routing, manager = build_model(
                    points, vehicles, dist_m, dur_s,
                    objective="custom",
                    custom_weights=self.custom_weights
                )
                solution = solve(routing, manager, self.config, objective="custom")
                rotalar = extract_routes(routing, manager, solution, points, vehicles, dist_m, dur_s)
                kpis = compute_kpis(rotalar, points, vehicles, orders)
                self.last_results["scenarios"]["custom"] = {
                    "rotalar": rotalar,
                    "kpis": kpis,
                }
            except Exception as e:
                print(f"[HATA] Custom optimizasyon başarısız: {e}")

        return self.get_dashboard_data(scenario="custom")

    def get_dashboard_data(self, scenario=None):
        """Dashboard frontend'i için hazırlanmış JSON yapısını döner."""
        if not self.last_results:
            self.run_full_pipeline()

        selected_scenario = scenario or self.active_scenario
        if selected_scenario not in self.last_results["scenarios"]:
            selected_scenario = "distance"
        self.active_scenario = selected_scenario

        scenarios_data = self.last_results["scenarios"]
        current_scenario_data = scenarios_data.get(selected_scenario, {})
        rotalar = current_scenario_data.get("rotalar", [])
        kpis = current_scenario_data.get("kpis", {})
        vehicles_df = self.last_results["vehicles"]
        orders_df = self.last_results["orders"]
        points_df = self.last_results["points"]

        vehicles_list = []
        routes_list = []
        
        order_assignment = {}

        for idx, r in enumerate(rotalar):
            arac_id = r["arac_id"]
            arac_row = vehicles_df[vehicles_df["arac_id"] == arac_id].iloc[0]
            sabit = float(arac_row["sabit_maliyet"])
            km_maliyet = float(arac_row["km_maliyet"])
            mesafe_km = float(r["mesafe_km"])
            toplam_maliyet = sabit + (mesafe_km * km_maliyet)

            duraklar = r["duraklar"] 
            durak_sayisi = max(0, len(duraklar) - 2)

            rota_kg = 0.0
            rota_desi = 0.0
            durak_detaylari = []

            for d_idx, kargo_no in enumerate(duraklar):
                p_match = points_df[points_df["kargo_takip_no"].astype(str) == str(kargo_no)]
                if not p_match.empty:
                    p = p_match.iloc[0]
                    kg = float(p.get("agirlik_kg", 0))
                    desi = float(p.get("desi", 0))
                    if d_idx > 0 and d_idx < len(duraklar) - 1:
                        rota_kg += kg
                        rota_desi += desi
                        order_assignment[str(kargo_no)] = {
                            "arac_id": arac_id,
                            "arac_tipi": str(arac_row.get("arac_tipi", "")),
                            "sira": d_idx,
                            "durum": "Aktif"
                        }
                    
                    varis_dk = 0
                    if "durak_zamanlar_dk" in r and d_idx < len(r["durak_zamanlar_dk"]):
                        varis_dk = r["durak_zamanlar_dk"][d_idx]

                    durak_detaylari.append({
                        "kargo_takip_no": str(kargo_no),
                        "musteri_adi": str(p.get("musteri_adi", "")),
                        "adres": str(p.get("adres", "")),
                        "islem_tipi": str(p.get("islem_tipi", "")),
                        "kategori": str(p.get("kategori", "")),
                        "lat": float(p.get("lat", 41.0)),
                        "lon": float(p.get("lon", 29.0)),
                        "agirlik_kg": kg,
                        "desi": desi,
                        "varis_dakika": varis_dk,
                        "zaman_penceresi": f"{p.get('zaman_baslangic', '09:00')} - {p.get('zaman_bitis', '18:00')}"
                    })

            kapasite_kg = float(arac_row["kapasite_kg"])
            kapasite_desi = float(arac_row["kapasite_desi"])
            doluluk_kg_pct = round((rota_kg / kapasite_kg * 100), 1) if kapasite_kg > 0 else 0
            doluluk_desi_pct = round((rota_desi / kapasite_desi * 100), 1) if kapasite_desi > 0 else 0
            verimlilik_pct = min(100, round((doluluk_kg_pct + doluluk_desi_pct) / 2 + 10, 1))

            gidis_km = float(r.get("gidis_km", mesafe_km))
            donus_km = float(r.get("donus_km", 0.0))
            gidis_sure_dk = float(r.get("gidis_sure_dk", round(gidis_km / 25.0 * 60, 1)))
            donus_sure_dk = float(r.get("donus_sure_dk", round(donus_km / 25.0 * 60, 1)))
            toplam_sure_dk = float(r.get("sure_dk", round(mesafe_km / 25.0 * 60, 1)))
            bacak_mesafeler = r.get("bacak_mesafeler_km", [])

            route_obj = {
                "rota_id": f"RT-{idx+1:03d}",
                "arac_id": arac_id,
                "arac_tipi": str(arac_row.get("arac_tipi", "PANELVAN")),
                "durumu": "Aktif",
                "mesafe_km": round(mesafe_km, 1),
                "gidis_km": round(gidis_km, 1),
                "donus_km": round(donus_km, 1),
                "gidis_sure_dk": round(gidis_sure_dk, 1),
                "donus_sure_dk": round(donus_sure_dk, 1),
                "toplam_sure_dk": round(toplam_sure_dk, 1),
                "bacak_mesafeler_km": bacak_mesafeler,
                "sure_saat": round(toplam_sure_dk / 60.0, 1), 
                "maliyet_tl": round(toplam_maliyet, 1),
                "durak_sayisi": durak_sayisi,
                "doluluk_kg_pct": doluluk_kg_pct,
                "doluluk_desi_pct": doluluk_desi_pct,
                "verimlilik_pct": verimlilik_pct,
                "duraklar": durak_detaylari
            }
            routes_list.append(route_obj)

            vehicles_list.append({
                "arac_id": arac_id,
                "arac_tipi": str(arac_row.get("arac_tipi", "")),
                "durum": "Aktif",
                "hiz": "28.4 km/s",
                "verimlilik": f"{verimlilik_pct}%",
                "kg_doluluk": f"{doluluk_kg_pct}%",
                "desi_doluluk": f"{doluluk_desi_pct}%",
                "mesafe_km": round(mesafe_km, 1),
                "gidis_km": round(gidis_km, 1),
                "donus_km": round(donus_km, 1),
                "gidis_sure_dk": round(gidis_sure_dk, 1),
                "donus_sure_dk": round(donus_sure_dk, 1),
                "toplam_sure_dk": round(toplam_sure_dk, 1),
                "maliyet_tl": round(toplam_maliyet, 1),
                "durak_sayisi": durak_sayisi,
                "kapasite_kg": kapasite_kg,
                "kapasite_desi": kapasite_desi
            })

        kullanilan_araclar = [r["arac_id"] for r in rotalar]
        for _, arac_row in vehicles_df.iterrows():
            if arac_row["arac_id"] not in kullanilan_araclar:
                vehicles_list.append({
                    "arac_id": arac_row["arac_id"],
                    "arac_tipi": str(arac_row.get("arac_tipi", "")),
                    "durum": "Depoda",
                    "hiz": "0 km/s",
                    "verimlilik": "0%",
                    "kg_doluluk": "0%",
                    "desi_doluluk": "0%",
                    "mesafe_km": 0,
                    "maliyet_tl": 0,
                    "durak_sayisi": 0,
                    "kapasite_kg": float(arac_row["kapasite_kg"]),
                    "kapasite_desi": float(arac_row["kapasite_desi"])
                })

        orders_list = []
        for _, row in orders_df.iterrows():
            kargo_no = str(row["kargo_takip_no"])
            if kargo_no == "0" or str(row.get("islem_tipi", "")).upper() == "DEPO":
                continue
            
            assignment = order_assignment.get(kargo_no, {
                "arac_id": "Atanmadı",
                "arac_tipi": "-",
                "sira": "-",
                "durum": "Servis Edilemedi"  
            })

            orders_list.append({
                "kargo_takip_no": kargo_no,
                "musteri_adi": str(row.get("musteri_adi", "")),
                "adres": str(row.get("adres", "")),
                "islem_tipi": str(row.get("islem_tipi", "TESLIMAT")),
                "agirlik_kg": float(row.get("agirlik_kg", 0)),
                "desi": float(row.get("desi", 0)),
                "kategori": str(row.get("kategori", "STANDART")),
                "zaman_baslangic": str(row.get("zaman_baslangic", "09:00")),
                "zaman_bitis": str(row.get("zaman_bitis", "18:00")),
                "servis_suresi_dk": int(row.get("servis_suresi_dk", 5)),
                "lat": float(row.get("lat", 41.0082)) if pd.notna(row.get("lat")) else 41.0082,
                "lon": float(row.get("lon", 28.9784)) if pd.notna(row.get("lon")) else 28.9784,
                "arac_id": assignment["arac_id"],
                "arac_tipi": assignment["arac_tipi"],
                "sira": assignment["sira"],
                "durum": assignment["durum"]
            })

        kategori_sayilari = orders_df[orders_df["kargo_takip_no"] != 0]["kategori"].value_counts().to_dict()
        islem_sayilari = orders_df[orders_df["kargo_takip_no"] != 0]["islem_tipi"].value_counts().to_dict()

        servis_edilemeyen = [o["kargo_takip_no"] for o in orders_list if o["durum"] == "Servis Edilemedi"]
        validation_uyarilar = (self.last_results.get("validation") or {}).get("uyarilar", [])
        uyari_mesajlari = list(validation_uyarilar)
        if servis_edilemeyen:
            uyari_mesajlari.append(
                f"{len(servis_edilemeyen)} sipariş kapasite/kısıt nedeniyle servis edilemedi: "
                + ", ".join(servis_edilemeyen)
                + ". Filoya araç/kapasite ekleyin veya sipariş çıkarın."
            )

        depot_row = points_df.iloc[0] if len(points_df) > 0 else {}
        depot_info = {
            "musteri_adi": str(depot_row.get("musteri_adi", "Kadıköy Şube (Depo)")),
            "adres": str(depot_row.get("adres", "Hasanpasa, Kadikoy, Istanbul")),
            "lat": float(depot_row.get("lat", 40.997314)),
            "lon": float(depot_row.get("lon", 29.044531)),
        }

        toplam_gidis_km = round(sum(float(r.get("gidis_km", 0)) for r in routes_list), 1)
        toplam_donus_km = round(sum(float(r.get("donus_km", 0)) for r in routes_list), 1)
        toplam_gidis_sure_dk = round(sum(float(r.get("gidis_sure_dk", 0)) for r in routes_list), 1)
        toplam_donus_sure_dk = round(sum(float(r.get("donus_sure_dk", 0)) for r in routes_list), 1)
        toplam_sure_dk = round(sum(float(r.get("toplam_sure_dk", 0)) for r in routes_list), 1)

        return {
            "active_scenario": selected_scenario,
            "depot": depot_info,
            "scenarios_summary": {
                name: data["kpis"] for name, data in scenarios_data.items()
            },
            "kpis": {
                "toplam_rota": len(routes_list),
                "aktif_araclar": len([v for v in vehicles_list if v["durum"] == "Aktif"]),
                "toplam_arac": len(vehicles_list),
                "toplam_mesafe_km": kpis.get("toplam_km", 0),
                "toplam_gidis_km": toplam_gidis_km,
                "toplam_donus_km": toplam_donus_km,
                "toplam_sure_dk": toplam_sure_dk,
                "toplam_gidis_sure_dk": toplam_gidis_sure_dk,
                "toplam_donus_sure_dk": toplam_donus_sure_dk,
                "toplam_maliyet_tl": kpis.get("toplam_maliyet_tl", 0),
                "toplam_saat": round(toplam_sure_dk / 60.0, 1),
                "zamaninda_teslimat_oran": kpis.get("zamaninda_teslimat_oran", 95),
                "kg_doluluk_oran": kpis.get("kg_dolusu_oran", 0),
                "desi_doluluk_oran": kpis.get("desi_dolusu_oran", 0)
            },
            "vehicles": vehicles_list,
            "routes": routes_list,
            "orders": orders_list,
            "uyarilar": {
                "servis_edilemeyen_sayisi": len(servis_edilemeyen),
                "servis_edilemeyen": servis_edilemeyen,
                "mesajlar": uyari_mesajlari,
            },
            "custom_weights": self.custom_weights,
            "charts": {
                "categories": {
                    "labels": list(kategori_sayilari.keys()),
                    "data": [int(v) for v in kategori_sayilari.values()]
                },
                "operations": {
                    "labels": list(islem_sayilari.keys()),
                    "data": [int(v) for v in islem_sayilari.values()]
                }
            }
        }

    def add_order(self, order_data: dict):
        """Yeni sipariş ekler (DOĞRULAYARAK ve ATOMİK yazımla), sonra yeniden optimize eder.

        Sağlamlık iyileştirmeleri:
          - Gelen veri doğrulanır; bozuk giriş dosyayı/optimizasyonu bozamaz.
          - CSV'ye atomik yazım (temp dosya + os.replace); yazım yarıda kesilse
            bile mevcut veri bozulmaz.
          - Matris cache'i SİLİNMEZ: cache imza-bazlı olduğundan yeni nokta kümesi
            zaten yeni bir kayıt üretir; eski kayıtlar korunur (ORS kotası israf edilmez).
        """
        from src.loader import VALID_ISLEM, VALID_KATEGORI, _hhmm_to_min

        def _to_pos_float(v, ad):
            try:
                x = float(v)
            except (TypeError, ValueError):
                raise ValueError(f"{ad} sayısal olmalı (gelen: {v!r})")
            if x < 0:
                raise ValueError(f"{ad} negatif olamaz (gelen: {x})")
            return x

        adres = str(order_data.get("adres", "")).strip()
        if not adres:
            raise ValueError("Adres boş olamaz — geocoding için gereklidir.")

        islem = str(order_data.get("islem_tipi", "TESLIMAT")).upper()
        if islem not in (VALID_ISLEM - {"DEPO"}):
            raise ValueError(f"Geçersiz islem_tipi '{islem}' (TESLIMAT veya TOPLAMA olmalı).")

        kategori = str(order_data.get("kategori", "STANDART")).upper()
        if kategori not in (VALID_KATEGORI - {"DEPO"}):
            raise ValueError(f"Geçersiz kategori '{kategori}'.")

        agirlik = _to_pos_float(order_data.get("agirlik_kg", 2.5), "agirlik_kg")
        desi = _to_pos_float(order_data.get("desi", 8.0), "desi")

        zb = str(order_data.get("zaman_baslangic", "09:00")).strip()
        ze = str(order_data.get("zaman_bitis", "18:00")).strip()
        try:
            if _hhmm_to_min(zb) >= _hhmm_to_min(ze):
                raise ValueError(f"Zaman penceresi hatalı: başlangıç ({zb}) >= bitiş ({ze}).")
        except ValueError:
            raise
        except Exception:
            raise ValueError(f"Zaman formatı HH:MM olmalı (gelen: {zb} - {ze}).")

        try:
            servis = int(order_data.get("servis_suresi_dk", 5) or 5)
        except (TypeError, ValueError):
            raise ValueError("servis_suresi_dk tam sayı olmalı.")

        orders_df = pd.read_csv(self.orders_path)
        existing_nos = set(str(x) for x in orders_df["kargo_takip_no"])
        n = len(existing_nos)
        new_kargo_no = f"KP{n:03d}"
        while new_kargo_no in existing_nos:
            n += 1
            new_kargo_no = f"KP{n:03d}"

        atanan_arac = str(order_data.get("arac_id", "") or order_data.get("atanan_arac", "")).strip()

        new_row = {
            "kargo_takip_no": order_data.get("kargo_takip_no") or new_kargo_no,
            "musteri_adi": order_data.get("musteri_adi", "Yeni Müşteri"),
            "adres": adres,
            "islem_tipi": islem,
            "agirlik_kg": agirlik,
            "desi": desi,
            "kategori": kategori,
            "zaman_baslangic": zb,
            "zaman_bitis": ze,
            "servis_suresi_dk": servis,
        }
        if atanan_arac and atanan_arac not in ("OTOMATIK", "", "None", "-"):
            new_row["atanan_arac"] = atanan_arac

        updated_df = pd.concat([orders_df, pd.DataFrame([new_row])], ignore_index=True)

        tmp_path = str(self.orders_path) + ".tmp"
        updated_df.to_csv(tmp_path, index=False, encoding="utf-8")
        os.replace(tmp_path, self.orders_path)  

        self.run_full_pipeline(force_geocode=False)
        return self.get_dashboard_data()

    def address_autocomplete(self, query: str, limit: int = 5):
        """Adres için ORS otomatik tamamlama önerileri (Türkiye odaklı, ücretsiz).

        pelias_autocomplete kullanır (search ile aynı ücretsiz kota). En az 3
        karakterde çalışır. Dönüş: [{"label": tam adres, "lat":.., "lon":..}, ...]
        """
        q = (query or "").strip()
        if len(q) < 3 or not self.api_key:
            return []

        import openrouteservice
        client = openrouteservice.Client(key=self.api_key)
        ors_cfg = self.config.get("ors", {})
        country = ors_cfg.get("country_code", "TUR")
        focus = None
        if ors_cfg.get("focus_lon") is not None and ors_cfg.get("focus_lat") is not None:
            focus = (ors_cfg["focus_lon"], ors_cfg["focus_lat"])

        try:
            res = client.pelias_autocomplete(text=q, country=country, focus_point=focus)
        except Exception:
            try:
                res = client.pelias_search(text=q, country=country, focus_point=focus, size=limit)
            except Exception:
                return []

        out = []
        for f in (res.get("features") or [])[:limit]:
            props = f.get("properties", {}) or {}
            label = props.get("label") or props.get("name")
            coords = (f.get("geometry", {}) or {}).get("coordinates", [None, None])
            if label:
                out.append({"label": label, "lon": coords[0], "lat": coords[1]})
        return out

    def delete_order(self, kargo_takip_no):
        """Bir siparişi listeden kaldırır (atomik yazım) ve yeniden optimize eder."""
        kn = str(kargo_takip_no).strip()
        if not kn or kn == "0":
            raise ValueError("Geçersiz sipariş numarası.")
        df = pd.read_csv(self.orders_path, dtype=str)
        before = len(df)
        df = df[df["kargo_takip_no"].astype(str).str.strip() != kn]
        if len(df) == before:
            raise ValueError(f"Sipariş bulunamadı: {kn}")
        tmp = str(self.orders_path) + ".tmp"
        df.to_csv(tmp, index=False, encoding="utf-8")
        os.replace(tmp, self.orders_path)  
        self.run_full_pipeline(force_geocode=False)
        return self.get_dashboard_data()

    def delete_unserved(self):
        """Servis edilemeyen tüm siparişleri listeden kaldırır ve yeniden optimize eder."""
        data = self.get_dashboard_data()
        unserved = [str(x) for x in data.get("uyarilar", {}).get("servis_edilemeyen", [])]
        if not unserved:
            return data
        df = pd.read_csv(self.orders_path, dtype=str)
        df = df[~df["kargo_takip_no"].astype(str).str.strip().isin(unserved)]
        tmp = str(self.orders_path) + ".tmp"
        df.to_csv(tmp, index=False, encoding="utf-8")
        os.replace(tmp, self.orders_path)  
        self.run_full_pipeline(force_geocode=False)
        return self.get_dashboard_data()


service = OptimizationService()
