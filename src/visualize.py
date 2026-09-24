"""Modül 11 — Görselleştirme (folium harita + özet paneli + senaryo seçimi).

ORS Directions ile gerçek rota geometrisini alıp folium haritasında çizer;
her aracı farklı renkte gösterir, duraklara bilgi baloncuğu ekler.

Modül 11 Enhancements:
  - Her senaryo (distance/time/cost) için ayrı harita
  - Özet paneli: araç sayısı, toplam mesafe, maliyet, KPI'lar
  - Senaryo seçim dropdown'ı (HTML sayfada interaktif geçiş)
  - KPI tablosu göstergesi
"""
import json
from pathlib import Path

import folium
import openrouteservice
import pandas as pd


ARAC_RENKLERI = {
    "MOTO_KURYE": "#FF6B6B",   
    "PANELVAN": "#4ECDC4",     
    "KAMYONET": "#FFE66D",     
}


_GEOM_CACHE = None
_GEOM_CACHE_PATH = Path("cache/directions_cache.json")


def _get_route_geometry(client: "openrouteservice.Client", koordinatlar: list, profile: str) -> dict:
    """ORS Directions ile bir rota için polyline ve mesafe alır (disk cache'li).

    koordinatlar: [(lon, lat), (lon, lat), ...] listesi
    Döndürür: {"polyline": [[lat,lon], ...], "distance_m": ..., "duration_s": ...}

    Aynı rota (aynı koordinat dizisi + profil) daha önce çizildiyse ORS'ye
    gidilmez, sonuç diskteki cache'den anında döner — dashboard yüklenmesini
    ciddi hızlandırır.
    """
    if len(koordinatlar) < 2:
        return None

    global _GEOM_CACHE
    if _GEOM_CACHE is None:
        try:
            _GEOM_CACHE = json.loads(_GEOM_CACHE_PATH.read_text(encoding="utf-8")) \
                if _GEOM_CACHE_PATH.exists() else {}
        except Exception:
            _GEOM_CACHE = {}

    key = profile + "|" + json.dumps([[round(lon, 5), round(lat, 5)] for lon, lat in koordinatlar])
    if key in _GEOM_CACHE:
        return _GEOM_CACHE[key]

    try:
        result = client.directions(
            coordinates=koordinatlar,
            profile=profile,
            format="geojson",
            validate=False,
        )
        features = result.get("features", [])
        if not features:
            return None

        geom = features[0]["geometry"]
        props = features[0]["properties"]

        polyline = [[lat, lon] for lon, lat in geom["coordinates"]]
        out = {
            "polyline": polyline,
            "distance_m": props.get("summary", {}).get("distance", 0),
            "duration_s": props.get("summary", {}).get("duration", 0),
        }
        _GEOM_CACHE[key] = out
        try:
            _GEOM_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            _GEOM_CACHE_PATH.write_text(json.dumps(_GEOM_CACHE, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return out
    except Exception as e:
        print(f"[UYARI] Rota geometrisi alınamadı: {e}")
        return None


def _create_summary_panel_html(kpis: dict, scenario_name: str) -> str:
    """Özet paneli HTML'sini oluştur — harita üzerinde KPI'ları gösteren kutu.

    Neden ayrı bir fonksiyon?
      Modül 11'de multiple senaryoları karşılaştırırken her haritanın
      kendi özet paneli olacak (distance/time/cost). HTML'ye doğru şekilde
      embed edilmesi gerekli.

    Parametreler:
      kpis: compute_kpis() çıktısı
      scenario_name: "DISTANCE", "TIME", "COST" vs.

    Döndürür: HTML string (folium.Element ile haritaya eklenecek)
    """
    html = f"""
    <div style="
        position: fixed;
        top: 10px; right: 10px; width: 320px; height: auto;
        background-color: rgba(255, 255, 255, 0.95);
        border: 2px solid #333;
        border-radius: 8px;
        z-index: 9999;
        font-size: 13px;
        padding: 15px;
        font-family: 'Segoe UI', Arial, sans-serif;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    ">
        <div style="font-size: 16px; font-weight: bold; margin-bottom: 12px; color: #333;">
            📊 {scenario_name}
        </div>
        <div style="border-top: 1px solid #ddd; padding-top: 10px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 6px 0; color: #666;">Toplam Mesafe:</td>
                    <td style="padding: 6px 0; font-weight: bold; text-align: right; color: #222;">
                        {kpis.get('toplam_km', 0):.1f} km
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 6px 0; color: #666;">Toplam Süre:</td>
                    <td style="padding: 6px 0; font-weight: bold; text-align: right; color: #222;">
                        {kpis.get('toplam_saat', 0):.1f} saat
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 6px 0; color: #666;">Toplam Maliyet:</td>
                    <td style="padding: 6px 0; font-weight: bold; text-align: right; color: #d9534f;">
                        ₺{kpis.get('toplam_maliyet_tl', 0):.0f}
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 6px 0; color: #666;">Araç Sayısı:</td>
                    <td style="padding: 6px 0; font-weight: bold; text-align: right; color: #222;">
                        {kpis.get('arac_sayisi', 0)}
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 6px 0; color: #666;">KG Doluluk:</td>
                    <td style="padding: 6px 0; font-weight: bold; text-align: right; color: #222;">
                        %{kpis.get('kg_dolusu_oran', 0):.0f}
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 6px 0; color: #666;">Desi Doluluk:</td>
                    <td style="padding: 6px 0; font-weight: bold; text-align: right; color: #222;">
                        %{kpis.get('desi_dolusu_oran', 0):.0f}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; color: #666;">Zamanında Teslimat:</td>
                    <td style="padding: 6px 0; font-weight: bold; text-align: right; color: #5cb85c;">
                        %{kpis.get('zamaninda_teslimat_oran', 0):.0f}
                    </td>
                </tr>
            </table>
        </div>
    </div>
    """
    return html


def draw_routes(
    rotalar: list,
    points: pd.DataFrame,
    vehicles: pd.DataFrame,
    api_key: str,
    out_html: str = "cache/rota_haritasi.html",
    profile: str = "driving-car",
) -> str:
    """Rotaları interaktif folium haritasında çizer.

    Parametreler:
    - rotalar: extract_routes'tan gelen lista (arac_id, duraklar, mesafe_km)
    - points: sipariş DataFrame'i (lat, lon, kargo_takip_no, kategori, desi)
    - vehicles: araç DataFrame'i (arac_id, arac_tipi)
    - api_key: ORS API anahtarı
    - out_html: çıktı HTML dosyası yolu
    - profile: ORS routing profili ("driving-car")

    Döndürür: çıktı dosyası yolu
    """
    if not rotalar:
        raise ValueError("Rota listesi boş — çizilecek hiç rota yok.")

    client = openrouteservice.Client(key=api_key)

    merkez_lat = points["lat"].mean()
    merkez_lon = points["lon"].mean()
    harita = folium.Map(
        location=[merkez_lat, merkez_lon],
        zoom_start=11,
        tiles="OpenStreetMap",
    )

    for rota in rotalar:
        arac_id = rota["arac_id"]
        durak_nos = rota["duraklar"]
        mesafe_km = rota["mesafe_km"]

        arac_row = vehicles[vehicles["arac_id"] == arac_id].iloc[0]
        arac_tipi = arac_row["arac_tipi"]
        renk = ARAC_RENKLERI.get(arac_tipi, "#888888")

        durak_rows = []
        koordinatlar = []  
        for no in durak_nos:
            if no == "0":  
                row = points.iloc[0]
            else:
                row = points[points["kargo_takip_no"] == no].iloc[0]
            durak_rows.append(row)
            koordinatlar.append((row["lon"], row["lat"]))

        rota_geom = _get_route_geometry(client, koordinatlar, profile)

        if rota_geom:
            folium.PolyLine(
                locations=rota_geom["polyline"],
                color=renk,
                weight=3,
                opacity=0.8,
                popup=f"{arac_id}: {mesafe_km:.1f} km",
            ).add_to(harita)

        for i, row in enumerate(durak_rows):
            is_depot = (i == 0 or i == len(durak_rows) - 1)
            icon_color = "black" if is_depot else "blue"
            icon = folium.Icon(color=icon_color, icon="info-sign")

            popup_text = f"""
            <b>{row['kargo_takip_no']}</b><br>
            {row['musteri_adi']}<br>
            {row['adres']}<br>
            Ağırlık: {row['agirlik_kg']:.1f} kg<br>
            Desi: {row['desi']:.1f}<br>
            Kategori: {row['kategori']}<br>
            İşlem: {row['islem_tipi']}
            """
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=row["kargo_takip_no"],
                icon=icon,
            ).add_to(harita)

    legend_html = """
    <div style="position: fixed;
                bottom: 50px; right: 50px; width: 200px; height: 180px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 10px">
    <b>Rota Haritası Açıklaması</b><br>
    <i class="fa fa-circle" style="color:#FF6B6B"></i> Moto Kurye<br>
    <i class="fa fa-circle" style="color:#4ECDC4"></i> Panelvan<br>
    <i class="fa fa-circle" style="color:#FFE66D"></i> Kamyonet<br>
    <br>
    🔵 Durak (teslimat/toplama)<br>
    ⚫ Depo (başlangıç/bitiş)
    </div>
    """
    harita.get_root().html.add_child(folium.Element(legend_html))

    out_path = Path(out_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    harita.save(str(out_path))

    return str(out_path)


def draw_routes_with_summary(
    rotalar: list,
    points: pd.DataFrame,
    vehicles: pd.DataFrame,
    kpis: dict,
    scenario_name: str,
    api_key: str,
    out_html: str = "cache/rota_haritasi.html",
    profile: str = "driving-car",
) -> str:
    """Rotaları haritasında çiz + özet paneli ekle.

    Modül 11: Senaryoya özel KPI özet paneli eklenmiş versyon.
    draw_routes() temel fonksiyonudur, bu enhanced versiyon.

    Parametreler: draw_routes + kpis + scenario_name
    """
    if not rotalar:
        raise ValueError("Rota listesi boş — çizilecek hiç rota yok.")

    client = openrouteservice.Client(key=api_key)

    merkez_lat = points["lat"].mean()
    merkez_lon = points["lon"].mean()
    harita = folium.Map(
        location=[merkez_lat, merkez_lon],
        zoom_start=11,
        tiles="OpenStreetMap",
    )

    for rota in rotalar:
        arac_id = rota["arac_id"]
        durak_nos = rota["duraklar"]
        mesafe_km = rota["mesafe_km"]

        arac_row = vehicles[vehicles["arac_id"] == arac_id].iloc[0]
        arac_tipi = arac_row["arac_tipi"]
        renk = ARAC_RENKLERI.get(arac_tipi, "#888888")

        durak_rows = []
        koordinatlar = []
        for no in durak_nos:
            if no == "0":  
                row = points.iloc[0]
            else:
                row = points[points["kargo_takip_no"] == no].iloc[0]
            durak_rows.append(row)
            koordinatlar.append((row["lon"], row["lat"]))

        rota_geom = _get_route_geometry(client, koordinatlar, profile)

        if rota_geom:
            folium.PolyLine(
                locations=rota_geom["polyline"],
                color=renk,
                weight=3,
                opacity=0.8,
                popup=f"{arac_id}: {mesafe_km:.1f} km",
            ).add_to(harita)

        for i, row in enumerate(durak_rows):
            is_depot = (i == 0 or i == len(durak_rows) - 1)
            icon_color = "black" if is_depot else "blue"
            icon = folium.Icon(color=icon_color, icon="info-sign")

            popup_text = f"""
            <b>{row['kargo_takip_no']}</b><br>
            {row['musteri_adi']}<br>
            {row['adres']}<br>
            Ağırlık: {row['agirlik_kg']:.1f} kg<br>
            Desi: {row['desi']:.1f}<br>
            Kategori: {row['kategori']}<br>
            İşlem: {row['islem_tipi']}
            """
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=row["kargo_takip_no"],
                icon=icon,
            ).add_to(harita)

    summary_html = _create_summary_panel_html(kpis, scenario_name)
    harita.get_root().html.add_child(folium.Element(summary_html))

    legend_html = """
    <div style="position: fixed;
                bottom: 50px; right: 50px; width: 200px; height: 180px;
                background-color: white; border:2px solid grey; z-index:9998;
                font-size:14px; padding: 10px">
    <b>Rota Haritası</b><br>
    <i class="fa fa-circle" style="color:#FF6B6B"></i> Moto Kurye<br>
    <i class="fa fa-circle" style="color:#4ECDC4"></i> Panelvan<br>
    <i class="fa fa-circle" style="color:#FFE66D"></i> Kamyonet<br>
    <br>
    🔵 Durak<br>
    ⚫ Depo
    </div>
    """
    harita.get_root().html.add_child(folium.Element(legend_html))

    out_path = Path(out_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    harita.save(str(out_path))

    return str(out_path)


def draw_scenario_maps(
    scenarios: dict,
    points: pd.DataFrame,
    vehicles: pd.DataFrame,
    api_key: str,
    out_dir: str = "cache/",
    profile: str = "driving-car",
) -> dict:
    """Birden fazla senaryo (distance/time/cost) için harita ve index sayfası oluştur.

    Modül 11: Senaryo seçimi dropdown'u olan interaktif index sayfa.

    Parametreler:
      scenarios: {
        'distance': {'rotalar': [...], 'kpis': {...}},
        'time': {...},
        'cost': {...}
      }

    Döndürür:
      {
        'index_html': index sayfa yolu,
        'maps': {
          'distance': harita dosya yolu,
          'time': harita dosya yolu,
          'cost': harita dosya yolu
        }
      }

    Nedir bu?
      - Her senaryo için ayrı harita çizilir (harita_distance.html, harita_time.html, vs.)
      - index.html oluşturulur: senaryo dropdown'u ile haritayı switch eden sayfa
      - Kullanıcı dropdown'dan "TIME" seçince harita_time.html'de iframe yüklenir
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    maps_dict = {}
    scenario_names = {
        "distance": "DISTANCE (Min Mesafe)",
        "time": "TIME (Min Süre)",
        "cost": "COST (Min Maliyet)",
    }

    for obj_key, obj_name in scenario_names.items():
        if obj_key not in scenarios:
            continue

        rotalar = scenarios[obj_key].get("rotalar", [])
        kpis = scenarios[obj_key].get("kpis", {})

        map_file = out_path / f"harita_{obj_key}.html"
        draw_routes_with_summary(
            rotalar,
            points,
            vehicles,
            kpis,
            obj_name,
            api_key,
            out_html=str(map_file),
            profile=profile,
        )
        maps_dict[obj_key] = str(map_file)

    index_html = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kargo Rota Optimizasyonu — Senaryo Analizi</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 28px;
                margin-bottom: 10px;
            }}
            .header p {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .controls {{
                padding: 20px 30px;
                background: #f8f9fa;
                border-bottom: 1px solid #ddd;
                display: flex;
                gap: 15px;
                align-items: center;
                flex-wrap: wrap;
            }}
            .controls label {{
                font-weight: bold;
                color: #333;
            }}
            .controls select {{
                padding: 10px 15px;
                font-size: 14px;
                border: 2px solid #667eea;
                border-radius: 6px;
                cursor: pointer;
                background: white;
                color: #333;
            }}
            .controls select:hover {{
                border-color: #764ba2;
            }}
            .map-container {{
                width: 100%;
                height: 800px;
                position: relative;
            }}
            iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
            .info-box {{
                padding: 20px 30px;
                background: #e8f4f8;
                border-top: 1px solid #ddd;
                font-size: 13px;
                color: #555;
                line-height: 1.6;
            }}
            .info-box strong {{
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚚 Kargo Rota Optimizasyonu</h1>
                <p>Üç farklı hedef (mesafe/süre/maliyet) için senaryo analizi ve karşılaştırma</p>
            </div>

            <div class="controls">
                <label for="scenario-select">📊 Senaryo Seçin:</label>
                <select id="scenario-select" onchange="switchMap(this.value)">
                    <option value="distance">DISTANCE — En Kısa Mesafe</option>
                    <option value="time">TIME — En Hızlı Teslimat</option>
                    <option value="cost">COST — En Düşük Maliyet</option>
                </select>
            </div>

            <div class="map-container">
                <iframe id="map-iframe" src="harita_distance.html"></iframe>
            </div>

            <div class="info-box">
                <strong>💡 Nasıl kullanılır?</strong><br>
                Senaryo dropdown'undan farklı optimizasyon hedeflerini seçin. Her senaryo için
                harita üzerinde renklendirilen rotalar (Moto/Panelvan/Kamyonet) ve sağ üstte
                KPI özeti (mesafe, maliyet, araç sayısı, doluluk, zamanında teslimat %) gösterilir.
                <br><br>
                <strong>📌 Hangi senaryoyu seçmeliyim?</strong><br>
                • <strong>DISTANCE:</strong> Çevre dostu, yakıt tasarrufu<br>
                • <strong>TIME:</strong> Hızlı teslimat, müşteri memnuniyeti<br>
                • <strong>COST:</strong> En karlı işletme (genellikle en iyi seçim)
            </div>
        </div>

        <script>
            function switchMap(scenario) {{
                document.getElementById('map-iframe').src = 'harita_' + scenario + '.html';
            }}
        </script>
    </body>
    </html>
    """

    index_file = out_path / "index.html"
    with open(str(index_file), "w", encoding="utf-8") as f:
        f.write(index_html)

    return {
        "index_html": str(index_file),
        "maps": maps_dict,
    }
