"""Modül 8 — Toplama/İade (backhaul) yük mantığı.

TESLIMAT durakları araçtaki yükü azaltır (-), TOPLAMA durakları artırır (+).
Bu sürümde toplama kargolar şubeye geri getirilir (noktadan-noktaya değil).
Kritik kural: araçtaki yük (kg ve desi) rotanın HİÇBİR anında kapasiteyi aşmamalı.

Basit stratejisi: toplama paketlerinin talebini negatif sayıyoruz
(kapasite boyutunda -kg, -desi olarak) ki çözücü otomatik olarak
"önce teslimat sonra toplama" tercih etsin.
"""
import pandas as pd


def compute_adjusted_demands(points: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Her durak için kapasite talebini (kg ve desi) hesapla.

    TESLIMAT ve TOPLAMA'nın İKİSİ de kapasiteyi POZİTİF tüketir: bir araç,
    rota boyunca taşıdığı hem teslim edilecek hem de toplanacak kargoya aynı
    anda yer bulabilmelidir. Bu, tek kapasite boyutuyla güvenli (aşırı yükleme
    yapmayan) modeldir.

    NOT (neden negatif DEĞİL): Toplama talebini negatif yapmak, aracın net
    yükünü olduğundan az gösterir ve gerçekte kapasiteyi aşan yük atanmasına
    yol açar (ör. 270 desi'lik gerçek yük, 200 kapasiteli araca sığmış gibi
    görünür). Bu yüzden burada tüm talepler pozitif tutulur.

    Not: "Toplama dönüşte yer açar" gibi ileri backhaul optimizasyonu (yükün
    rota boyunca artıp azaldığı gerçek modelleme) sonraki bir geliştirmedir;
    doğru kurulumu iki uçlu (pickup&delivery) düğüm eşleştirmesi gerektirir.

    Return: (adjusted_kg, adjusted_desi) Series'ler — hepsi pozitif.
    """
    adjusted_kg = points["agirlik_kg"].abs().copy()
    adjusted_desi = points["desi"].abs().copy()
    return adjusted_kg, adjusted_desi


def apply_pickup_delivery(routing, manager, points: pd.DataFrame):
    """Teslimat/toplama yük değişimini kapasite boyutlarına uygular (Modül 8).

    Basit backhaul stratejisi: TOPLAMA paketlerinin talebini negatif yap.
    Bu, model.py'de capacity dimension'ı güncelleme gerekir (adjusted demands).

    NOT: Bu versiyonda, capacity dimension'lar build_model'de zaten
    oluşturulmuş, bu fonksiyon ise post-processing / doğrulama amaçlı.
    Tam implementasyon için model kuruluma integral edilmeli.
    """
    pass
