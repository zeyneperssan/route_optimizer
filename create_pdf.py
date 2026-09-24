"""
Kargo ERP Modül 0-8 Detaylı Rehberi PDF Oluşturucu
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from datetime import datetime

pdf_path = "KARGO_ERP_MODUL_0-8_DETAYLI_REHBER.pdf"
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    topMargin=0.5*inch,
    bottomMargin=0.5*inch,
    leftMargin=0.75*inch,
    rightMargin=0.75*inch
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=12,
    alignment=1
)

heading2_style = ParagraphStyle(
    'CustomHeading2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#2E5090'),
    spaceAfter=10,
    spaceBefore=10
)

heading3_style = ParagraphStyle(
    'CustomHeading3',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#4A7BA7'),
    spaceAfter=8
)

normal_style = ParagraphStyle(
    'CustomNormal',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    alignment=4  
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Normal'],
    fontSize=8,
    fontName='Courier',
    backColor=colors.HexColor('#f5f5f5'),
    leftIndent=10,
    rightIndent=10,
    spaceAfter=6,
    leading=11
)

story = []

story.append(Spacer(1, 2*inch))
story.append(Paragraph("KARGO DAĞITIM OPTİMİZASYON SİSTEMİ", title_style))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("Modül 0-8 Detaylı Kod ve İşleyiş Rehberi", heading2_style))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph(
    f"<b>Staj Projesi</b><br/>{datetime.now().strftime('%d Ağustos %Y')}<br/>Zeynep Ersan",
    normal_style
))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(
    "Python • OR-Tools • OpenRouteService • Pandas • Folium",
    normal_style
))
story.append(PageBreak())

story.append(Paragraph("İÇİNDEKİLER", heading2_style))
story.append(Spacer(1, 0.2*inch))

toc_items = [
    "1. Sistem Mimarisi Genel Bakış",
    "2. Modül 0: Kurulum ve İskelet",
    "3. Modül 1: Veri Okuma &amp; Doğrulama",
    "4. Modül 2: Geocoding (Adres → Koordinat)",
    "5. Modül 3: Gerçek Yol Matrisi",
    "6. Modül 4: Temel Dağıtım (Çift Kapasite)",
    "7. Modül 5: Heterojen Filo + Araç Uyumluluğu",
    "8. Modül 6: Zaman Pencereleri &amp; Servis Süresi",
    "9. Modül 7: SLA &amp; Gecikme Cezası",
    "10. Modül 8: Backhaul (Teslimat/Toplama)",
    "11. İntegrasyon &amp; Sonuç"
]

for item in toc_items:
    story.append(Paragraph(f"<b>•</b> {item}", normal_style))
    story.append(Spacer(1, 0.08*inch))

story.append(PageBreak())

story.append(Paragraph("1. SİSTEM MİMARİSİ GENEL BAKIŞ", heading2_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Pipeline Akışı (Ana Veri Akışı):</b>", heading3_style))
pipeline_text = """
<b>CSV Dosyaları</b> (siparisler, araclar)
→ <b>Modül 1</b> (Veri Okuma &amp; Doğrulama)
→ <b>Modül 2</b> (Geocoding: Adres→Koordinat)
→ <b>Modül 3</b> (Matris: Mesafe/Süre)
→ <b>Modül 4-5</b> (OR-Tools Model Kurma)
→ <b>Modül 6-8</b> (Kısıtları Ekleme)
→ <b>Çözücü</b> (30 saniye optimizasyon)
→ <b>Rotalar</b> (Durak sırası, mesafe, zaman)
→ <b>Görselleştirme</b> (Harita, rapor)
"""
story.append(Paragraph(pipeline_text, normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Proje Dosya Yapısı:</b>", heading3_style))
structure = """
<font face="Courier" size="8">
kargo_optimizer/
├── config.yaml                  # Konfigürasyon (hedef, parametreler)
├── .env                         # ORS_API_KEY (gizli)
├── main.py                      # Ana pipeline (tüm modülleri çalıştırır)
│
├── data/
│   ├── siparisler.csv           # Gönderi listesi (13 satır: 1 depo + 12 sipariş)
│   └── araclar.csv              # Filo bilgileri (3 araç: Moto, Panelvan, Kamyonet)
│
├── src/
│   ├── __init__.py
│   ├── config_loader.py         # (Modül 0) Config ve API Key yükleme
│   ├── loader.py                # (Modül 1) CSV okuma ve doğrulama
│   ├── geocode.py               # (Modül 2) Adres→(lat,lon) çevirme
│   ├── matrix.py                # (Modül 3) Mesafe/süre matrisi
│   ├── pickup.py                # (Modül 8) Backhaul (teslimat/toplama) mantığı
│   ├── model.py                 # (Modül 4-8) OR-Tools model kurma
│   ├── solve.py                 # (Modül 4/9) Çözücü ve rota çıkarma
│   ├── evaluate.py              # (Modül 10) KPI hesaplama
│   └── visualize.py             # (Modül 11) Folium harita çizimi
│
└── cache/
    ├── geocode_cache.json       # Adres→koordinat cache (API kota koruma)
    ├── matrix_cache.json        # Mesafe/süre cache
    ├── geocode_kontrol.html     # Doğrulama haritası
    └── rota_haritasi.html       # Final rotaların haritası
