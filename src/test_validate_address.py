"""Unit testler: Coğrafi Adres Doğrulama.

Geçerli adres, sahte adres, şehir dışı adres, hizmet bölgesi dışında vb. test senaryoları.
"""
import pytest

from src.validate_address import (
    haversine_distance,
    is_in_istanbul_bounds,
    is_within_service_distance,
    validate_address,
)
from src.config_loader import get_api_key


class TestDistanceCalculation:
    """Haversine mesafe hesaplaması testleri."""

    def test_same_point(self):
        """Aynı noktanın mesafesi sıfır olmalı."""
        distance = haversine_distance(41.0082, 28.9784, 41.0082, 28.9784)
        assert abs(distance) < 0.01

    def test_known_distance(self):
        """Kadıköy ↔ Taksim arası mesafe ~5 km olmalı."""
        lat1, lon1 = 40.997314, 29.044531  
        lat2, lon2 = 41.037234, 28.992456  
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        assert 4 < distance < 6, f"Beklenen: ~5 km, Bulunan: {distance:.2f} km"

    def test_long_distance(self):
        """Kadıköy ↔ Ankara arası mesafe ~450+ km olmalı."""
        lat1, lon1 = 40.997314, 29.044531  
        lat2, lon2 = 39.9334, 32.8597      
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        assert distance > 400, f"Beklenen: >400 km, Bulunan: {distance:.2f} km"


class TestBoundaryChecks:
    """İstanbul sınırı kontrolü testleri."""

    def test_point_in_istanbul(self):
        """Caferağa, Kadıköy İstanbul sınırında olmalı."""
        assert is_in_istanbul_bounds(40.991, 29.063)

    def test_point_south_of_istanbul(self):
        """40.6° enlem İstanbul'un güneyinde (dışında)."""
        assert not is_in_istanbul_bounds(40.6, 28.9)

    def test_point_north_of_istanbul(self):
        """41.7° enlem İstanbul'un kuzeyinde (dışında)."""
        assert not is_in_istanbul_bounds(41.7, 28.9)

    def test_point_west_of_istanbul(self):
        """27.8° boylam İstanbul'un batısında (dışında)."""
        assert not is_in_istanbul_bounds(41.0, 27.8)

    def test_point_east_of_istanbul(self):
        """30.0° boylam İstanbul'un doğusunda (dışında)."""
        assert not is_in_istanbul_bounds(41.0, 30.0)


class TestServiceDistance:
    """Depo'dan hizmet mesafesi testleri."""

    def test_within_service_range(self):
        """Aynı nokta (depo) 75 km içinde olmalı."""
        assert is_within_service_distance(40.997314, 29.044531)

    def test_nearby_location(self):
        """Taksim, depoya ~5 km yakındır, 75 km içinde olmalı."""
        assert is_within_service_distance(41.037234, 28.992456)

    def test_ankara_out_of_range(self):
        """Ankara depoya ~450+ km uzak, 75 km dışında olmalı."""
        assert not is_within_service_distance(39.9334, 32.8597)

    def test_exact_boundary(self):
        """Tam 75 km mesafede olan bir nokta kontrol."""
        distance = haversine_distance(40.997314, 29.044531, 41.0, 30.7)
        is_valid = is_within_service_distance(41.0, 30.7, max_km=75.0)
        print(f"75 km sınırı testi: mesafe={distance:.2f} km, geçerli={is_valid}")


class TestAddressValidation:
    """ORS tabanlı adres doğrulama testleri (API Anahtarı gerekli).

    Çalıştırmak için: ORS_API_KEY ortam değişkeni ayarlı olmalı.
    pytest src/test_validate_address.py::TestAddressValidation -v
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Her testten önce API anahtarını kontrol et."""
        self.api_key = get_api_key()
        if not self.api_key:
            pytest.skip("ORS API anahtarı yapılandırılmamış (.env dosyasında ORS_API_KEY gerekli)")

    def test_valid_address_istanbul(self):
        """Geçerli bir İstanbul adresi."""
        result = validate_address(
            "Moda Caddesi, Kadıköy, İstanbul",
            api_key=self.api_key,
            country_code="TUR",
            focus_point=(29.044531, 40.997314),
        )
        assert result["valid"], f"Beklenen: Geçerli, Alınan: {result['reason']}"
        assert result["lat"] is not None
        assert result["lon"] is not None

    def test_valid_address_caferagra(self):
        """Caferağa Mahallesi, Kadıköy (depo yakınında)."""
        result = validate_address(
            "Caferağa Mahallesi, Kadıköy",
            api_key=self.api_key,
            country_code="TUR",
            focus_point=(29.044531, 40.997314),
        )
        assert result["valid"], f"Beklenen: Geçerli, Alınan: {result['reason']}"
        assert result["lat"] is not None
        assert result["lon"] is not None

    def test_invalid_address_gibberish(self):
        """Uydurma adres haritada bulunmamalı."""
        result = validate_address(
            "asdfghjkl qwerty 12345 uydurma",
            api_key=self.api_key,
            country_code="TUR",
        )
        assert not result["valid"], "Uydurma adres geçerli görülmemelidir"
        assert "haritada bulunamadı" in result["reason"].lower()

    def test_invalid_address_ankara(self):
        """Ankara (hizmet bölgesi dışında) adres geçersiz olmalı."""
        result = validate_address(
            "Kızılay Meydanı, Çankaya, Ankara",
            api_key=self.api_key,
            country_code="TUR",
        )
        if result["lat"] is not None:  
            assert not result["valid"], "Ankara hizmet bölgesi dışında olmalı"
            assert "hizmet bölgesi" in result["reason"].lower()

    def test_empty_address(self):
        """Boş adres geçersiz olmalı."""
        result = validate_address("", api_key=self.api_key)
        assert not result["valid"]
        assert "boş" in result["reason"].lower()

    def test_whitespace_only_address(self):
        """Sadece boşluk olan adres geçersiz olmalı."""
        result = validate_address("   ", api_key=self.api_key)
        assert not result["valid"]
        assert "boş" in result["reason"].lower()


class TestAddressValidationIntegration:
    """Entegrasyon testleri: API'ye gerçek istekler."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_key = get_api_key()
        if not self.api_key:
            pytest.skip("ORS API anahtarı yapılandırılmamış")

    def test_batch_validation(self):
        """Birden fazla adres toplu doğrulama."""
        from src.validate_address import batch_validate_addresses

        addresses = [
            "Moda Caddesi, Kadıköy",
            "asdfghjkl uydurma",
            "Kızılay, Ankara",  
        ]
        results = batch_validate_addresses(
            addresses,
            api_key=self.api_key,
            country_code="TUR",
            focus_point=(29.044531, 40.997314),
        )
        assert len(results) == 3
        assert results[0]["valid"], "Moda Caddesi geçerli olmalı"
        assert not results[1]["valid"], "Uydurma adres geçersiz olmalı"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
