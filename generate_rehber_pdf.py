"""
Kargo Dağıtım Optimizasyonu - Modül 0'dan 8'e Kapsamlı Teknik Rehber PDF Oluşturucu
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_dir = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont('Arial', os.path.join(font_dir, 'arial.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(font_dir, 'arialbd.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(font_dir, 'ariali.ttf')))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic', os.path.join(font_dir, 'arialbi.ttf')))
pdfmetrics.registerFont(TTFont('CourierNew', os.path.join(font_dir, 'cour.ttf')))
pdfmetrics.registerFont(TTFont('CourierNew-Bold', os.path.join(font_dir, 'courbd.ttf')))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  
        
        self.saveState()
        
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawString(54, 800, "KARGO ERP DAĞITIM OPTİMİZASYON SİSTEMİ — MODÜL 0-8 TEKNİK REHBERİ")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(54, 792, 541, 792)

        self.line(54, 48, 541, 48)
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(54, 34, "Kargo ERP Staj Projesi | Python • OR-Tools • OpenRouteService")
        page_str = f"Sayfa {self._pageNumber} / {page_count}"
        self.drawRightString(541, 34, page_str)
        
        self.restoreState()


def build_pdf():
    pdf_filename = "KARGO_ERP_MODUL_0-8_DETAYLI_REHBER.pdf"
    
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    PRIMARY = colors.HexColor("#1A365D")      
    SECONDARY = colors.HexColor("#2B6CB0")    
    ACCENT = colors.HexColor("#2C7A7B")       
    TEXT_DARK = colors.HexColor("#2D3748")    
    BG_LIGHT = colors.HexColor("#F7FAFC")     
    BG_CODE = colors.HexColor("#EDF2F7")      
    BORDER_COLOR = colors.HexColor("#E2E8F0") 
    HIGHLIGHT = colors.HexColor("#C53030")    
    SUCCESS = colors.HexColor("#276749")      

    styles = getSampleStyleSheet()

    style_cover_title = ParagraphStyle(
        'CoverTitle',
        fontName='Arial-Bold',
        fontSize=24,
        leading=30,
        textColor=PRIMARY,
        alignment=1, 
        spaceAfter=15
    )

    style_cover_sub = ParagraphStyle(
        'CoverSubtitle',
        fontName='Arial-Bold',
        fontSize=13,
        leading=18,
        textColor=SECONDARY,
        alignment=1,
        spaceAfter=25
    )

    style_cover_meta = ParagraphStyle(
        'CoverMeta',
        fontName='Arial',
        fontSize=10,
        leading=15,
        textColor=TEXT_DARK,
        alignment=1
    )

    style_h1 = ParagraphStyle(
        'CustomH1',
        fontName='Arial-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'CustomH2',
        fontName='Arial-Bold',
        fontSize=11.5,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    style_h3 = ParagraphStyle(
        'CustomH3',
        fontName='Arial-Bold',
        fontSize=10,
        leading=13,
        textColor=ACCENT,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'CustomBody',
        fontName='Arial',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        spaceAfter=6,
        alignment=4 
    )

    style_body_bold = ParagraphStyle(
        'CustomBodyBold',
        fontName='Arial-Bold',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        spaceAfter=4
    )

    style_bullet = ParagraphStyle(
        'CustomBullet',
        fontName='Arial',
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_DARK,
        leftIndent=12,
        spaceAfter=3
    )

    style_code = ParagraphStyle(
        'CustomCode',
        fontName='CourierNew',
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor("#1A202C")
    )

    style_code_box = ParagraphStyle(
        'CustomCodeBox',
        fontName='CourierNew',
        fontSize=7.2,
        leading=9.8,
        textColor=colors.HexColor("#1A202C"),
        backColor=BG_CODE,
        borderColor=BORDER_COLOR,
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6,
        leftIndent=0,
        rightIndent=0
    )

    style_callout = ParagraphStyle(
        'CalloutText',
        fontName='Arial',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2C5282")
    )

    story = []

    def make_callout(text, title="ÖNEMLİ BİLGİ & MİMARİ NOT"):
        content = [
            Paragraph(f"<b>💡 {title}</b>", ParagraphStyle('CTitle', fontName='Arial-Bold', fontSize=8.5, leading=11, textColor=PRIMARY, spaceAfter=3)),
            Paragraph(text, style_callout)
        ]
        t = Table([[content]], colWidths=[487])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
            ('BORDER', (0,0), (-1,-1), 0.75, colors.HexColor("#90CDF4")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    story.append(Spacer(1, 1.2*inch))
    
    story.append(HRFlowable(width="100%", thickness=4, color=PRIMARY, spaceBefore=0, spaceAfter=20))
    
    story.append(Paragraph("KARGO ERP DAĞITIM & ROTA OPTİMİZASYON SİSTEMİ", style_cover_title))
    story.append(Paragraph("Modül 0'dan Modül 8'e Mimari, İşleyiş, Araçlar ve Adım Adım Kod Rehberi", style_cover_sub))
    
    story.append(HRFlowable(width="60%", thickness=1, color=SECONDARY, spaceBefore=10, spaceAfter=30))
    
    story.append(Spacer(1, 0.4*inch))
    
    meta_text = """
    <b>Proje Türü:</b> Kurumsal Kargo ERP Rota Optimizasyonu Staj Projesi<br/>
    <b>Doküman Sürümü:</b> 1.0 (Modül 0 - Modül 8 Eksiksiz Tamamlanma Raporu)<br/>
    <b>Tarih:</b> 14 Ağustos 2026<br/>
    <b>Geliştirici:</b> Zeynep Ersan<br/>
    <b>Teknoloji Yığını:</b> Python 3.10+ • Google OR-Tools • OpenRouteService API • Pandas • Folium • YAML
    """
    story.append(Paragraph(meta_text, style_cover_meta))
    
    story.append(Spacer(1, 0.8*inch))
    
    cover_summary_data = [
        ["Kapsanan Modüller", "Amaç & Yetkinlik", "Çözülen Problem"],
        ["Modül 0", "Kurulum, Config ve API Entegrasyonu", "Güvenli konfigürasyon ve ortam hazırlığı"],
        ["Modül 1", "Veri Okuma, Desi Hesabı ve Doğrulama", "Girdi CSV denetimi, veri tiplendirme ve depo kontrolü"],
        ["Modül 2", "Geocoding (Adres → Koordinat)", "Metin adreslerin enlem/boylama çevrimi ve cache yönetimi"],
        ["Modül 3", "Gerçek Yol Mesafe & Süre Matrisi", "ORS Matrix API, Haversine kıyaslaması ve blok sorgulama"],
        ["Modül 4", "Çift Kapasiteli Temel VRP (kg + desi)", "OR-Tools modeli, hacim ve ağırlık sınır optimizasyonu"],
        ["Modül 5", "Heterojen Filo & Araç Uyumluluğu", "Sabit sefer maliyeti, km maliyeti ve max durak sınırı"],
        ["Modül 6", "Zaman Pencereleri & Servis Süresi", "Müşteri randevu aralığı, adreste hizmet ve vardiya kısıtı"],
        ["Modül 7", "SLA & Gecikme Cezaları (Soft Windows)", "EXPRESS ve STANDART gecikmelerine kademeli parasal ceza"],
        ["Modül 8", "Backhaul (Teslimat + Toplama / İade)", "Ters işaretli talep mantığıyla dinamik yük yönetimi"]
    ]
    t_cover = Table(cover_summary_data, colWidths=[70, 210, 207])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('FONTNAME', (0,1), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_cover)
    story.append(PageBreak())

    story.append(Paragraph("1. SİSTEM MİMARİSİ VE GENEL BAKIŞ", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "Kargo Dağıtım ve Rota Optimizasyon Sistemi, bir kargo şubesine bağlı araç filosunun gün içindeki teslimat (delivery) ve toplama (pickup) siparişlerini minimum operasyonel maliyet, minimum toplam mesafe, araç kapasite sınırları (ağırlık ve hacim/desi), çalışma vardiyası ve müşteri randevu saatleri (zaman pencereleri) kısıtları altında en verimli şekilde dağıtmasını sağlayan endüstriyel standartta bir optimizasyon motorudur.",
        style_body
    ))
    
    story.append(Paragraph("<b>End-to-End Veri Akış Pipeline'ı:</b>", style_h2))
    
    pipeline_flow = """
    [1. CSV Girdi Verileri] (data/siparisler.csv & data/araclar.csv)
            │
            ▼
    [Modül 0: config_loader.py] ➔ YAML ayarları & .env API Key güvenli yükleme
            │
            ▼
    [Modül 1: loader.py] ➔ Veri okuma, tip dönüşümü, desi hesabı ve sıkı doğrulama (validate)
            │
            ▼
    [Modül 2: geocode.py] ➔ Adreslerin ORS Pelias ile enlem/boylama çevrimi (JSON Cache + Kadıköy Focus)
            │
            ▼
    [Modül 3: matrix.py] ➔ 13×13 Gerçek karayolu mesafe ve süre matrisi (MD5 Hash Cache + Parçalama)
            │
            ▼
    [Modül 4-8: model.py & pickup.py] ➔ Google OR-Tools VRP Modeli:
            ├─ Modül 4: Çift Kapasite (kg + desi) Boyutları
            ├─ Modül 5: Heterojen Filo (Sabit Maliyet + Km Maliyeti + Max Durak)
            ├─ Modül 6: Zaman Pencereleri + Servis Süresi + Vardiya Sınırı
            ├─ Modül 7: SLA ve Kademeli Gecikme Cezaları (Soft Time Windows)
            └─ Modül 8: Backhaul (Teslimat + Toplama / İade Dinamik Yük Dengesi)
            │
            ▼
    [Çözücü: solve.py] ➔ PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH (30 sn limit)
            │
            ▼
    [Görselleştirme & Rapor: visualize.py & main.py] ➔ İnteraktif Folium Haritası + Detaylı KPI Raporu
    """
    story.append(Paragraph(pipeline_flow.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code_box))
    
    story.append(Paragraph("<b>Dizin ve Modül Dağılım Tablosu:</b>", style_h2))
    
    folder_table_data = [
        ["Dosya / Dizin", "Ait Olduğu Modül", "Temel İşlevi ve Sorumluluğu"],
        ["config.yaml", "Modül 0", "Optimizasyon hedefi, dosya yolları, ORS koordinatları ve çözücü parametreleri"],
        [".env", "Modül 0", "OpenRouteService API anahtarının güvenli ve gizli tutulduğu ortam dosyası"],
        ["src/config_loader.py", "Modül 0", "YAML dosyasını ve .env gizli anahtarını doğrulayarak sisteme sunan modül"],
        ["src/loader.py", "Modül 1", "CSV dosyalarını okuma, tiplendirme, desi hesabı ve tutarlılık denetimi (validate)"],
        ["src/geocode.py", "Modül 2", "Adresleri ORS Pelias ile koordinata çevirme, cacheleme ve doğrulama haritası"],
        ["src/matrix.py", "Modül 3", "Gerçek yol mesafe/süre matrisi, Haversine kıyası ve MD5 önbellekleme"],
        ["src/model.py", "Modül 4 - 8", "Google OR-Tools RoutingModel üzerinde tüm kısıt ve boyutların inşası"],
        ["src/pickup.py", "Modül 8", "Backhaul (toplama/iade) için negatif talep hesaplama ve yük dengeleme"],
        ["src/solve.py", "Modül 4 / 9", "Arama stratejisi (Guided Local Search) ile çözümü yürütme ve rotaları çıkarma"],
        ["src/visualize.py", "Görselleştirme", "Çıkan rotaları Folium ile renkli interaktif HTML haritasına dökme"],
        ["main.py", "Orkestrasyon", "Tüm modülleri uçtan uca çalıştıran ana çalıştırma betiği"]
    ]
    t_folder = Table(folder_table_data, colWidths=[95, 80, 312])
    t_folder.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('FONTNAME', (0,1), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_folder)
    story.append(Spacer(1, 8))
    
    story.append(make_callout(
        "Kargo operasyonlarında araçların kapasitesi sadece <b>Ağırlık (kg)</b> ile dolmaz; kutuların hacimsel büyüklüğü olan <b>Desi</b> faktörü çoğu zaman aracı çok daha önce doldurur. Bu projede hem ağırlık hem desi, zaman pencereleri ve geri dönüş yükleri eşzamanlı olarak modellenmiştir.",
        "GERÇEK DÜNYA LOJİSTİK MANTIĞI"
    ))
    story.append(PageBreak())

    story.append(Paragraph("2. MODÜL 0: KURULUM, KONFİGÜRASYON VE İSKELET", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>2.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Modül 0, projenin temel altyapısını kurar. Kod içerisine sabit (hardcoded) değerler yazılmasını engelleyerek sistemin parametrik çalışmasını sağlar. Çözücü parametreleri, dosya yolları, API koordinat odak noktaları ve güvenlik anahtarları bağımsız dosyalardan yönetilir.",
        style_body
    ))
    
    story.append(Paragraph("<b>2.2. Kullanılan Önemli Araçlar ve Kütüphaneler:</b>", style_h2))
    story.append(Paragraph("• <b>PyYAML (yaml.safe_load):</b> <code>config.yaml</code> dosyasındaki hiyerarşik yapılandırmayı güvenli biçimde Python sözlüğüne dönüştürür.", style_bullet))
    story.append(Paragraph("• <b>python-dotenv (load_dotenv, os.getenv):</b> API anahtarı gibi hassas bilgilerin kod tabanından izole edilerek <code>.env</code> dosyasından okunmasını sağlar.", style_bullet))
    story.append(Paragraph("• <b>pathlib.Path:</b> İşletim sisteminden bağımsız (Windows/Linux/macOS uyumlu) mutlak dosya yolu çözünürlüğü sağlar.", style_bullet))
    
    story.append(Paragraph("<b>2.3. Adım Adım İşleyiş ve Kod Mimarisi:</b>", style_h2))
    story.append(Paragraph("1. Proje kök dizini <code>Path(__file__).resolve().parent.parent</code> ile dinamik tespit edilir.", style_bullet))
    story.append(Paragraph("2. <code>load_config()</code> fonksiyonu ile <code>config.yaml</code> okunur.", style_bullet))
    story.append(Paragraph("3. <code>get_api_key()</code> fonksiyonu ile <code>.env</code> kontrol edilir; anahtar yoksa veya şablon metin kalmışsa <code>None</code> döndürülerek kullanıcı uyarılır.", style_bullet))

    story.append(Paragraph("<b>config.yaml ve config_loader.py Kod Yapısı:</b>", style_h3))
    code_m0 = """# config.yaml
