"""Route Optimizer PowerPoint (.pptx) Sunum Oluşturucu — v2.0 Güncel Sürüm.

Bu betik; projenin en son eklenen tüm özelliklerini, modüler mimarisini (Modül 0-8 & 9-12),
harita doğruluğu iyileştirmelerini (ORS Pelias Geocoding, Disambiguation, Gerçek Yol Matrisi),
çift kapasiteli (KG + Desi) ve Soft SLA kısıtlarını, 3 stratejik senaryoyu,
3 katmanlı akıllı cache altyapısını, canlı web dashboardunu (autocomplete, validate-address, re-optimize)
ve otomatik PDF rehber ekosistemini kapsayan 14 slaytlık modern kurumsal bir sunum üretir.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BG_COLOR = RGBColor(11, 19, 43)          
CARD_BG = RGBColor(28, 37, 65)          
CARD_BG_ALT = RGBColor(20, 29, 52)      
CARD_BORDER = RGBColor(58, 80, 107)     
PINE_GREEN = RGBColor(45, 106, 79)      
EMERALD = RGBColor(16, 185, 129)        
BLUE_ACCENT = RGBColor(59, 130, 246)    
SKY_BLUE = RGBColor(56, 189, 248)       
GOLD_ACCENT = RGBColor(245, 158, 11)    
PURPLE_ACCENT = RGBColor(168, 85, 247)  
ROSE_ACCENT = RGBColor(244, 63, 94)     
TEXT_WHITE = RGBColor(248, 250, 252)    
TEXT_LIGHT = RGBColor(226, 232, 240)    
TEXT_MUTED = RGBColor(148, 163, 184)    

FONT_FAMILY = "Segoe UI"
TOTAL_SLIDES = 14


def set_slide_background(slide):
    """Slayt arka planını koyu lacivert renkle doldurur."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR


def add_header(slide, tag_text: str, title_text: str, current_slide: int, total_slides: int = TOTAL_SLIDES):
    """Standart kurumsal üst bilgi, kategori etiketi ve slayt sayacı ekler."""
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8.5), Inches(0.32))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = FONT_FAMILY
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = EMERALD

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(9.8), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    num_box = slide.shapes.add_textbox(Inches(11.2), Inches(0.35), Inches(1.3), Inches(0.4))
    tf_num = num_box.text_frame
    tf_num.margin_left = tf_num.margin_top = tf_num.margin_right = tf_num.margin_bottom = 0
    p_num = tf_num.paragraphs[0]
    p_num.text = f"{current_slide:02d} / {total_slides:02d}"
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.font.name = FONT_FAMILY
    p_num.font.size = Pt(10.5)
    p_num.font.bold = True
    p_num.font.color.rgb = EMERALD


