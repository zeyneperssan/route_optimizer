"""Kargo Dağıtım Optimizasyonu — ana akış (pipeline).

Akış: veri -> geocode -> matris -> model -> çöz -> değerlendir -> görselleştir
Modüller tamamlandıkça aşağıdaki adımlar tek tek açılacak.

Çalıştırma (proje kök dizininde):
    python main.py
"""
import sys
from src.config_loader import load_config, get_api_key

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    config = load_config()
    api_key = get_api_key()

    print("=" * 52)
    print(" KARGO DAĞITIM OPTİMİZASYONU")
    print("=" * 52)
    print(f"  Hedef (objective) : {config.get('objective')}")
    print(f"  Sipariş dosyası    : {config['data']['orders_file']}")
    print(f"  Araç dosyası       : {config['data']['vehicles_file']}")
    print(f"  ORS anahtarı       : {'VAR' if api_key else 'YOK (.env dosyasına ekleyin)'}")
    print("-" * 52)

    from src.loader import load_orders, load_vehicles, validate
    orders = load_orders(config['data']['orders_file'])
    vehicles = load_vehicles(config['data']['vehicles_file'])
    ozet = validate(orders, vehicles)

    print(f"  Sipariş sayısı     : {ozet['toplam_siparis']} "
          f"(teslimat {ozet['teslimat']}, toplama {ozet['toplama']})")
    print(f"  Toplam teslimat    : {ozet['toplam_teslimat_kg']:.1f} kg / "
          f"{ozet['toplam_teslimat_desi']:.1f} desi")
    print(f"  Filo kapasitesi    : {ozet['filo_kapasite_kg']:.0f} kg / "
          f"{ozet['filo_kapasite_desi']:.0f} desi  ({ozet['arac_sayisi']} araç)")
    for u in ozet['uyarilar']:
        print(f"  [UYARI] {u}")
    print("-" * 52)

    if not api_key:
        print("  [ATLANDI] Modül 2 (geocoding) için ORS anahtarı gerekli.")
    else:
        from src.geocode import geocode_addresses, summarize_geocode, save_verification_map
        ors_cfg = config['ors']
        focus_point = None
        if ors_cfg.get('focus_lon') is not None and ors_cfg.get('focus_lat') is not None:
            focus_point = (ors_cfg['focus_lon'], ors_cfg['focus_lat'])
        orders = geocode_addresses(
            orders,
            api_key,
            cache_path=config['cache']['geocode_cache_file'],
            country_code=ors_cfg.get('country_code'),
            focus_point=focus_point,
        )
        geo_ozet = summarize_geocode(orders)
        print(f"  Geocode edilen adres : {geo_ozet['basarili']}/{geo_ozet['toplam']} başarılı")
        if geo_ozet['basarisiz']:
            print(f"  [UYARI] Koordinat bulunamayan adresler: {geo_ozet['basarisiz_adresler']}")
        harita_yolu = save_verification_map(orders)
        print(f"  Doğrulama haritası   : {harita_yolu} (tarayıcıda açıp noktaları kontrol edin)")
    print("-" * 52)

    if not api_key or "lat" not in orders.columns:
        print("  [ATLANDI] Modül 3 (matris) için önce Modül 2 (geocoding) gerekli.")
    else:
        from src.matrix import build_matrix, summarize_matrix
        dist_m, dur_s, points = build_matrix(
            orders,
            api_key,
            cache_path=config['cache']['matrix_cache_file'],
            profile=config['ors']['profile'],
        )
        mat_ozet = summarize_matrix(points, dist_m, dur_s)
        en_uzun_a, en_uzun_b, en_uzun_km = mat_ozet['en_uzun_mesafe']
        print(f"  Matris boyutu        : {mat_ozet['nokta_sayisi']} x {mat_ozet['nokta_sayisi']}")
        print(f"  Ortalama mesafe/süre : {mat_ozet['ortalama_mesafe_km']:.1f} km / "
              f"{mat_ozet['ortalama_sure_dk']:.1f} dk")
        print(f"  En uzun bağlantı     : {en_uzun_a} -> {en_uzun_b} ({en_uzun_km:.1f} km)")
        if mat_ozet['yol_vs_kus_ucusu_ortalama_oran']:
            print(f"  Yol / kuş uçuşu oranı: ortalama {mat_ozet['yol_vs_kus_ucusu_ortalama_oran']:.2f}x, "
                  f"en yüksek {mat_ozet['yol_vs_kus_ucusu_en_yuksek_oran']:.2f}x")
    print("-" * 52)

    if not api_key or "lat" not in orders.columns:
        print("  [ATLANDI] Modül 4-5 için önce Modül 2-3 (geocoding + matris) gerekli.")
    else:
        from src.model import build_model
        from src.solve import solve, extract_routes
        routing, manager = build_model(points, vehicles, dist_m, dur_s)
        solution = solve(routing, manager, config)
        rotalar = extract_routes(routing, manager, solution, points, vehicles, dist_m, dur_s)

        print(f"  ✓ MODÜL 4: Çift kapasite (kg + desi), çok araç")
        print(f"  ✓ MODÜL 5: Heterojen filo, sabit maliyet, max durak sınırı\n")

        print(f"  Kullanılan araç      : {len(rotalar)}/{len(vehicles)}")
        toplam_maliyet_tl = 0
        for r in rotalar:
            arac = vehicles[vehicles["arac_id"] == r["arac_id"]].iloc[0]
            sabit = arac["sabit_maliyet"]
            km_maliyet = arac["km_maliyet"]
            toplam = sabit + (r["mesafe_km"] * km_maliyet)
            toplam_maliyet_tl += toplam
            print(f"    {r['arac_id']:<12} {len(r['duraklar'])-2:2d} durak  "
                  f"{r['mesafe_km']:6.1f} km  ₺{toplam:7.2f}")
        print(f"  Toplam maliyet       : ₺{toplam_maliyet_tl:.2f}")
    print("-" * 52)
    print("=" * 52)

    if not api_key or "lat" not in orders.columns:
        print("  [ATLANDI] Modül 6-8 için önce Modül 2-3 (geocoding + matris) gerekli.")
    else:
        from src.model import build_model
        from src.solve import solve, extract_routes
        routing, manager = build_model(points, vehicles, dist_m, dur_s)
        solution = solve(routing, manager, config)
        rotalar = extract_routes(routing, manager, solution, points, vehicles, dist_m, dur_s)

        print(f"\n  ✓ MODÜL 6: Zaman pencereleri + servis süresi + vardiya sınırı")
        print(f"  ✓ MODÜL 7: Soft time windows (SLA/gecikme cezası) — EXPRESS/STANDART")
        print(f"  ✓ MODÜL 8: Backhaul (toplama/iade) hazırlandı\n")

        print(f"  Kullanılan araç      : {len(rotalar)}/{len(vehicles)}")
        toplam_maliyet_tl = 0
        for r in rotalar:
            arac = vehicles[vehicles["arac_id"] == r["arac_id"]].iloc[0]
            sabit = arac["sabit_maliyet"]
            km_maliyet = arac["km_maliyet"]
            toplam = sabit + (r["mesafe_km"] * km_maliyet)
            toplam_maliyet_tl += toplam
            print(f"    {r['arac_id']:<12} {len(r['duraklar'])-2:2d} durak  "
                  f"{r['mesafe_km']:6.1f} km  ₺{toplam:7.2f}")
            if "durak_zamanlar_dk" in r:
                print(f"                 Varış zamanları (dk): {r['durak_zamanlar_dk'][:3]}...")

        print(f"  Toplam maliyet       : ₺{toplam_maliyet_tl:.2f}")

        from src.visualize import draw_routes
        harita_yolu = draw_routes(
            rotalar, points, vehicles, api_key,
            out_html=config['cache'].get('rota_harita_file', 'cache/rota_haritasi.html'),
            profile=config['ors']['profile']
        )
        print(f"  Rota haritası        : {harita_yolu} (tarayıcıda açıp rotaları kontrol edin)")
    print("-" * 52)
    print("  Modül 6-8 tamam. Tüm kısıtlar aktif.")
    print("=" * 52)

    print("\n" + "=" * 70)
    print(" 🔄 MODÜL 9: MALİYET MODELİ + ÇOK AMAÇLI SENARYO")
    print("=" * 70)

    if not api_key or "lat" not in orders.columns:
        print("  [ATLANDI] Modül 9 için önce Modül 2-3 (geocoding + matris) gerekli.")
    else:
        from src.model import build_model
        from src.solve import solve, extract_routes
        from src.evaluate import compute_kpis

        scenarios = {}

        for objective in ["distance", "time", "cost"]:
            print(f"\n  🔷 Senaryo: {objective.upper()}")
            print(f"    Kuruluyor...", end="", flush=True)

            routing, manager = build_model(points, vehicles, dist_m, dur_s, objective=objective)
            solution = solve(routing, manager, config, objective=objective)
            rotalar = extract_routes(routing, manager, solution, points, vehicles, dist_m, dur_s)

            print(f" ✓")

            kpis = compute_kpis(rotalar, points, vehicles, orders)
            scenarios[objective] = {
                "rotalar": rotalar,
                "kpis": kpis,
            }

            print(f"    Mesafe      : {kpis['toplam_km']:.1f} km")
            print(f"    Süre        : {kpis['toplam_saat']:.1f} saat")
            print(f"    Maliyet     : ₺{kpis['toplam_maliyet_tl']:.0f}")
            print(f"    Araç sayısı : {kpis['arac_sayisi']}")
            print(f"    Zamanında   : %{kpis['zamaninda_teslimat_oran']:.0f}")

        print("\n" + "=" * 85)
        print(" SENARYO KARŞILAŞTIRMASI")
        print("=" * 85)

        print(f"{'Senaryo':<12} {'Mesafe':>10} {'Süre':>10} {'Maliyet':>10} "
              f"{'Araç':>6} {'KG%':>6} {'Desi%':>7} {'Zamanında':>10}")
        print("-" * 85)

        for objective in ["distance", "time", "cost"]:
            kpis = scenarios[objective]["kpis"]
            obj_name = {
                "distance": "DISTANCE",
                "time": "TIME",
                "cost": "COST"
            }[objective]

            print(f"{obj_name:<12} {kpis['toplam_km']:>9.1f} km "
                  f"{kpis['toplam_saat']:>9.1f} h "
                  f"₺{kpis['toplam_maliyet_tl']:>8.0f} "
                  f"{kpis['arac_sayisi']:>6} "
                  f"{kpis['kg_dolusu_oran']:>5.0f}% "
                  f"{kpis['desi_dolusu_oran']:>6.0f}% "
                  f"{kpis['zamaninda_teslimat_oran']:>9.0f}%")

        print("=" * 85)

        best_distance = min(scenarios.items(), key=lambda x: x[1]["kpis"]["toplam_km"])
        best_time = min(scenarios.items(), key=lambda x: x[1]["kpis"]["toplam_saat"])
        best_cost = min(scenarios.items(), key=lambda x: x[1]["kpis"]["toplam_maliyet_tl"])

        print(f"\n  💡 ÖNERİLER:")
        print(f"    📊 Çevre dostu (min mesafe)     → {best_distance[0].upper()}: {best_distance[1]['kpis']['toplam_km']:.1f} km")
        print(f"    ⏱️  Hızlı teslimat (min süre)   → {best_time[0].upper()}: {best_time[1]['kpis']['toplam_saat']:.1f} saat ({best_time[1]['kpis']['toplam_km']:.1f} km)")
        print(f"    💰 Karlı işletme (min maliyet) → {best_cost[0].upper()}: ₺{best_cost[1]['kpis']['toplam_maliyet_tl']:.0f}")
        print("=" * 85)

        print(f"\n  📈 TRADE-OFF ANALİZİ:")
        print(f"    • Mesafe vs Maliyet: COST senaryo {best_distance[1]['kpis']['toplam_km'] - best_cost[1]['kpis']['toplam_km']:.1f} km daha kısa")
        print(f"                        ₺{best_distance[1]['kpis']['toplam_maliyet_tl'] - best_cost[1]['kpis']['toplam_maliyet_tl']:.0f} fazla maliyet")
        print(f"    • Maliyet vs Süre: TIME senaryo ₺{best_cost[1]['kpis']['toplam_maliyet_tl'] - best_time[1]['kpis']['toplam_maliyet_tl']:.0f} daha ucuz")
        print(f"    • Seçim: İşletme karlılığını optimize etmek için TIME senaryo kullanın")
        print("=" * 85)

        print("\n" + "=" * 85)
        print(" 📊 MODÜL 10: KPI RAPORU VE BASELINE KARŞILAŞTIRMASI")
        print("=" * 85)

        from src.kpi_report import generate_comparison_report, print_kpi_report

        comparison_df = generate_comparison_report(scenarios, points, vehicles)

        print_kpi_report(comparison_df)

        report_csv = config['cache'].get('kpi_report_file', 'cache/kpi_raporu.csv')
        comparison_df.to_csv(report_csv, index=False, encoding='utf-8')
        print(f"\n  📄 KPI raporu CSV'ye kaydedildi: {report_csv}")

        print("\n" + "=" * 85)
        print(" 🗺️  MODÜL 11: GÖRSELLEŞTİRME (FOLIUM + ÖZET + SENARYO SEÇİMİ)")
        print("=" * 85)

        from src.visualize import draw_scenario_maps

        maps_result = draw_scenario_maps(
            scenarios,
            points,
            vehicles,
            api_key,
            out_dir=config['cache'].get('maps_dir', 'cache/'),
            profile=config['ors']['profile']
        )

        index_html = maps_result['index_html']
        maps_files = maps_result['maps']

        print(f"\n  ✅ İnteraktif harita sayıları oluşturuldu:")
        print(f"    • Index sayfası (senaryo seçici) : {index_html}")
        for scenario, map_file in maps_files.items():
            print(f"    • {scenario.upper()} haritası      : {map_file}")

        print(f"\n  🌐 Tarayıcıda açmak için:")
        print(f"     → {index_html}")
        print("\n  💡 Index sayfasından dropdown menüde senaryo seçerek haritaları karşılaştırabilirsiniz.")
        print("=" * 85)


if __name__ == "__main__":
    main()