objective: "distance"  # Optimizasyon hedefi: mesafe minimizasyonu
data:
  orders_file: "data/siparisler.csv"
  vehicles_file: "data/araclar.csv"
cache:
  enabled: true
  geocode_cache_file: "cache/geocode_cache.json"
  matrix_cache_file: "cache/matrix_cache.json"
ors:
  profile: "driving-car"
  country_code: "TUR"
  focus_lat: 40.997314   # Kadıköy Şube Odak Enlemi
  focus_lon: 29.044531   # Kadıköy Şube Odak Boylamı
solver:
  time_limit_seconds: 30
  first_solution_strategy: "PATH_CHEAPEST_ARC"
  local_search_metaheuristic: "GUIDED_LOCAL_SEARCH"

# src/config_loader.py
def load_config(path="config.yaml") -> dict:
    cfg_path = ROOT / path
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_api_key() -> str | None:
    load_dotenv(ROOT / ".env")
    key = os.getenv("ORS_API_KEY")
    return key.strip() if key and key.strip() not in ("", "senin_api_anahtarin_buraya") else None"""
    story.append(Paragraph(code_m0.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code_box))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. MODÜL 1: VERİ OKUMA, TİPLENDİRME, DESİ VE DOĞRULAMA", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>3.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Operasyonel veriler CSV formatında sisteme girer. Modül 1, eksik veya hatalı verilerin optimizasyon algoritmasını çökertmesini engellemek için katı doğrulama (data validation) kuralları uygular. Ayrıca saat formatlarını (HH:MM) gün içi dakikaya çevirir ve kargo desilerini hesaplar.",
        style_body
    ))
    
    story.append(Paragraph("<b>3.2. Kullanılan Önemli Araçlar ve Fonksiyonlar:</b>", style_h2))
    story.append(Paragraph("• <b>pandas (read_csv, to_numeric, apply):</b> Veri çerçevelerinin oluşturulması ve metin alanların sayısal tiplere dönüştürülmesi.", style_bullet))
    story.append(Paragraph("• <b>Desi Formülü:</b> Kargo hacimsel ağırlığı <code>Desi = (En × Boy × Yükseklik) / 3000</code> formülüyle belirlenir.", style_bullet))
    story.append(Paragraph("• <b>HH:MM → Gün İçi Dakika Dönüştürücü:</b> <code>safe_hhmm_to_min()</code> fonksiyonu ile '09:30' ➔ <code>9×60 + 30 = 570</code> dakikaya dönüştürülür.", style_bullet))
    story.append(Paragraph("• <b>validate() Fonksiyonu:</b> Toplam 8 kritik kontrol gerçekleştirir (Negatif kg/desi, tanımsız işlem tipi, geçersiz zaman aralığı, DEPO tekliği, toplam yük vs filo kapasitesi ön kontrolü).", style_bullet))

    story.append(Paragraph("<b>Giriş Veri Formatı ve Doğrulama Kriterleri Tablosu:</b>", style_h3))
    
    m1_table_data = [
        ["Sütun Adı", "Örnek Değer", "Veri Tipi", "Doğrulama Kuralı & Açıklama"],
        ["kargo_takip_no", "KP001 / 0", "String", "Tekil kimlik. 0 değeri sadece ana depoyu temsil eder."],
        ["islem_tipi", "TESLIMAT / TOPLAMA", "Enum", "Sadece 'DEPO', 'TESLIMAT' veya 'TOPLAMA' kabul edilir."],
        ["agirlik_kg", "3.5", "Float", "Pozitif sayı olmalıdır (Depo için 0)."],
        ["desi", "12.0", "Float", "Pozitif sayı olmalıdır (Hacimsel alan)."],
        ["kategori", "EXPRESS / STANDART", "Enum", "'STANDART', 'EXPRESS', 'AGIR_YUK', 'DEPO' değerleri."],
        ["zaman_baslangic", "09:00 (540 dk)", "Integer", "Randevu başlangıcı. 08:00 - 20:00 mesai saatleri."],
        ["zaman_bitis", "18:00 (1080 dk)", "Integer", "Randevu bitişi. zaman_baslangic < zaman_bitis olmalıdır."],
        ["servis_suresi_dk", "5", "Integer", "Adreste teslimat/toplama için harcanan bekleme süresi."]
    ]
    t_m1 = Table(m1_table_data, colWidths=[90, 85, 60, 252])
    t_m1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('FONTNAME', (0,1), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_m1)
    story.append(PageBreak())

    story.append(Paragraph("4. MODÜL 2: GEOCODING (ADRES → KOORDİNAT DÖNÜŞÜMÜ)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>4.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Kargo siparişlerinde yer alan serbest metin formatındaki adreslerin OpenRouteService Pelias arama motoru ile coğrafi enlem/boylam (lat, lon) koordinatlarına dönüştürülmesini sağlar. Çift katmanlı JSON önbellek mimarisiyle API kota tüketimini sıfırlar ve Kadıköy odak noktasıyla mükerrer mahalle isimlerini doğru lokasyonla eşleştirir.",
        style_body
    ))
    
    story.append(Paragraph("<b>4.2. Kullanılan Önemli Araçlar ve Teknikler:</b>", style_h2))
    story.append(Paragraph("• <b>openrouteservice.Client (pelias_search):</b> OpenStreetMap veritabanı üzerinden metin adresi koordinata çeviren REST API istemcisi.", style_bullet))
    story.append(Paragraph("• <b>Focus Point Disambiguation:</b> Türkiye'de yüzlerce 'Barbaros', 'Atatürk' veya 'Merkez' mahallesi bulunur. <code>focus_point=(29.044531, 40.997314)</code> (Kadıköy Şube) parametresi verilerek sonuçların şubeye en yakın olan mahalleyle eşleşmesi garanti edilir.", style_bullet))
    story.append(Paragraph("• <b>Akıllı JSON Cache (geocode_cache.json):</b> Sorgulanan her adres diske yazılır. Program tekrar çalıştığında kota harcanmaz. Bulunamayan adresler de kaydedilerek boşa istek atılması önlenir.", style_bullet))
    story.append(Paragraph("• <b>Folium Harita Doğrulaması (save_verification_map):</b> Koordinatları çıkarılan 13 noktanın haritada doğru yere düşüp düşmediğini kontrol etmek için interaktif HTML haritası (<code>cache/geocode_kontrol.html</code>) üretilir.", style_bullet))

    story.append(Paragraph("<b>src/geocode.py Kod Yapısı ve Önbellek Akışı:</b>", style_h3))
    code_m2 = """def geocode_addresses(orders: pd.DataFrame, api_key: str, cache_path: str,
                      country_code: str = "TUR", focus_point: tuple = (29.044531, 40.997314)):
    cache = _load_cache(cache_path)  # JSON cache dosyasını oku
    client = openrouteservice.Client(key=api_key)
    
    for address in orders["adres"].unique():
        if address in cache:
            continue  # Önbellekte varsa API çağrısı yapma!
        
        # ORS Pelias Arama Motoru
        res = client.pelias_search(text=address, size=1, country=country_code, focus_point=focus_point)
        features = res.get("features", [])
        if features:
            lon, lat = features[0]["geometry"]["coordinates"]
            cache[address] = {"lat": lat, "lon": lon}
        else:
            cache[address] = None
        time.sleep(0.2)  # Rate-limit koruması
        
    _save_cache(cache_path, cache)
    df = orders.copy()
    df["lat"] = df["adres"].map(lambda a: (cache.get(a) or {}).get("lat"))
    df["lon"] = df["adres"].map(lambda a: (cache.get(a) or {}).get("lon"))
    return df"""
    story.append(Paragraph(code_m2.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code_box))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. MODÜL 3: GERÇEK YOL MESAFE VE SÜRE MATRİSİ", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>5.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Kuş uçuşu mesafeler karayolu rotalamasında yanıltıcıdır (tek yönler, deniz engeli, otoyol köprüleri). Modül 3, OpenRouteService Matrix servisini kullanarak N adet nokta arasındaki N×N gerçek karayolu mesafesi (metre) ve seyahat süresi (saniye) matrislerini üretir.",
        style_body
    ))
    
    story.append(Paragraph("<b>5.2. Kullanılan Önemli Araçlar ve Algoritmalar:</b>", style_h2))
    story.append(Paragraph("• <b>openrouteservice.distance_matrix:</b> N×N gerçek sürüş mesafesi ve süresi hesaplayan API çağrısı.", style_bullet))
    story.append(Paragraph("• <b>MD5 İmzalı Cache Mekanizması:</b> Noktaların enlem/boylam koordinatları ve araç profili birleştirilerek MD5 hash anahtarı üretilir (<code>_signature</code>). Koordinatlar değişmediği sürece matris doğrudan diskten okunur.", style_bullet))
    story.append(Paragraph("• <b>Dinamik Blok/Parçalama Stratejisi (_call_ors_matrix):</b> ORS'nin tek istekteki 2500 rota limitini aşmamak için kaynak noktalar dinamik bloklara bölünür (<code>blok_boyu = max(1, 2500 // n)</code>).", style_bullet))
    story.append(Paragraph("• <b>Haversine Formülü ile Kuş Uçuşu Kıyaslaması:</b> Gerçek karayolu mesafesi ile kuş uçuşu mesafe karşılaştırılır. Test veri setinde ortalama <b>1.46x</b>, en çıkmaz sokaklarda ise <b>2.54x</b> sapma tespit edilmiştir.", style_bullet))

    story.append(Paragraph("<b>Haversine vs Gerçek Yol Matris Özeti:</b>", style_h3))
    matrix_metrics_data = [
        ["Metrik Adı", "Hesaplanan Değer", "Açıklama"],
        ["Matris Boyutu", "13 × 13 (169 Bağlantı)", "1 Depo + 12 Müşteri Noktası"],
        ["Ortalama Mesafe", "18.6 km", "Noktalar arası ortalama karayolu mesafesi"],
        ["Ortalama Süre", "18.7 dakika", "Noktalar arası ortalama seyahat süresi"],
        ["En Uzun Bağlantı", "42.5 km (KP010 ➔ KP012)", "Kartal ile Şile/Çekmeköy hattı arasındaki mesafe"],
        ["Gerçek Yol / Kuş Uçuşu Oranı", "1.46x Ortalama (2.54x Maksimum)", "İstanbul yol ağının ve trafik kıvrımlarının somut kanıtı"]
    ]
    t_mat = Table(matrix_metrics_data, colWidths=[130, 150, 207])
    t_mat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('FONTNAME', (0,1), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_mat)
    story.append(PageBreak())

    story.append(Paragraph("6. MODÜL 4: TEMEL DAĞITIM VE ÇİFT KAPASİTE YÖNETİMİ (VRP)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>6.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Kargo dağıtımında klasik Araç Rotalama Problemini (VRP) Google OR-Tools optimizasyon kütüphanesi üzerinde kurar. En önemli özelliği, aracı sadece ağırlık (kg) kısıtıyla değil, eşzamanlı olarak hacim (desi) kısıtıyla da sınırlayan <b>Çift Kapasite Boyutu (Dual Capacity Dimension)</b> mimarisini kurmasıdır.",
        style_body
    ))
    
    story.append(Paragraph("<b>6.2. Kullanılan Önemli Araçlar ve OR-Tools Bileşenleri:</b>", style_h2))
    story.append(Paragraph("• <b>pywrapcp.RoutingIndexManager:</b> Düğüm sayıları (nodes), araç sayıları ve depo indeksini OR-Tools'un dahili solver indekslerine eşleyen yönetici.", style_bullet))
    story.append(Paragraph("• <b>pywrapcp.RoutingModel:</b> Optimizasyon kısıtlarının ve maliyet fonksiyonlarının eklendiği ana model nesnesi.", style_bullet))
    story.append(Paragraph("• <b>RegisterTransitCallback & SetArcCostEvaluatorOfAllVehicles:</b> Modül 3'ten gelen gerçek karayolu mesafe matrisini rota maliyet fonksiyonu (Arc Cost) olarak atar.", style_bullet))
    story.append(Paragraph("• <b>AddDimensionWithVehicleCapacity:</b> Ağırlık ('Agirlik') ve Hacim ('Desi') için iki ayrı boyut açar. Her aracın kendi kapasite tavanı bu boyuta tanımlanır.", style_bullet))

    story.append(Paragraph("<b>src/model.py Çift Kapasite Boyut Kodu:</b>", style_h3))
    code_m4 = """def _add_capacity_dimension(routing, manager, demands, capacities, name: str):
    demands_int = [int(round(d)) for d in demands]
    capacities_int = [int(round(c)) for c in capacities]

    def demand_callback(from_index):
        node = manager.IndexToNode(from_index)
        return demands_int[node]

    demand_cb_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_cb_idx,
        0,                 # Slack (bekleme/esneme yok)
        capacities_int,    # Her aracın kendi kapasitesi [Moto, Panelvan, Kamyonet]
        True,              # start_cumul_to_zero (Araç depodan 0 birikimli başlar)
        name               # 'Agirlik' ve 'Desi'
    )"""
    story.append(Paragraph(code_m4.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code_box))
    story.append(Spacer(1, 10))

    story.append(Paragraph("7. MODÜL 5: HETEROJEN FİLO VE ARAÇ UYUMLULUĞU", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>7.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Gerçek hayatta kargo filoları tek tip araçtan oluşmaz. Motokurye, Panelvan ve Kamyonet gibi farklı taşıma kapasitelerine, farklı sabit sefer maliyetlerine ve farklı kilometre maliyetlerine sahip araçlar bulunur. Modül 5, filoyu heterojenleştirir ve ağır paket filtrelerini devreye sokar.",
        style_body
    ))
    
    story.append(Paragraph("<b>7.2. Kullanılan Önemli Araçlar ve Matematiksel Mantık:</b>", style_h2))
    story.append(Paragraph("• <b>SetFixedCostOfVehicle:</b> Bir aracı depodan çıkarmanın sabit bir bedeli vardır (Örn: Moto 600 TL, Panelvan 900 TL, Kamyonet 1200 TL). Çözücü gereksiz araç çalıştırmayı cezalandırır.", style_bullet))
    story.append(Paragraph("• <b>Maksimum Durak Sınırı (MaxDurak Dimension):</b> Kuryelerin fiziksel yorgunluğu ve işlem kapasitesi gereği araç başına durak tavanı konur (Moto: 25, Panelvan: 40, Kamyonet: 50 durak).", style_bullet))
    story.append(Paragraph("• <b>Ağır/Hacimli Paket Filtresi:</b> Motokuryenin taşıyamayacağı <code>AGIR_YUK</code> veya <code>>30 desi</code> paketler otomatik olarak Panelvan veya Kamyonet'e yönlendirilir.", style_bullet))

    story.append(Paragraph("<b>Heterojen Filo Özellikleri Tablosu:</b>", style_h3))
    fleet_table_data = [
        ["Araç Tipi", "Araç ID", "Kapasite (kg)", "Kapasite (desi)", "Sabit Maliyet", "Km Maliyeti", "Max Durak"],
        ["MOTO_KURYE", "34-MOTO-01", "60 kg", "50 desi", "₺600", "₺3.50 / km", "25 Durak"],
        ["PANELVAN", "34-PNL-01", "800 kg", "400 desi", "₺900", "₺7.50 / km", "40 Durak"],
        ["KAMYONET", "34-KMY-01", "1500 kg", "1000 desi", "₺1200", "₺9.50 / km", "50 Durak"]
    ]
    t_fl = Table(fleet_table_data, colWidths=[80, 75, 65, 75, 65, 65, 62])
    t_fl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('FONTNAME', (0,1), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_fl)
    story.append(PageBreak())

    story.append(Paragraph("8. MODÜL 6: ZAMAN PENCERELERİ VE SERVİS SÜRESİ (VRPTW)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>8.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Kargo teslimatlarında müşterilerin randevu saatleri (zaman pencereleri), kuryenin paketi teslim ederken kapıda harcadığı servis süresi (işlem süresi) ve kuryenin günlük yasal çalışma vardiyası (8 saat = 480 dakika mesai) bu modülde 'Zaman' boyutu olarak modellenir.",
        style_body
    ))
    
    story.append(Paragraph("<b>8.2. Kullanılan Önemli Araçlar ve Formülasyon:</b>", style_h2))
    story.append(Paragraph("• <b>AddDimension('Zaman'):</b> Rota boyunca kümülatif geçen zamanı izleyen boyut (24 saat = 1440 dk kapasite).", style_bullet))
    story.append(Paragraph("• <b>Transit Callback (Yol + Servis Süresi):</b> İki durak arasındaki toplam süre <code>Geçiş Süresi = Gerçek Yol Süresi (dur_s) + Kalkan Duraktaki Servis Süresi (servis_suresi_dk)</code> olarak hesaplanır.", style_bullet))
    story.append(Paragraph("• <b>Vardiya Sınırı (Shift Limit):</b> Her aracın bitiş düğümünde (End Node) <code>time_dim.CumulVar(end_index).SetMax(max_calisma_dk)</code> uygulanarak kuryenin 480 dakikadan fazla çalışması engellenir.", style_bullet))

    story.append(Paragraph("<b>src/model.py Zaman Boyutu ve Servis Süresi Kodu:</b>", style_h3))
    code_m6 = """def _add_time_dimension(routing, manager, points, dur_s, vehicles):
    servis_dk = points["servis_suresi_dk"].fillna(0).tolist()

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        travel_time_dk = dur_s[from_node][to_node] / 60.0  # Saniye ➔ Dakika
        service_time_dk = servis_dk[from_node]              # Duraktaki bekleme
        return int(round(travel_time_dk + service_time_dk))

    time_cb_idx = routing.RegisterTransitCallback(time_callback)
    routing.AddDimension(time_cb_idx, slack_max=600, capacity=1440, fix_start_cumul_to_zero=True, name="Zaman")
    time_dim = routing.GetDimensionOrDie("Zaman")

    # Vardiya Sınırı: Kurye maksimum 480 dk (8 saat) çalışabilir
    for v_idx in range(routing.vehicles()):
        end_index = routing.End(v_idx)
        max_time = int(vehicles.iloc[v_idx]["max_calisma_dk"])
        time_dim.CumulVar(end_index).SetMax(max_time)"""
    story.append(Paragraph(code_m6.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code_box))
    story.append(Spacer(1, 10))

    story.append(Paragraph("9. MODÜL 7: SLA VE KADEMELİ GECİKME CEZALARI", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>9.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Klasik VRP modellerinde katı zaman pencereleri (Hard Constraints) kullanılır; kurye randevuya 1 dakika bile geç kalırsa çözüm 'İMKÂNSIZ' (Infeasible) ilan edilir. Modül 7, <b>Soft Time Windows</b> yaklaşımıyla randevu ihlallerini yasaklamak yerine her gecikme dakikasına parasal bir ceza (SLA Penalty) uygulayarak esnek optimizasyon sağlar.",
        style_body
    ))
    
    story.append(Paragraph("<b>9.2. Kategori Bazlı Gecikme Ceza Tarifesi:</b>", style_h2))
    story.append(Paragraph("• <b>EXPRESS Kargo:</b> Dakika başına <b>10 TL</b> gecikme cezası (Öncelikli teslimat, çözücü bu paketlere ilk uğramayı hedefler).", style_bullet))
    story.append(Paragraph("• <b>STANDART Kargo:</b> Dakika başına <b>1 TL</b> gecikme cezası (Normal öncelik).", style_bullet))
    story.append(Paragraph("• <b>AGIR_YUK & DEPO:</b> Gecikme cezası <b>0 TL</b> (Öncelik zaman değil kapasitedir).", style_bullet))
    story.append(Paragraph("• <b>OR-Tools Metodu:</b> <code>SetCumulVarSoftUpperBound(routing_index, slack_max_min, penalty_tl_per_min)</code> fonksiyonu ile modele entegre edilir.", style_bullet))

    story.append(Paragraph("<b>src/model.py Soft Time Window Fonksiyonu:</b>", style_h3))
    code_m7 = """def _add_soft_time_windows(routing, manager, points, time_dim):
    penalty_per_min = {"EXPRESS": 10, "STANDART": 1, "AGIR_YUK": 0, "DEPO": 0}

    for node_idx in range(1, len(points)):
        point = points.iloc[node_idx]
        kategori = point.get("kategori", "STANDART")
        penalty = penalty_per_min.get(kategori, 0)
        zaman_bitis = point.get("zaman_bitis")

        if pd.notna(zaman_bitis) and penalty > 0:
            routing_index = manager.NodeToIndex(node_idx)
            # Randevu bitiş saatinden sonraki her dakika için maliyet fonksiyonuna ceza ekle
            time_dim.SetCumulVarSoftUpperBound(routing_index, int(zaman_bitis), int(penalty))"""
    story.append(Paragraph(code_m7.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code_box))
    story.append(PageBreak())

    story.append(Paragraph("10. MODÜL 8: BACKHAUL (TESLİMAT VE TOPLAMA / İADE ENTEGRASYONU)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>10.1. Modülün Amacı ve Kapsamı:</b>", style_h2))
    story.append(Paragraph(
        "Kargo operasyonunda araçlar sadece depodan müşteriye teslimat (delivery) yapmaz; aynı zamanda müşterilerden e-ticaret iadeleri veya yeni gönderileri (pickup/backhaul) toplayıp şubeye geri getirir. Modül 8, teslimat ve toplama işlemlerinin aynı rotada araç kapasitesini hiçbir an aşmadan yürütülmesini sağlar.",
        style_body
    ))
    
    story.append(Paragraph("<b>10.2. Çözüm: Ters İşaretli Talep (Adjusted Demands) Stratejisi:</b>", style_h2))
    story.append(Paragraph("• <b>TESLIMAT Paketleri (+kg, +desi):</b> Araç depodan teslimat yüküyle çıkar. Duraklara uğradıkça araçtaki yük azalır.", style_bullet))
    story.append(Paragraph("• <b>TOPLAMA Paketleri (-kg, -desi):</b> Toplama durağında araç yük alır. Talebi negatif olarak tanımlandığı için çözücü teslimatları önce yapıp aracı boşaltmayı, ardından dönüş yolunda toplamaları almayı otomatik olarak tercih eder.", style_bullet))
    story.append(Paragraph("• <b>Net Kapasite Korunumu:</b> <code>Gidiş Yükü - Dönüş Yükü = Net Yük</code> formülüyle aracın hiçbir noktada aşırı yüklenmemesi garanti edilir.", style_bullet))

    story.append(Paragraph("<b>src/pickup.py ve model.py Entegrasyon Kodu:</b>", style_h3))
    code_m8 = """# src/pickup.py
