# 🚚 Route Optimizer — Akıllı Lojistik & Rota Optimizasyonu Karar Destek Sistemi

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google OR-Tools](https://img.shields.io/badge/Optimization-Google%20OR--Tools-orange.svg)](https://developers.google.com/optimization)
[![OpenRouteService](https://img.shields.io/badge/GIS-OpenRouteService%20API-green.svg)](https://openrouteservice.org/)
[![Flask Dashboard](https://img.shields.io/badge/Web-Flask%20%2B%20Leaflet.js-darkblue.svg)](http://127.0.0.1:5000)

**Route Optimizer**, modern kargo ve dağıtım operasyonları için geliştirilmiş; çok araçlı, çok kısıtlı ve çok senaryolu bir **Kapasiteli ve Zaman Pencereli Araç Rotalama (CVRPTW)** karar destek yazılımıdır. 

Sistem; kuş uçuşu mesafeler yerine **gerçek karayolu ağını** (OpenRouteService) kullanarak, filodaki araçların kapasite, mesai ve kargo tiplerine göre en uygun dağıtım planını milisaniyeler içinde matematiksel olarak optimize eder.

---

## 🌟 Öne Çıkan Temel Özellikler

- 🎯 **3 Farklı Optimizasyon Senaryosu:**
  - 📏 **Mesafe Senaryosu:** Toplam kat edilen kilometreyi ve karbon ayak izini minimize eder.
  - ⏱️ **Süre Senaryosu:** Teslimatları en kısa sürede tamamlayarak müşteri memnuniyetini (SLA) maksimize eder.
  - 💰 **Maliyet Senaryosu:** Sabit araç çıkış bedelleri ve km başı yakıt/amortisman maliyetlerini dengeleyerek en yüksek kârlılığı sağlar.
- 🚛 **Heterojen Filo Yönetimi:** Motosiklet, Panelvan ve Kamyonet gibi farklı kapasite, hız ve maliyet profiline sahip araçların eşzamanlı yönetimi.
- ⚖️ **Çok Boyutlu Kısıt Modellemesi:**
  - **Çift Kapasite:** Aynı anda hem Ağırlık (kg) hem de Hacim (desi) sınırlarının denetlenmesi.
  - **Zaman Pencereleri & Soft SLA:** Müşterinin talep ettiği saat aralığında teslimat ve gecikme cezası puanlaması.
  - **Maksimum Durak & Vardiya Sınırı:** Sürücü mesai saatleri ve yasal mola limitleri.
  - **Teslimat & Toplama (Backhaul):** Aynı rotada hem müşteriye teslimat hem de mağaza/iade toplama yönetimi.
  - **Paket-Araç Uyumluluğu:** Ağır yüklerin motokuryelere atanmasının engellenmesi.
- 🗺️ **Canlı GIS & Harita Entegrasyonu:**
  - Leaflet.js tabanlı, araç bazlı renklendirilmiş canlı rota çizgileri ve numaralandırılmış durak popupları.
  - Gerçek zamanlı adres otomatik tamamlama (Autocomplete) ve geocoding motoru.
  - API kotasını ve performansı koruyan **2 katmanlı akıllı disk önbellek (cache)** mimarisi.
- 📊 **Etkileşimli Yönetim Paneli:**
  - Anlık KPI göstergeleri (Toplam KM, Tahmini Maliyet, Aktif Araç Sayısı, SLA Uyumu).
  - Canlı filtreleme (Plaka, Araç Türü, İşlem Tipi, Arama).
  - Yeni sipariş ekleme ve tek tıkla anlık yeniden optimizasyon (Re-optimize).

---

## 🏗️ Proje Mimarisi ve Klasör Yapısı

```bash
route_optimizer/
│
├── app.py                      # Flask REST API ve Dashboard Web Sunucusu
├── config.yaml                 # Sistem yapılandırması (hedef senaryo, API kotaları, dosya yolları)
├── requirements.txt            # Python kütüphane bağımlılıkları
├── env
├── dashboard.html              # Modern, interaktif canlı yönetim paneli (Leaflet + Chart.js)
│
├── data/                       # Girdi Veri Setleri
│   ├── araclar.csv             # Filo bilgileri (plaka, araç tipi, kapasite, maliyet)
│   └── siparisler.csv          # Canlı sipariş listesi (adres, işlem, kg, desi, saat)
│
├── src/                        # Çekirdek Optimizasyon ve Servis Katmanı
│   ├── config_loader.py        # Konfigürasyon ve çevre değişkenleri yükleyici
│   ├── loader.py               # CSV veri okuma, temizleme ve doğrulama motoru
│   ├── geocode.py              # ORS Geocoding (Adres -> Koordinat) servisi
│   ├── matrix.py               # ORS Mesafe ve Süre matrisi oluşturucu
│   ├── model.py                # Google OR-Tools CVRPTW kısıt ve model kurucu
│   ├── solve.py                # Metaheuristics çözücü ve rota çıkarma motoru
│   ├── evaluate.py             # KPI ve maliyet hesaplama analitiği
│   ├── visualize.py            # Folium ve görsel harita katmanı
│   └── service.py              # Web API ile optimizasyon motoru entegrasyonu
│
├── cache/                      # Önbellek ve Üretilen Çıktılar
│   ├── geocode_cache.json      # Coğrafi koordinat önbelleği (Kota koruyucu)
│   ├── matrix_cache.json       # Mesafe/süre matris önbelleği
│   └── directions_cache.json   # Rota geometrisi önbelleği
│
└── tests/                      # Otomatik Birim ve Entegrasyon Testleri
    └── test_*.py               # Modül testleri (Doğrulama, Geocode, Matris, Model)
```

---

## 🚀 Kurulum ve Çalıştırma

### 1. Gereksinimler
- Python 3.10 veya üzeri
- OpenRouteService (ORS) ücretsiz API anahtarı ([openrouteservice.org](https://openrouteservice.org/) üzerinden temin edilebilir)

### 2. Adım Adım Kurulum

```bash
# 1. Proje dizinine gidin
cd route_optimizer

# 2. Sanal ortam (virtualenv) oluşturun ve aktif edin
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. .env dosyanızı oluşturun ve ORS API anahtarınızı tanımlayın
echo ORS_API_KEY=your_openrouteservice_api_key_here > .env
```

### 3. Web Sunucusunu Başlatma

```bash
python app.py
```

Tarayıcınızdan **`http://127.0.0.1:5000`** adresine giderek canlı gösterge paneline erişebilirsiniz.

---

## 📡 REST API Uç Noktaları (Endpoints)

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `GET` | `/` | Canlı Yönetim Paneli (HTML) |
| `GET` | `/api/data` | Aktif senaryonun KPI'ları, araçları, rotaları ve siparişleri (`?scenario=distance\|time\|cost`) |
| `POST` | `/api/scenario` | Aktif optimizasyon senaryosunu değiştirir |
| `POST` | `/api/orders` | Yeni bir sipariş ekler ve rotaları dinamik olarak yeniden optimize eder |
| `POST` | `/api/optimize` | Tüm optimizasyon sürecini baştan tetikler |
| `GET` | `/api/autocomplete` | Canlı adres arama kutusu için ORS önerilerini döner (`?q=kadikoy`) |

---

## 📊 Matematiksel Modelleme & Karar Kısıtları

Sistem, Google OR-Tools Constraint Programming (CP-SAT / Routing) kütüphanesi üzerinde aşağıdaki matematiksel boyutları çözer:

```math
\min \sum_{v \in V} \sum_{i,j \in N} c_{ij}^v \cdot x_{ij}^v + \sum_{v \in V} F_v \cdot y_v + \sum_{i \in N} P_i \cdot \text{Late}_i
```

- **$c_{ij}^v$:** Seçilen senaryoya göre $i$ ve $j$ noktaları arasındaki arc maliyeti (metre, saniye veya kuruş).
- **$F_v$:** $v$ aracının sabit sefere çıkış maliyeti.
- **$P_i$:** $i$ paketinin zaman penceresi aşımındaki gecikme cezası (Express: 500 puan/dk, Standart: 50 puan/dk).
- **Kapasite Kısıtları:** $\sum \text{Ağırlık} \le \text{Kap}_{kg}$, $\sum \text{Hacim} \le \text{Kap}_{desi}$
- **Mesai & Durak:** Rota Süresi $\le \text{Vardiya}_{max}$, Uğranan Durak $\le \text{Durak}_{max}$

---

## 🧪 Testleri Çalıştırma

Projede bulunan birim ve entegrasyon testlerini çalıştırmak için:

```bash
pytest -v
```

---

## 👩‍💻 Geliştirici & Lisans
Bu proje, modern lojistik yönetiminde yapay zeka ve yöneylem araştırması yaklaşımlarını birleştiren ileri düzey bir Ar-Ge ve optimizasyon çalışması olarak geliştirilmiştir.
MIT Lisansı altında sunulmaktadır.