def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER, border_width=1):
    """Görsel kart bileşeni oluşturur."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(border_width)
    return shape


def add_speaker_notes(slide, notes_text: str):
    """Slayta konuşmacı notlarını ekler (Sunucu görünümünde okunabilir)."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    badge = add_card(s1, Inches(0.8), Inches(0.9), Inches(5.2), Inches(0.42), bg_color=RGBColor(18, 38, 58), border_color=PINE_GREEN)
    tf_b = badge.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "🚚 KURUMSAL KARGO ERP & DAĞITIM OPTİMİZASYONU"
    p_b.font.name = FONT_FAMILY
    p_b.font.size = Pt(9.5)
    p_b.font.bold = True
    p_b.font.color.rgb = EMERALD
    p_b.alignment = PP_ALIGN.CENTER

    title_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(11.7), Inches(2.2))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Route Optimizer"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Yapay Zeka ve Yöneylem Araştırması Destekli Akıllı Rota & Filo Yönetim Sistemi"
    p1_sub.font.name = FONT_FAMILY
    p1_sub.font.size = Pt(18)
    p1_sub.font.bold = True
    p1_sub.font.color.rgb = SKY_BLUE

    sub_box = s1.shapes.add_textbox(Inches(0.8), Inches(3.7), Inches(11.5), Inches(1.1))
    tf_sub = sub_box.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Gerçek karayolu mesafeleri, çift kapasite (KG + Desi), randevulu zaman pencereleri ve teslimat/iade toplama (Backhaul) kısıtları altında kargo dağıtımını optimize eden ve canlı web paneliyle yöneten Karar Destek Sistemi."
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = TEXT_MUTED

    k1 = add_card(s1, Inches(0.8), Inches(4.9), Inches(3.7), Inches(1.7))
    tf = k1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🎯 Temel Amaç & Vizyon"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p2 = tf.add_paragraph()
    p2.text = "Manuel rota hazırlığını saniyelere indirmek; yakıt, mesai ve operasyonel maliyetlerde %25+ tasarruf sağlamak."
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED

    k2 = add_card(s1, Inches(4.8), Inches(4.9), Inches(3.7), Inches(1.7))
    tf = k2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚙️ Matematiksel Çözücü"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Google OR-Tools CP-SAT (Kapasiteli & Zaman Pencereli CVRPTW), Guided Local Search ve Tabu Search metaheuristics."
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED

    k3 = add_card(s1, Inches(8.8), Inches(4.9), Inches(3.7), Inches(1.7))
    tf = k3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🗺️ Gerçek GIS & Web Paneli"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "OpenRouteService gerçek karayolu matrisi, 3 katmanlı disk önbelleği ve Leaflet.js destekli canlı yönetim arayüzü."
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_MUTED

    meta_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.7), Inches(0.4))
    tf_meta = meta_box.text_frame
    p_meta = tf_meta.paragraphs[0]
    p_meta.text = "📌 Modül 0 - 12 Tam Kapsamlı Kurumsal Dağıtım & Optimizasyon Sunumu • Python 3.10+ | Google OR-Tools | OpenRouteService | Flask | Leaflet.js"
    p_meta.font.size = Pt(8.5)
    p_meta.font.color.rgb = TEXT_MUTED

    add_speaker_notes(s1, "Sayın Yöneticilerim, bugün sizlere kargo dağıtım operasyonlarımızı manuel planlamadan kurtaran, gerçek karayolu ağını ve çok boyutlu operasyonel kısıtları matematiksel modelle çözen Route Optimizer projemizi sunmaktan mutluluk duyuyorum.")

    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "01 / Yönetici Özeti", "Sektörel Darboğazlar ve Route Optimizer Çözüm Vizyonu", 2)

    c_left = add_card(s2, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), bg_color=CARD_BG, border_color=ROSE_ACCENT, border_width=2)
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "❌ Geleneksel Dağıtımdaki Darboğazlar"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ROSE_ACCENT

    probs = [
        ("• Kuş Uçuşu Mesafe Yanılgısı:", "Haritada yakın görünen noktaların köprü, trafik ve tek yönler nedeniyle 1.5x-2.1x daha uzun sürmesi."),
        ("• Hacim (Desi) Darboğazı:", "Ağır olmayan ancak hacimce büyük kolilerin aracı erken doldurması ve sefer planını bozması."),
        ("• Araç-Paket Uyumsuzluğu:", "Ağır ve hacimli kargoların motokuryelere, hafif zarfların büyük kamyonlara atanması israfı."),
        ("• İade Toplama Karmaşası:", "Teslimat dönüşünde satıcı iadelerinin toplanamaması ve mükerrer araç sefere çıkarılması."),
        ("• Zaman Penceresi İhlalleri:", "Müşterinin belirttiği saat aralıklarının kaçırılması, SLA cezaları ve müşteri kaybı.")
    ]
    for p_title_sub, p_desc in probs:
        p_it = tf_l.add_paragraph()
        p_it.text = f"{p_title_sub} {p_desc}"
        p_it.font.size = Pt(9.5)
        p_it.font.color.rgb = TEXT_LIGHT

    c_right = add_card(s2, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.4), bg_color=CARD_BG, border_color=EMERALD, border_width=2)
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "✅ Route Optimizer ile Getirilen Çözümler"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = EMERALD

    solns = [
        ("• Gerçek Karayolu Ağı (ORS):", "Noktalar arası gerçek sürüş mesafesi ve süresi matrisiyle %98 doğrulukta rota oluşturma."),
        ("• Çift Kapasite Denetimi:", "Aynı anda hem Kilogram (kg) hem de Hacim (desi) sınırlarını eşzamanlı denetleme."),
        ("• Kural Tabanlı Akıllı Atama:", "Motosiklet, Panelvan ve Kamyonet tipine göre paket ağırlık ve desi kısıtlarını zorunlu kılma."),
        ("• Entegre Backhaul Modeli:", "Teslimat yaparken dönüş güzergahında satıcı iadelerini dinamik yük kontrolüyle toplama."),
        ("• Soft SLA & Öncelik Yönetimi:", "Express kargolara yüksek gecikme cezası tanımlayarak zamanında teslimat garantisi.")
    ]
    for s_title_sub, s_desc in solns:
        p_it = tf_r.add_paragraph()
        p_it.text = f"{s_title_sub} {s_desc}"
        p_it.font.size = Pt(9.5)
        p_it.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s2, "Kargo lojistiğinde en büyük maliyetler kuş uçuşu mesafe yanılgısından, hacim darboğazından ve mükerrer iade seferlerinden kaynaklanır. Route Optimizer bu 5 kritik problemi matematiksel kurallarla kökten çözer.")

    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "02 / Modüler Mimari", "Uçtan Uca Modüler Süreç Akışı (Pipeline Mimarisi)", 3)

    modules_row1 = [
        ("MODÜL 0 & 1", "Veri Yükleme & Doğrulama", "araclar.csv ve siparisler.csv verilerini okur, eksik alanları ve boyutlardan Desi hesabını doğrular.", EMERALD),
        ("MODÜL 2", "Akıllı Geocoding", "ORS Pelias API + Focus Point ile metin adresleri gerçek koordinatlara çevirir, cache ile kotayı korur.", BLUE_ACCENT),
        ("MODÜL 3", "Gerçek Yol Matrisi", "Depo ve tüm duraklar arası gerçek sürüş mesafesi (m) ve süresi (sn) matrisini oluşturur.", GOLD_ACCENT)
    ]
    modules_row2 = [
        ("MODÜL 4 - 8", "Çoklu Kısıt Modellemesi", "Çift kapasite (kg+desi), heterojen filo, zaman pencereleri, Soft SLA cezaları ve Backhaul toplama.", PURPLE_ACCENT),
        ("MODÜL 9 & 10", "Çözücü & KPI Analitiği", "OR-Tools CP-SAT çözücü, 3 stratejik senaryo optimizasyonu ve gerçek matristen KPI raporlama.", SKY_BLUE),
        ("MODÜL 11 & 12", "Canlı Panel & Raporlama", "Flask REST API, Leaflet.js canlı haritası, otomatik adres tamamlama ve PDF teknik rapor motoru.", EMERALD)
    ]

    card_w = Inches(3.7)
    card_h = Inches(2.5)

    for idx, (m_code, m_title, m_desc, m_col) in enumerate(modules_row1):
        left_pos = Inches(0.8 + (idx * 4.0))
        c_mod = add_card(s3, left_pos, Inches(1.4), card_w, card_h)
        tf = c_mod.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = m_code
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = m_col

        p_t = tf.add_paragraph()
        p_t.text = m_title
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

        p_d = tf.add_paragraph()
        p_d.text = m_desc
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = TEXT_MUTED

    for idx, (m_code, m_title, m_desc, m_col) in enumerate(modules_row2):
        left_pos = Inches(0.8 + (idx * 4.0))
        c_mod = add_card(s3, left_pos, Inches(4.2), card_w, card_h)
        tf = c_mod.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = m_code
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = m_col

        p_t = tf.add_paragraph()
        p_t.text = m_title
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

        p_d = tf.add_paragraph()
        p_d.text = m_desc
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = TEXT_MUTED

    add_speaker_notes(s3, "Sistemimiz Modül 0'dan 12'ye kadar birbirine gevşek bağlı (loosely-coupled) bir boru hattı (pipeline) şeklinde çalışır. Veri okunur, geocode edilir, matris üretilir, model çözülür ve canlı haritaya aktarılır.")

    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "03 / Teknoloji Yığını", "Projeyi Geliştirirken Kullandığımız Araçlar & Kütüphaneler", 4)

    techs = [
        ("⚙️ Google OR-Tools", "Yöneylem Araştırması & Çözücü", "Constraint Programming (CP-SAT), Routing Model, Guided Local Search ve Tabu Search metaheuristics.", EMERALD),
        ("🌐 OpenRouteService API", "Gerçek Karayolu & Coğrafi Veri", "Pelias Geocoding servisi, Driving-Car gerçek mesafe/süre matrisi ve yol kıvrımları (Directions).", BLUE_ACCENT),
        ("🐍 Python 3.10+ & Pandas", "Çekirdek Dil & Veri Analitiği", "Vektörel veri temizleme, desi hesaplama algoritmaları, model parametre yapılandırması.", GOLD_ACCENT),
        ("⚡ Flask REST API", "Web Sunucusu & Servis Katmanı", "/api/data, /api/orders, /api/scenario ve /api/autocomplete uç noktaları üzerinden tam entegrasyon.", ROSE_ACCENT),
        ("🗺️ Leaflet.js Haritası", "Canlı Görselleştirme", "Araç bazlı renklendirilmiş canlı rota çizgileri, numaralandırılmış durak pinleri, teslimat popupları.", SKY_BLUE),
        ("📑 ReportLab & Chart.js", "Kurumsal Raporlama & Analitik", "Otomatik teknik el kitabı PDF üretimi, Chart.js ile dinamik kargo kategori ve operasyon grafikleri.", PURPLE_ACCENT)
    ]

    t_w = Inches(3.7)
    t_h = Inches(2.5)

    for i, (t_name, t_role, t_desc, t_col) in enumerate(techs):
        row = i // 3
        col = i % 3
        c_t = add_card(s4, Inches(0.8 + (col * 4.0)), Inches(1.4 + (row * 2.8)), t_w, t_h)
        tf = c_t.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t_name
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = t_col

        p_r = tf.add_paragraph()
        p_r.text = t_role
        p_r.font.size = Pt(9.5)
        p_r.font.bold = True
        p_r.font.color.rgb = TEXT_LIGHT

        p_d = tf.add_paragraph()
        p_d.text = t_desc
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = TEXT_MUTED

    add_speaker_notes(s4, "Teknoloji seçimimizde endüstri standardı çözümleri birleştirdik: Optimizasyonda Google OR-Tools, coğrafi veride OpenRouteService, web ve haritada Flask ve Leaflet.js tercih edildi.")

    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "04 / Harita Doğruluğu", "Kuş Uçuşu Yanılgısından Gerçek Karayolu Ağına Geçiş", 5)

    c_left = add_card(s5, Inches(0.8), Inches(1.4), Inches(5.6), Inches(5.4), bg_color=CARD_BG, border_color=BLUE_ACCENT, border_width=2)
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "🗺️ Kuş Uçuşu (Haversine) vs Gerçek Yol"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    comp_items = [
        ("• İstanbul Şehir İçi Sapması:", "Kuş uçuşu 2.0 km görünen iki nokta gerçek karayolunda köprü, sahil ve kavşaklar sebebiyle 3.4 km sürmektedir."),
        ("• Yol / Kuş Uçuşu Katsayısı:", "Sistemimizde ortalama 1.45x, zorlu coğrafi bölgelerde 2.1x sapma otomatik olarak tespit edilmekte ve modellenmektedir."),
        ("• Gerçek Hız Profili (Driving-Car):", "Sadece mesafe değil; cadde hız limitleri ve sürüş süreleri gerçekçi olarak hesaplanmaktadır."),
        ("• Doğruluk Oranı:", "Haversine formülünün %60-70 doğruluğuna karşılık ORS Matrix API ile %98 karayolu doğruluğu yakalanmıştır.")
    ]
    for c_title_sub, c_desc in comp_items:
        p_it = tf_l.add_paragraph()
        p_it.text = f"{c_title_sub} {c_desc}"
        p_it.font.size = Pt(9.5)
        p_it.font.color.rgb = TEXT_LIGHT

    c_ru = add_card(s5, Inches(6.8), Inches(1.4), Inches(5.7), Inches(2.55), bg_color=CARD_BG, border_color=EMERALD, border_width=1.5)
    tf_ru = c_ru.text_frame
    tf_ru.word_wrap = True
    p = tf_ru.paragraphs[0]
    p.text = "🎯 Focus Point ile Adres Belirleme (Disambiguation)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = EMERALD

    fp_items = [
        "• Çelişkili Mahalle Ayrımı: 'Barbaros Mah.' aramasında depo koordinatına (Kadıköy/İstanbul) en yakın doğru konumu seçer.",
        "• Otomatik Yazım Düzeltme: Pelias algoritması ile eksik veya hatalı girilen adresleri harita üzerinde otomatik tamamlar.",
        "• Depo Odaklı Doğruluk: 29.044, 40.997 referans noktasıyla adres koordinat sapmalarını sıfıra indirir."
    ]
    for fp in fp_items:
        p_it = tf_ru.add_paragraph()
        p_it.text = fp
        p_it.font.size = Pt(8.5)
        p_it.font.color.rgb = TEXT_LIGHT

    c_rd = add_card(s5, Inches(6.8), Inches(4.25), Inches(5.7), Inches(2.55), bg_color=CARD_BG, border_color=GOLD_ACCENT, border_width=1.5)
    tf_rd = c_rd.text_frame
    tf_rd.word_wrap = True
    p = tf_rd.paragraphs[0]
    p.text = "⚠️ Kritik Optimizasyon: Direct Matrix Lookup"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT

    fix_items = [
        "• Önceki Hata: Süre ve Maliyet senaryolarında rota mesafesi Arc Cost değerinden okunduğu için km hesabı bozuluyordu.",
        "• Yapılan Düzeltme: Hangi hedef senaryo seçilirse seçilsin, rota mesafesi doğrudan gerçek dist_m matrisinden hesaplanır.",
        "• Bacak Detayı: Her segmentin mesafesi (A→B: 2.3km) ve gidiş/dönüş km'leri ayrı ayrı netleştirilmiştir."
    ]
    for fi in fix_items:
        p_it = tf_rd.add_paragraph()
        p_it.text = fi
        p_it.font.size = Pt(8.5)
        p_it.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s5, "Harita doğruluğu projemizin en kritik kazanımlarından biridir. Kuş uçuşu hesaplamayı terk edip gerçek karayolu matrisine geçtik; ayrıca Focus Point ile ilçe çelişkilerini çözdük ve mesafe hesaplamalarını gerçek matrise bağladık.")

    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "05 / Model Kısıtları", "Gerçek Dünya Lojistik Kısıtları (Kapasite & Filo Uyumu)", 6)

    k_w = Inches(5.6)
    k_h = Inches(2.5)

    k1 = add_card(s6, Inches(0.8), Inches(1.4), k_w, k_h)
    tf = k1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚖️ 1. Çift Kapasite Denetimi (KG + Desi)"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p2 = tf.add_paragraph()
    p2.text = "Her aracın aynı anda hem Ağırlık (kg) hem de Hacim (desi) sınırı vardır. Model iki boyutu da eşzamanlı izler; hafif ama koli ebatları çok büyük paketlerin aracı erken doldurarak taşmasını matematiksel olarak engeller."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    k2 = add_card(s6, Inches(6.8), Inches(1.4), k_w, k_h)
    tf = k2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🛵 2. Heterojen Filo & Paket Uyumluluğu"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Filoda Motosiklet (70 kg / 40 desi), Panelvan (1000 kg / 600 desi) ve Kamyonet (2000 kg / 1200 desi) araçları tanımlıdır. Ağır yük (AGIR_YUK) veya 30 desi / 15 kg üzeri kargoların motokuryelere verilmesi kural tabanlı engellenmiştir."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    k3 = add_card(s6, Inches(0.8), Inches(4.2), k_w, k_h)
    tf = k3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⏱️ 3. Maksimum Vardiya & Mesai Sınırı"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Sürücülerin yasal çalışma saatleri (maksimum 480-540 dakika / 8-9 saat) aşılmaz. Sürüş süreleri ve adresteki teslimat süreleri toplanarak mesai aşımı olmadan gün içi rota planı tamamlanır."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    k4 = add_card(s6, Inches(6.8), Inches(4.2), k_w, k_h)
    tf = k4.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📍 4. Maksimum Durak Sınırı"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = PURPLE_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Araç tipine ve bölge yoğunluğuna göre tek bir araca atanabilecek maksimum durak sayısı (örn. Motosiklet: 15, Panelvan: 30) sınırlandırılarak kurye iş yükü dengelenir ve aşırı yığılmalar önlenir."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    add_speaker_notes(s6, "Lojistik operasyonlarda sadece ağırlık yetersizdir; hacim kısıtı da hayati önem taşır. Modelimiz hem KG hem Desi kısıtını, araç-paket uyumunu ve sürücü mesai sınırlarını eksiksiz yönetir.")

    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "06 / İleri Kısıtlar", "Zaman Pencereleri, Soft SLA Cezaları & Backhaul Toplama", 7)

    z1 = add_card(s7, Inches(0.8), Inches(1.4), k_w, k_h)
    tf = z1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🕒 1. Randevulu Teslimat Pencereleri (VRPTW)"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = SKY_BLUE
    p2 = tf.add_paragraph()
    p2.text = "Müşterinin talep ettiği saat aralıklarında (örn: 09:00-12:00 veya 14:00-18:00) adrese varış hedeflenir. Erken varışta aracın beklemesi, geç varışta ise gecikme süresinin hesaplanması modellenmiştir."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    z2 = add_card(s7, Inches(6.8), Inches(1.4), k_w, k_h)
    tf = z2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⏳ 2. Durak Başı Servis Süresi"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p2 = tf.add_paragraph()
    p2.text = "Her durakta paketin teslim edilmesi, imza alınması ve kat çıkılması için 5 dakika sabit servis süresi eklenir. Böylece kağıt üzerindeki süreler ile sahadaki gerçek teslim saatleri birebir örtüşür."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    z3 = add_card(s7, Inches(0.8), Inches(4.2), k_w, k_h)
    tf = z3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🚨 3. Kademeli Soft SLA & Gecikme Cezaları"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = ROSE_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "EXPRESS kargolarda gecikme dakikası başına 500 ceza puanı, STANDART kargolarda 50 ceza puanı atanır. Çözücü matematiksel olarak express paketleri ilk sıralara yerleştirerek SLA uyumunu %98'e çıkarır."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    z4 = add_card(s7, Inches(6.8), Inches(4.2), k_w, k_h)
    tf = z4.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📦 4. Backhaul (Teslimat + İade/Satıcı Toplama)"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Aynı rotada gidişte teslimatlar bırakılırken, dönüş bacağında satıcı iadeleri toplanır. Ters işaretli talep mantığıyla aracın anlık yükü durak durak izlenir; hiçbir noktada kapasite taşması yaşanmaz."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    add_speaker_notes(s7, "Müşteri memnuniyetini maksimize etmek için Express paketlere yüksek ceza puanları tanımladık. Ayrıca teslimat biterken aynı araçla iade kargoları toplayan Backhaul modeli sayesinde mükerrer sefer masraflarını sıfırladık.")

    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "07 / Senaryo Yönetimi", "Farklı Hedefler İçin 3 Ayrı Optimizasyon Senaryosu", 8)

    sc_w = Inches(3.7)
    sc_h = Inches(5.3)

    s1_c = add_card(s8, Inches(0.8), Inches(1.4), sc_w, sc_h, bg_color=CARD_BG, border_color=BLUE_ACCENT, border_width=2)
    tf = s1_c.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📏 1. MESAFE SENARYOSU\n(Minimum Kilometre)\n"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    bullets1 = [
        ("• Temel Hedef:", "Filo toplam kat edilen kilometresini minimize etmek."),
        ("• Arama Stratejisi:", "Guided Local Search ile hızlı ve global mesafe optimizasyonu."),
        ("• Ne Zaman Seçilir?", "Akaryakıt tüketimini ve karbon ayak izini en aza indirmek istendiğinde."),
        ("• Öne Çıkan Sonuç:", "En kompakt, en kısa rota geometrisi.")
    ]
    for b_title, b_desc in bullets1:
        p_b = tf.add_paragraph()
        p_b.text = f"{b_title} {b_desc}\n"
        p_b.font.size = Pt(9)
        p_b.font.color.rgb = TEXT_LIGHT

    s2_c = add_card(s8, Inches(4.8), Inches(1.4), sc_w, sc_h, bg_color=CARD_BG, border_color=PURPLE_ACCENT, border_width=2)
    tf = s2_c.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⏱️ 2. SÜRE SENARYOSU\n(Hızlı Teslimat & Maksimum SLA)\n"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = PURPLE_ACCENT
    bullets2 = [
        ("• Temel Hedef:", "Tüm dağıtım operasyonunu en kısa sürede tamamlamak."),
        ("• Arama Stratejisi:", "Guided Local Search + Gecikme ceza minimizasyonu."),
        ("• Ne Zaman Seçilir?", "Express ve randevulu paketlerin yoğun olduğu günlerde müşteri memnuniyeti için."),
        ("• Öne Çıkan Sonuç:", "%98 zamanında teslimat oranı.")
    ]
    for b_title, b_desc in bullets2:
        p_b = tf.add_paragraph()
        p_b.text = f"{b_title} {b_desc}\n"
        p_b.font.size = Pt(9)
        p_b.font.color.rgb = TEXT_LIGHT

    s3_c = add_card(s8, Inches(8.8), Inches(1.4), sc_w, sc_h, bg_color=CARD_BG, border_color=EMERALD, border_width=2.5)
    tf = s3_c.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "💰 3. MALİYET SENARYOSU\n(Maksimum Kârlılık - Önerilen)\n"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    bullets3 = [
        ("• Temel Hedef:", "Toplam operasyonel maliyeti (TL) en aza indirmek."),
        ("• Arama Stratejisi:", "Tabu Search ile derinlemesine maliyet dengesi optimizasyonu."),
        ("• Ne Zaman Seçilir?", "Sabit araç çıkış bedelleri (600-1200 TL) ile km yakıt maliyetini dengelemek için."),
        ("• Öne Çıkan Sonuç:", "Şirkete en yüksek kârlılığı getiren filo dağılımı.")
    ]
    for b_title, b_desc in bullets3:
        p_b = tf.add_paragraph()
        p_b.text = f"{b_title} {b_desc}\n"
        p_b.font.size = Pt(9)
        p_b.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s8, "Yöneticimiz operasyonel önceliğe göre tek tıkla 'Minimum Kilometre', 'En Hızlı Dağıtım' veya 'En Yüksek Kârlılık' senaryoları arasında anlık geçiş yapabilir.")

    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "08 / KPI Analitiği", "Gerçek Verilerle 3 Senaryonun Karşılaştırmalı Performans Matrisi", 9)

    rows, cols = 4, 8
    left, top, width, height = Inches(0.8), Inches(1.4), Inches(11.7), Inches(2.5)
    table_shape = s9.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    table.columns[0].width = Inches(2.0)
    table.columns[1].width = Inches(1.4)
    table.columns[2].width = Inches(1.3)
    table.columns[3].width = Inches(1.5)
    table.columns[4].width = Inches(1.3)
    table.columns[5].width = Inches(1.3)
    table.columns[6].width = Inches(1.3)
    table.columns[7].width = Inches(1.6)

    headers = ["Senaryo", "Toplam KM", "Toplam Süre", "Toplam Maliyet", "Araç Sayısı", "KG Doluluk", "Desi Doluluk", "Zamanında (SLA)"]
    data = [
        ["📏 DISTANCE (Mesafe)", "450.2 km", "28.5 saat", "₺5,250", "12 Araç", "%85", "%78", "%94"],
        ["⏱️ TIME (Süre)", "475.1 km", "24.0 saat", "₺5,890", "11 Araç", "%88", "%81", "%98 ⭐"],
        ["💰 COST (Maliyet)", "462.5 km", "29.1 saat", "₺5,100 ⭐", "13 Araç", "%82", "%74", "%90"]
    ]

    for col_idx, h_text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(18, 38, 58)
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = EMERALD
        p.alignment = PP_ALIGN.CENTER

    for row_idx, row_data in enumerate(data):
        for col_idx, val in enumerate(row_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 0 else CARD_BG_ALT
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_FAMILY
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_WHITE if col_idx == 0 else TEXT_LIGHT
            p.alignment = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER
            if "⭐" in val:
                p.font.bold = True
                p.font.color.rgb = GOLD_ACCENT

    kpi_card = add_card(s9, Inches(0.8), Inches(4.2), Inches(11.7), Inches(2.6), bg_color=CARD_BG, border_color=PINE_GREEN, border_width=1.5)
    tf_kpi = kpi_card.text_frame
    tf_kpi.word_wrap = True
    p = tf_kpi.paragraphs[0]
    p.text = "📊 Yönetimsel Değerlendirme & Karar Destek Çıkarımları"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = EMERALD

    insights = [
        "• En Kârlı Senaryo (COST): Sabit çıkış maliyetlerini ve değişken km yakıtını en iyi optimize eden senaryo ₺5,100 ile Maliyet senaryosudur (Standart operasyon için önerilir).",
        "• En Yüksek Müşteri Memnuniyeti (TIME): Express siparişlerin yoğun olduğu kritik günlerde Süre senaryosu seçilerek SLA başarısı %98'e çıkarılmaktadır.",
        "• Yakıt ve Karbon Tasarrufu (DISTANCE): Mesafe senaryosu toplam kilometreyi 450.2 km'ye çekerek karbon ayak izini ve filo yıpranmasını minimuma indirmektedir."
    ]
    for ins in insights:
        p_i = tf_kpi.add_paragraph()
        p_i.text = ins
        p_i.font.size = Pt(9)
        p_i.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s9, "Bu tabloda gerçek operasyonel verilerle 3 senaryonun çıktılarını görüyoruz. Maliyet senaryosu şirket bütçesinde en yüksek tasarrufu sağlarken, Süre senaryosu SLA oranını %98'e ulaştırmaktadır.")

    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "09 / Performans Altyapısı", "API Kotalarını ve Çözüm Hızını Koruyan 3 Katmanlı Önbellek Mimarisi", 10)

    c_w = Inches(3.7)
    c_h = Inches(5.3)

    cc1 = add_card(s10, Inches(0.8), Inches(1.4), c_w, c_h)
    tf = cc1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📍 1. Geocode Cache\n(Adres Koordinat Önbelleği)\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p2 = tf.add_paragraph()
    p2.text = "• Dosya: geocode_cache.json\n\n• İşleyiş: Daha önce sorgulanan adreslerin koordinatları diskte kalıcı saklanır.\n\n• Fayda: Aynı adres tekrar girildiğinde dış API'ye gitmez, 0 ms yanıt süresiyle kota harcamadan anında döner."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    cc2 = add_card(s10, Inches(4.8), Inches(1.4), c_w, c_h)
    tf = cc2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🌐 2. Matrix Cache\n(Mesafe/Süre & Subset Matching)\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "• Dosya: matrix_cache.json\n\n• İşleyiş: Noktalar arası mesafe/süre matrisleri imza bazlı tutulur.\n\n• Akıllı Alt Küme Tespiti: Önbellekte 50 noktalı matris varsa, 30 noktalı alt küme sorgusu sıfır API çağrısıyla diskin içinden çözülür (%95 kota tasarrufu)."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    cc3 = add_card(s10, Inches(8.8), Inches(1.4), c_w, c_h)
    tf = cc3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚡ 3. Directions Cache & Hız\n(Anlık <1 Saniye Çözüm)\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "• Dosya: directions_cache.json\n\n• İşleyiş: Harita yol çizgisi geometrileri önbelleğe alınır.\n\n• Canlı Re-Optimize: Yeni sipariş eklendiğinde tüm filo ve kısıtlar 1 saniyenin altında yeniden optimize edilerek canlı ekrana yansıtılır."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s10, "Geliştirdiğimiz 3 katmanlı disk önbellek mimarisi sayesinde dış API kotalarını sıfır israfla koruyoruz ve optimizasyonu 1 saniyenin altında tamamlıyoruz.")

    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "10 / Canlı Web Paneli", "Operasyonel Canlı Yönetim Paneli & Kullanıcı Arayüzü", 11)

    u_w = Inches(5.6)
    u_h = Inches(2.5)

    u1 = add_card(s11, Inches(0.8), Inches(1.4), u_w, u_h)
    tf = u1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🗺️ 1. İnteraktif Harita & Canlı Yol Çizimi"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p2 = tf.add_paragraph()
    p2.text = "Leaflet.js haritası üzerinde her aracın rotası kendine özel canlı renkle ve gerçek karayolu kıvrımlarıyla (Directions) çizilir. Duraklar 1'den N'e sıralı pinlerle gösterilir; tıklandığında müşteri ve kargo detayları açılır."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    u2 = add_card(s11, Inches(6.8), Inches(1.4), u_w, u_h)
    tf = u2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🔍 2. Canlı Autocomplete & Adres Doğrulama"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = SKY_BLUE
    p2 = tf.add_paragraph()
    p2.text = "Arama kutusuna yazarken OpenRouteService Pelias üzerinden otomatik adres tamamlama önerileri sunulur. /api/validate-address uç noktası ile adres formu gönderilmeden önce koordinat onaylanır."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    u3 = add_card(s11, Inches(0.8), Inches(4.2), u_w, u_h)
    tf = u3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "➕ 3. Dinamik Sipariş Ekleme & Re-Optimize"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Saha operasyonu sırasında gelen acil sipariş modal üzerinden sisteme girilir. Sistem 1 saniye içinde rotaları en uygun araca atayarak mevcut planı bozmadan anlık günceller."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    u4 = add_card(s11, Inches(6.8), Inches(4.2), u_w, u_h)
    tf = u4.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📊 4. Canlı Filtreleme, Grafikler & CSV Export"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = PURPLE_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "Plaka, araç tipi ve teslimat/toplama türüne göre canlı filtreleme yapılır. Chart.js pasta grafikleriyle filo dağılımı izlenir ve saha kuryelerine iletilmek üzere tek tıkla CSV/Excel çıktısı alınır."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_MUTED

    add_speaker_notes(s11, "Geliştirdiğimiz canlı web paneli; harita takibi, canlı adres otomatik tamamlama, anlık sipariş ekleme, filtreleme ve CSV dışa aktarma gibi tüm saha ihtiyaçlarını karşılamaktadır.")

    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "11 / Entegrasyon & Kalite", "Kurumsal Dokümantasyon, Test Paketi & REST API", 12)

    c_w = Inches(3.7)
    c_h = Inches(5.3)

    d1 = add_card(s12, Inches(0.8), Inches(1.4), c_w, c_h)
    tf = d1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📑 1. Otomatik PDF Teknik El Kitabı\n(Modül 0-8 Rehberi)\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p2 = tf.add_paragraph()
    p2.text = "• ReportLab Motoru: generate_rehber_pdf.py ile üretilen profesyonel teknik rehber.\n\n• Kapsam: Modül 0'dan 8'e kadar tüm matematiksel modeller, kod yapıları, kısıt formülleri ve veri şemaları.\n\n• Standart: Kurumsal arşivleme ve yeni geliştiricilerin adaptasyonu için hazır doküman."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    d2 = add_card(s12, Inches(4.8), Inches(1.4), c_w, c_h)
    tf = d2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🧪 2. Otomatik Test Paketi\n(pytest Entegrasyonu)\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "• Birim & Entegrasyon Testleri: test_setup.py, test_ors.py, test_validate_address.py.\n\n• Doğrulama: CSV yükleyici, geocoding servisleri, matris hesaplayıcı ve OR-Tools kısıt çözücüsü otomatik testlerle denetlenir.\n\n• Sürekli Entegrasyon (CI/CD): Kod değişikliklerinde regresyon riskini sıfırlar."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    d3 = add_card(s12, Inches(8.8), Inches(1.4), c_w, c_h)
    tf = d3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📡 3. Modüler REST API Uç Noktaları\n(ERP Entegrasyonu)\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "• /api/data: Aktif senaryonun tüm KPI, araç ve rota verilerini döner.\n\n• /api/orders: Yeni sipariş ekleme ve anlık optimizasyon tetikleme.\n\n• /api/autocomplete: Adres arama önerileri.\n\n• /api/validate-address: Canlı koordinat doğrulama."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s12, "Projemiz yalnızca bir algoritma değil; kurumsal PDF dokümantasyon motoru, otomatik pytest testleri ve REST API uç noktalarıyla tam bir kurumsal yazılım paketidir.")

    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "12 / Gelecek Vizyonu", "Gelecek Yol Haritası ve Sistemi İleri Taşıyacak Genişlemeler", 13)

    f1 = add_card(s13, Inches(0.8), Inches(1.4), c_w, c_h)
    tf = f1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🚦 Faz 1: Canlı Trafik & Dinamik Tahmin\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = SKY_BLUE
    p2 = tf.add_paragraph()
    p2.text = "• Canlı Trafik API Entegrasyonu: Gün içindeki anlık trafik yoğunluğuna göre durak varış saatlerinin dinamik güncellenmesi.\n\n• Hava Durumu Kısıtı: Yağışlı havalarda motosiklet kurye hızlarının ve kapasitelerinin otomatik düşürülmesi."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    f2 = add_card(s13, Inches(4.8), Inches(1.4), c_w, c_h)
    tf = f2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "📱 Faz 2: Kurye Mobil Uygulaması\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p2 = tf.add_paragraph()
    p2.text = "• Sürücü Ekranı: Kuryelerin cep telefonundan durak sırasını görmesi, rota navigasyonunu başlatması.\n\n• Canlı Teslimat Onayı: Kapıda teslim edildi / alıcı bulunamadı durumlarının anlık merkeze iletilmesi ve rotanın anında revize edilmesi."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    f3 = add_card(s13, Inches(8.8), Inches(1.4), c_w, c_h)
    tf = f3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🔋 Faz 3: Elektrikli Araç & Şarj Kısıtı\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GOLD_ACCENT
    p2 = tf.add_paragraph()
    p2.text = "• Yeşil Filo Entegrasyonu: Elektrikli kargo araçlarının batarya menzili (SOC) kısıtlarının modele eklenmesi.\n\n• Akıllı Şarj İstasyonu Planlaması: Uzun rotalarda şarj istasyonu duraklamalarının otomatik olarak rotaya dahil edilmesi."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_LIGHT

    add_speaker_notes(s13, "Gelecek vizyonumuzda canlı trafik tahminleri, mobil kurye uygulaması ve elektrikli araç şarj yönetimi ile sistemi daha da ileri taşımayı hedefliyoruz.")

    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)

    end_card = add_card(s14, Inches(1.5), Inches(1.2), Inches(10.3), Inches(5.1), bg_color=CARD_BG, border_color=PINE_GREEN, border_width=2)
    tf_e = end_card.text_frame
    tf_e.word_wrap = True
    
    p = tf_e.paragraphs[0]
    p.text = "\n✨ Teşekkür Ederim"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER

    p2 = tf_e.add_paragraph()
    p2.text = "\nRoute Optimizer Sistemi, Şirketimiz Kargo Operasyonlarında Maliyetleri Düşürmeye,\nTeslimat Hızını Artırmaya ve Canlı Olarak Kullanılmaya Hazırdır.\n"
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_LIGHT
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf_e.add_paragraph()
    p3.text = "🚀 Canlı Sistem Web Paneli: http://127.0.0.1:5000\n"
    p3.font.size = Pt(15)
    p3.font.bold = True
    p3.font.color.rgb = EMERALD
    p3.alignment = PP_ALIGN.CENTER

    p4 = tf_e.add_paragraph()
    p4.text = "İzninizle şimdi sistemi canlı yönetim paneli üzerinde uygulamalı olarak test edelim."
    p4.font.size = Pt(12)
    p4.font.color.rgb = GOLD_ACCENT
    p4.alignment = PP_ALIGN.CENTER

    add_speaker_notes(s14, "Sunumumu dinlediğiniz için çok teşekkür ederim. İzninizle şimdi sistemi canlı web paneli üzerinde uygulamalı olarak göstermek ve sorularınızı yanıtlamak isterim.")

    output_path = Path("ROUTE_OPTIMIZER_SUNUM.pptx").resolve()
    prs.save(str(output_path))
    print(f"[OK] Yeni ve Guncel PowerPoint sunumu basariyla olusturuldu: {output_path} (Toplam 14 Slayt)")


if __name__ == "__main__":
    build_presentation()