</font>
"""
story.append(Paragraph(structure, normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Teknoloji Yığını:</b>", heading3_style))
tech_table_data = [
    ['Katman', 'Araç', 'Kullanım'],
    ['Dil', 'Python 3.10+', 'Tüm proje'],
    ['Optimizasyon', 'Google OR-Tools', 'VRP çözücü'],
    ['Veri', 'Pandas', 'CSV işleme'],
    ['Geocoding/Matris', 'OpenRouteService', 'ORS API'],
    ['Görselleştirme', 'Folium', 'İnteraktif harita'],
    ['Config', 'YAML + python-dotenv', '.yaml ve .env'],
]
tech_table = Table(tech_table_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
]))
story.append(tech_table)
story.append(PageBreak())

story.append(Paragraph("2. MODÜL 0: KURULUM VE İSKELET", heading2_style))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph(
    "<b>Hedef:</b> Proje yapısını organize etmek, yapılandırma dosyalarını yüklemek ve OpenRouteService API anahtarını tanımlamak.",
    heading3_style
))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("<b>Adımlar:</b>", heading3_style))
steps0 = """
1. <b>Klasör Yapısı Oluştur:</b> src/, data/, cache/ klasörlerini kur
2. <b>config.yaml Oluştur:</b> Optimizasyon hedefi, ORS profili, çözücü parametreleri
3. <b>.env Dosyası:</b> ORS_API_KEY="..." yazarak API anahtarı gizle
4. <b>Test Et:</b> python main.py komutu ile başlangıçta config ve API anahtarı kontrol edilir
"""
story.append(Paragraph(steps0, normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Dosya: config.yaml</b>", heading3_style))
config_yaml = """
<font face="Courier" size="8">
# Hedef optimizasyon: distance (en kısa mesafe)
objective: "distance"

# Giriş verileri
data:
  orders_file: "data/siparisler.csv"
  vehicles_file: "data/araclar.csv"

# API cache'leri
cache:
  enabled: true
  geocode_cache_file: "cache/geocode_cache.json"
  matrix_cache_file: "cache/matrix_cache.json"
  rota_harita_file: "cache/rota_haritasi.html"

# OpenRouteService ayarları
ors:
  profile: "driving-car"       # Karayolu profili
  country_code: "TUR"          # Ülke kodu
  focus_lat: 40.997314         # Kadıköy şubesi (latitude)
  focus_lon: 29.044531         # Kadıköy şubesi (longitude)