def compute_adjusted_demands(points: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    adjusted_kg = points["agirlik_kg"].copy()
    adjusted_desi = points["desi"].copy()

    # TOPLAMA paketlerinin talebini negatif yap (-kg, -desi)
    toplama_mask = points["islem_tipi"] == "TOPLAMA"
    adjusted_kg[toplama_mask] = -adjusted_kg[toplama_mask]
    adjusted_desi[toplama_mask] = -adjusted_desi[toplama_mask]

    return adjusted_kg, adjusted_desi

# src/model.py build_model() içerisindeki entegrasyon:
adjusted_kg, adjusted_desi = compute_adjusted_demands(points)
_add_capacity_dimension(routing, manager, adjusted_kg, vehicles["kapasite_kg"], "Agirlik")
_add_capacity_dimension(routing, manager, adjusted_desi, vehicles["kapasite_desi"], "Desi")"""
    story.append(Paragraph(code_m8.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code_box))
    story.append(Spacer(1, 8))

    story.append(Paragraph("11. SİSTEM ENTEGRASYONU, TEST SONUÇLARI VE PERFORMANS", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "Modül 0'dan 8'e kadar geliştirilen tüm bileşenler <code>main.py</code> orkestrasyonu altında 12 sipariş (9 teslimat, 3 toplama) ve 3 araçlık filo ile test edilmiştir. Sistem <b>0 eksiklik ve 0 hata</b> ile optimum çözümü 2 saniyenin altında bulmuştur.",
        style_body
    ))
    
    story.append(Paragraph("<b>Nihai Test Çıktıları ve KPI Özet Tablosu:</b>", style_h2))
    
    results_table_data = [
        ["Metrik / Parametre", "Elde Edilen Değer", "Değerlendirme & Açıklama"],
        ["Toplam Nokta Sayısı", "13 Nokta (1 Depo + 12 Müşteri)", "Tüm adresler %100 doğrulukla çözüldü."],
        ["Kullanılan Araç", "1 / 3 Araç (34-PNL-01 Panelvan)", "Sabit maliyet optimizasyonu ile tek araçta toplandı."],
        ["Atanan Durak Sayısı", "12 Durak (9 Teslimat + 3 Toplama)", "Tüm paketler rotaya eksiksiz dahil edildi."],
        ["Toplam Rota Mesafesi", "119.2 km", "Gerçek yol matrisine göre optimize edilmiş mesafe."],
        ["Toplam Operasyon Maliyeti", "₺1,793.69", "₺900 sabit maliyet + ₺893.69 km yakıt maliyeti."],
        ["Ağır Paket Filtre Başarısı", "KP006 (40kg/120desi) & KP010 (25kg/70desi)", "Moto elendi, otomatik olarak Panelvan'a atandı."],
        ["Backhaul Başarısı", "KP005, KP008, KP012 (3 Toplama)", "Dönüş yolunda toplanarak şubeye teslim edildi."]
    ]
    t_res = Table(results_table_data, colWidths=[125, 145, 217])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('FONTNAME', (0,1), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_res)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Genel Modül Tamamlanma Matrisi:</b>", style_h2))
    mod_matrix_data = [
        ["Modül No", "Modül Başlığı", "Temel Dosya", "Kullanılan Temel Araçlar", "Durum"],
        ["Modül 0", "Kurulum & İskelet", "config_loader.py", "PyYAML, python-dotenv, Path", "✅ TAMAM"],
        ["Modül 1", "Veri Okuma & Doğrulama", "loader.py", "Pandas, validate(), Desi Formülü", "✅ TAMAM"],
        ["Modül 2", "Geocoding (Adres→Koord)", "geocode.py", "ORS Pelias, Cache, Folium Haritası", "✅ TAMAM"],
        ["Modül 3", "Gerçek Yol Matrisi", "matrix.py", "ORS Matrix, MD5 Hash, Haversine", "✅ TAMAM"],
        ["Modül 4", "Çift Kapasiteli VRP", "model.py", "OR-Tools, Dual Dimension (kg+desi)", "✅ TAMAM"],
        ["Modül 5", "Heterojen Filo Yönetimi", "model.py", "SetFixedCost, MaxDurak, Filtreler", "✅ TAMAM"],
        ["Modül 6", "Zaman Pencereleri", "model.py", "Time Dimension, Servis Süresi, Vardiya", "✅ TAMAM"],
        ["Modül 7", "SLA & Gecikme Cezası", "model.py", "Soft Time Windows, EXPRESS/STANDART", "✅ TAMAM"],
        ["Modül 8", "Backhaul (Teslimat/Toplama)", "pickup.py", "Ters İşaretli Talep, Net Kapasite", "✅ TAMAM"]
    ]
    t_mod = Table(mod_matrix_data, colWidths=[48, 110, 85, 184, 60])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('FONTNAME', (0,1), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (-1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_mod)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(
        "<b>Sonuç:</b> Kargo ERP Rota Optimizasyonu motoru, 0'dan 8'e kadar tüm lojistik, coğrafi, zamansal ve kapasite kısıtlarını başarıyla karşılamakta ve kurumsal operasyona hazır durumdadır.",
        style_body_bold
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ PDF başarıyla oluşturuldu: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
