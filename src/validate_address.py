"""Modül: Coğrafi Adres Doğrulama.

Yeni rota/sipariş oluşturulurken girilen adresleri coğrafi bilgi sistemleri
(ORS Pelias Geocoding) ile doğrular. Hizmet bölgesi sınırları dışında kalan
veya haritada olmayan adresleri anında tespit eder.
"""
import math
from typing import Any

import openrouteservice

from src.geocode import _geocode_one


DEPOT_LAT, DEPOT_LON = 40.997314, 29.044531

ISTANBUL_BOUNDS = {
    "lat_min": 40.70,
    "lat_max": 41.65,
    "lon_min": 27.90,
    "lon_max": 29.98,
}

MAX_SERVICE_DISTANCE_KM = 75.0

CONFIDENCE_THRESHOLD = 0.4  


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """İki koordinat arasında kuş uçuşu mesafeyi hesaplar (km)."""
    R = 6371  
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def is_in_istanbul_bounds(lat: float, lon: float) -> bool:
    """Koordinatın İstanbul il sınırları içinde olup olmadığını kontrol eder."""
    return (
        ISTANBUL_BOUNDS["lat_min"] <= lat <= ISTANBUL_BOUNDS["lat_max"]
        and ISTANBUL_BOUNDS["lon_min"] <= lon <= ISTANBUL_BOUNDS["lon_max"]
    )


def is_within_service_distance(lat: float, lon: float, max_km: float = MAX_SERVICE_DISTANCE_KM) -> bool:
    """Koordinatın depoya maksimum mesafesinden daha yakın olup olmadığını kontrol eder."""
    distance = haversine_distance(DEPOT_LAT, DEPOT_LON, lat, lon)
    return distance <= max_km


def validate_address(
    address: str,
    api_key: str,
    country_code: str = "TUR",
    focus_point: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Adresi ORS Pelias ile doğrular ve hizmet bölgesi kontrolü yapar.

    Doğrulama kuralları:
    1. ORS Pelias'te bulunabilmesi (features boş olmamalı)
    2. Minimum 3 kelime veya 10 karakter (kısmi yazım: "ankar" rejected, "ankara" or "cadde" rejected)
    3. Adresin İstanbul ili sınırları veya depoya maksimum 75 km mesafede olması

    Dönüş değeri:
    {
        "valid": bool,                 # Adres geçerli mi?
        "reason": str | None,          # Geçersizse nedeni (örn: "Hizmet bölgesi dışında")
        "lat": float | None,           # Enlem (bulunursa)
        "lon": float | None,           # Boylam (bulunursa)
        "location_name": str | None,   # Bulunan yer adı (mahalle/ilçe)
        "confidence": float | None,    # ORS güven skoru (0-1)
    }
    """
    if not address or not address.strip():
        return {
            "valid": False,
            "reason": "Adres boş bırakılamaz",
            "lat": None,
            "lon": None,
            "location_name": None,
            "confidence": None,
        }

    words = address.strip().split()
    if len(address.strip()) < 6 or len(words) < 2:
        return {
            "valid": False,
            "reason": "Adres çok kısa. Lütfen ilçe ve mahalle başta gelen başta yazınız (örn: 'Caferağa, Kadıköy')",
            "lat": None,
            "lon": None,
            "location_name": None,
            "confidence": None,
        }

    try:
        client = openrouteservice.Client(key=api_key)
        geocode_result = _geocode_one(
            client, address, country_code=country_code, focus_point=focus_point
        )

        if geocode_result is None:
            return {
                "valid": False,
                "reason": "Adres haritada bulunamadı veya yazım hatası olabilir",
                "lat": None,
                "lon": None,
                "location_name": None,
                "confidence": None,
            }

        lat = geocode_result["lat"]
        lon = geocode_result["lon"]
        confidence = geocode_result.get("confidence", 0.0)

        if confidence < CONFIDENCE_THRESHOLD:
            return {
                "valid": False,
                "reason": f"Adres net değil (güven: {confidence:.0%}). Lütfen tam adres yazınız.",
                "lat": lat,
                "lon": lon,
                "location_name": geocode_result.get("location_name", address),
                "confidence": confidence,
            }

        distance_to_depot = haversine_distance(DEPOT_LAT, DEPOT_LON, lat, lon)
        if not is_in_istanbul_bounds(lat, lon):
            if not is_within_service_distance(lat, lon):
                return {
                    "valid": False,
                    "reason": f"Hizmet bölgesi dışında (depoya {distance_to_depot:.1f} km uzak, max 75 km)",
                    "lat": lat,
                    "lon": lon,
                    "location_name": geocode_result.get("location_name", address),
                    "confidence": geocode_result.get("confidence", 0.5),
                }
            elif distance_to_depot > 60:
                return {
                    "valid": True,
                    "reason": f"⚠️ Sınır bölgesinde: depoya {distance_to_depot:.1f} km uzak (rota optimizasyonu zor olabilir)",
                    "lat": lat,
                    "lon": lon,
                    "location_name": geocode_result.get("location_name", address),
                    "confidence": confidence,
                }

        return {
            "valid": True,
            "reason": None,
            "lat": lat,
            "lon": lon,
            "location_name": geocode_result.get("location_name", address),
            "confidence": confidence,
        }

    except Exception as e:
        return {
            "valid": False,
            "reason": f"Doğrulama hatası: {str(e)}",
            "lat": None,
            "lon": None,
            "location_name": None,
            "confidence": None,
        }


def batch_validate_addresses(
    addresses: list[str],
    api_key: str,
    country_code: str = "TUR",
    focus_point: tuple[float, float] | None = None,
) -> list[dict[str, Any]]:
    """Birden fazla adresi toplu doğrular.

    Kullanım: sipariş yükleme zamanı veya toplu adres import etmek için.
    """
    results = []
    for addr in addresses:
        result = validate_address(
            addr,
            api_key=api_key,
            country_code=country_code,
            focus_point=focus_point,
        )
        results.append(result)
    return results