# OR-Tools çözücü parametreleri
solver:
  time_limit_seconds: 30       # Maksimum 30 saniye arama
  first_solution_strategy: "PATH_CHEAPEST_ARC"
  local_search_metaheuristic: "GUIDED_LOCAL_SEARCH"
</font>
"""
story.append(Paragraph(config_yaml, code_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Dosya: .env (Gizli Kimlik Bilgileri)</b>", heading3_style))
env_content = """
<font face="Courier" size="9">
# OpenRouteService ücretsiz API anahtarı
# https://openrouteservice.org/ adresinden kaydolup al
ORS_API_KEY="YOUR_API_KEY_HERE"
</font>
"""
story.append(Paragraph(env_content, code_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Dosya: src/config_loader.py (Config Yükleme)</b>", heading3_style))
config_loader = """
<font face="Courier" size="8">
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

def load_config(path="config.yaml") -> dict:
    """config.yaml'ı YAML'dan oku ve sözlük olarak döndür"""
    cfg_path = ROOT / path
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_api_key() -> str | None:
    """.env'den ORS API anahtarını oku"""
    load_dotenv(ROOT / ".env")
    key = os.getenv("ORS_API_KEY")

    # Anahtar yoksa veya hâlâ şablon değerindeyse None döner
    if not key or key.strip() in ("", "senin_api_anahtarin_buraya"):
        return None

    return key.strip()
</font>
"""
story.append(Paragraph(config_loader, code_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Kullanım (main.py başında):</b>", heading3_style))
usage_m0 = """
<font face="Courier" size="8">
from src.config_loader import load_config, get_api_key

# Config yükle
config = load_config()
api_key = get_api_key()

print("=" * 52)
print(" KARGO DAĞITIM OPTİMİZASYONU")
print("=" * 52)
print(f"  Hedef (objective) : {config.get('objective')}")
print(f"  Sipariş dosyası    : {config['data']['orders_file']}")
print(f"  Araç dosyası       : {config['data']['vehicles_file']}")
print(f"  ORS anahtarı       : {'VAR' if api_key else 'YOK'}")
print("-" * 52)
</font>
"""
story.append(Paragraph(usage_m0, code_style))
story.append(PageBreak())

story.append(Paragraph("3. MODÜL 1: VERİ OKUMA &amp; DOĞRULAMA", heading2_style))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph(
    "<b>Hedef:</b> CSV dosyalarından sipariş ve araç verilerini okuyup geçerlilik doğrulaması yapmak.",
    heading3_style
))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("<b>Giriş Verisi: siparisler.csv Formatı</b>", heading3_style))
story.append(Spacer(1, 0.08*inch))

orders_sample = [
    ['kargo_takip_no', 'musteri_adi', 'adres', 'islem_tipi', 'agirlik_kg', 'desi', 'kategori', 'zaman_baslangic', 'zaman_bitis'],
    ['0', 'Kadikoy Sube', 'Hasanpasa...', 'DEPO', '0', '0', 'DEPO', '08:00', '20:00'],
    ['KP001', 'Alici - Moda', 'Caferaga...', 'TESLIMAT', '3.5', '12', 'STANDART', '09:00', '18:00'],
    ['KP005', 'Magaza Iadesi', 'Baglarbasi...', 'TOPLAMA', '5', '18', 'STANDART', '09:00', '18:00'],
    ['KP006', 'Alici - Kartal', 'Kordonboyu...', 'TESLIMAT', '40', '120', 'AGIR_YUK', '09:00', '18:00'],
]

orders_tbl = Table(orders_sample, colWidths=[0.8*inch, 1*inch, 1.2*inch, 0.8*inch, 0.7*inch, 0.6*inch, 0.8*inch, 0.7*inch, 0.7*inch])
orders_tbl.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 7),
    ('FONTSIZE', (0, 1), (-1, -1), 7),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
]))
story.append(orders_tbl)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Alanlar Açıklaması:</b>", heading3_style))
fields_desc = """
• <b>kargo_takip_no:</b> Gönderi barkodu (0 = depo)
• <b>musteri_adi:</b> Alıcı/gönderici ünvanı
• <b>adres:</b> Teslimat/toplama adresi (geocoding için giriş)
• <b>islem_tipi:</b> TESLIMAT, TOPLAMA veya DEPO
• <b>agirlik_kg:</b> Fiziksel ağırlık (kg)
• <b>desi:</b> Hacimsel büyüklük = (En × Boy × Yükseklik) / 3000
• <b>kategori:</b> STANDART, EXPRESS, AGIR_YUK veya DEPO
• <b>zaman_baslangic / zaman_bitis:</b> Teslim penceresi (HH:MM format)
• <b>servis_suresi_dk:</b> Adreste geçen hizmet süresi (dakika)
"""
story.append(Paragraph(fields_desc, normal_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Giriş Verisi: araclar.csv Formatı</b>", heading3_style))
story.append(Spacer(1, 0.08*inch))

vehicles_sample = [
    ['arac_id', 'arac_tipi', 'kapasite_kg', 'kapasite_desi', 'sabit_maliyet', 'km_maliyet', 'max_calisma_dk', 'max_durak_sayisi'],
    ['34-MOTO-01', 'MOTO_KURYE', '60', '50', '600', '3.5', '480', '25'],
    ['34-PNL-01', 'PANELVAN', '800', '400', '900', '7.5', '480', '40'],
    ['34-KMY-01', 'KAMYONET', '1500', '1000', '1200', '9.5', '480', '50'],
]

vehicles_tbl = Table(vehicles_sample, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 1*inch, 1*inch])
vehicles_tbl.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 7),
    ('FONTSIZE', (0, 1), (-1, -1), 7),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
]))
story.append(vehicles_tbl)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Kod: src/loader.py (Veri Okuma)</b>", heading3_style))
loader_code_m1 = """
<font face="Courier" size="7">
import pandas as pd

def load_orders(path: str) -> pd.DataFrame:
    """Sipariş CSV'sini okur ve veri tiplerini düzeltir"""
    df = pd.read_csv(path, dtype=str).fillna("")

    # Tüm sütunları text olarak oku, sonra tiplerini düzelt
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Sayısal alanlar
    df["agirlik_kg"] = pd.to_numeric(df["agirlik_kg"], errors="coerce")
    df["desi"] = pd.to_numeric(df["desi"], errors="coerce")
    df["servis_suresi_dk"] = pd.to_numeric(df["servis_suresi_dk"], errors="coerce")

    # Zaman penceresi: "HH:MM" formatından gün içi dakikaya çevir
    # Ör: 09:30 → 570 dakika, 23:59 → 1439 dakika
    def safe_hhmm_to_min(x):
        if not x or x == "":
            return pd.NA
        try:
            h, m = str(x).strip().split(":")
            return int(h) * 60 + int(m)
        except Exception as e:
            raise ValueError(f"Zaman formatı '{x}' hatalı (HH:MM olmalı): {e}")

    df["zaman_baslangic"] = df["zaman_baslangic"].apply(safe_hhmm_to_min)
    df["zaman_bitis"] = df["zaman_bitis"].apply(safe_hhmm_to_min)

    return df


def load_vehicles(path: str) -> pd.DataFrame:
    """Araç CSV'sini okur ve veri tiplerini düzeltir"""
    df = pd.read_csv(path, dtype=str).fillna("")
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Sayısal alanlar
    for col in ["kapasite_kg", "kapasite_desi", "sabit_maliyet",
                "km_maliyet", "max_calisma_dk", "max_durak_sayisi"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
</font>
"""
story.append(Paragraph(loader_code_m1, code_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Kod: src/loader.py (Doğrulama)</b>", heading3_style))
validate_code = """
<font face="Courier" size="7">
def validate(orders: pd.DataFrame, vehicles: pd.DataFrame) -> dict:
    """Veriyi doğrular; hata varsa yükseltir"""
    hatalar = []
    uyarilar = []

    # === Sipariş kontrolleri ===
    for i, r in orders.iterrows():
        etiket = r["kargo_takip_no"] or f"satır {i}"

        # Geçerli işlem tipi
        if r["islem_tipi"] not in {"TESLIMAT", "TOPLAMA", "DEPO"}:
            hatalar.append(f"{etiket}: geçersiz işlem_tipi '{r['islem_tipi']}'")

        # Geçerli kategori
        if r["kategori"] not in {"STANDART", "EXPRESS", "AGIR_YUK", "DEPO"}:
            hatalar.append(f"{etiket}: geçersiz kategori '{r['kategori']}'")

        # Ağırlık ve desi
        if pd.isna(r["agirlik_kg"]) or r["agirlik_kg"] < 0:
            hatalar.append(f"{etiket}: ağırlık_kg geçersiz")
        if pd.isna(r["desi"]) or r["desi"] < 0:
            hatalar.append(f"{etiket}: desi geçersiz")

        # Zaman pencereleri
        if (pd.notna(r["zaman_baslangic"]) and pd.notna(r["zaman_bitis"]) and
            r["zaman_baslangic"] >= r["zaman_bitis"]):
            hatalar.append(f"{etiket}: zaman penceresi hatalı (başlangıç >= bitiş)")

    # === Depo kontrolü ===
    depo = orders[orders["islem_tipi"] == "DEPO"]
    if len(depo) == 0:
        hatalar.append("Depo satırı yok (islem_tipi=DEPO olan bir satır olmalı)")
    elif len(depo) > 1:
        uyarilar.append("Birden çok DEPO satırı var; ilki kullanılacak")

    # === Talep vs Kapasite ===
    teslimat = orders[orders["islem_tipi"] == "TESLIMAT"]
    top_kg = teslimat["agirlik_kg"].sum()
    top_desi = teslimat["desi"].sum()
    filo_kg = vehicles["kapasite_kg"].sum()
    filo_desi = vehicles["kapasite_desi"].sum()

    if top_kg > filo_kg:
        uyarilar.append(f"Toplam teslimat ({top_kg:.0f} kg) "
                       f"filo kapasitesini ({filo_kg:.0f} kg) aşıyor")
    if top_desi > filo_desi:
        uyarilar.append(f"Toplam teslimat desisi ({top_desi:.0f}) "
                       f"filo desi kapasitesini ({filo_desi:.0f}) aşıyor")

    # Hatalar varsa exception fırlat
    if hatalar:
        raise ValueError("Veri doğrulama hataları:\n  - " +
                        "\n  - ".join(hatalar))

    # Özet bilgiler döndür
    return {
        "toplam_siparis": len(orders) - len(depo),
        "teslimat": len(teslimat),
        "toplama": len(orders) - len(teslimat) - len(depo),
        "toplam_teslimat_kg": top_kg,
        "toplam_teslimat_desi": top_desi,
        "filo_kapasite_kg": filo_kg,
        "filo_kapasite_desi": filo_desi,
        "arac_sayisi": len(vehicles),
        "uyarilar": uyarilar,
    }
</font>
"""
story.append(Paragraph(validate_code, code_style))
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("<b>Çıktı Örneği (main.py):</b>", heading3_style))
output_m1 = """
<font face="Courier" size="8">
Sipariş sayısı     : 12 (teslimat 9, toplama 3)
Toplam teslimat    : 106.5 kg / 316.0 desi
Filo kapasitesi    : 2360 kg / 1450 desi  (3 araç)
</font>
"""
story.append(Paragraph(output_m1, code_style))
story.append(PageBreak())

print("PDF Bölüm 1-3 tamamlandı. Devamı yazılıyor...")

doc.build(story)
print(f"\n✅ PDF oluşturuldu: {pdf_path}")
print(f"   Toplam sayfa: ~{len(story)//20} sayfa")
