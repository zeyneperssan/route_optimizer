"""Flask Web Sunucusu ve Rota Optimizasyonu API'si."""
import sys
from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.service import service
from src.validate_address import validate_address
from src.config_loader import get_api_key

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

@app.route('/')
def index():
    """Dashboard HTML sayfasını sun."""
    dashboard_path = BASE_DIR / 'dashboard.html'
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/data', methods=['GET'])
def get_data():
    """Canlı optimizasyon ve rota verilerini döner."""
    scenario = request.args.get('scenario')
    try:
        data = service.get_dashboard_data(scenario=scenario)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scenario', methods=['POST'])
def set_scenario():
    """Aktif senaryoyu değiştirir (distance / time / cost / custom)."""
    body = request.get_json() or {}
    scenario = body.get('scenario', 'distance')
    weights = body.get('weights')
    try:
        if scenario == 'custom' and weights:
            data = service.compute_custom_scenario(weights)
        else:
            data = service.get_dashboard_data(scenario=scenario)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scenario/custom', methods=['POST'])
def set_custom_scenario():
    """Kullanıcı tanımlı ağırlıklarla (cost, time, distance) optimizasyonu çözer."""
    body = request.get_json() or {}
    weights = body.get('weights', {})
    try:
        data = service.compute_custom_scenario(weights)
        return jsonify({"success": True, "message": "Özel senaryo başarıyla hesaplandı!", "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def add_order():
    """Yeni bir sipariş ekler ve optimizasyonu canlı olarak tetikler."""
    order_data = request.get_json()
    if not order_data:
        return jsonify({"success": False, "error": "Geçersiz sipariş verisi"}), 400
    try:
        data = service.add_order(order_data)
        return jsonify({"success": True, "message": "Sipariş eklendi ve rota yeniden optimize edildi!", "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
def reoptimize():
    """Tüm pipeline'ı sıfırdan yeniden çalıştırır."""
    try:
        service.run_full_pipeline(force_geocode=False)
        data = service.get_dashboard_data()
        return jsonify({"success": True, "message": "Optimizasyon başarıyla tamamlandı!", "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/orders/delete', methods=['POST'])
def delete_order():
    """Bir siparişi listeden kaldırır."""
    body = request.get_json() or {}
    try:
        return jsonify({"success": True, "data": service.delete_order(body.get('kargo_takip_no'))})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/orders/clear_unserved', methods=['POST'])
def clear_unserved():
    """Servis edilemeyen tüm siparişleri listeden kaldırır."""
    try:
        return jsonify({"success": True, "data": service.delete_unserved()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    """Adres yazarken ORS'den otomatik tamamlama önerileri döner."""
    q = request.args.get('q', '')
    try:
        return jsonify({"success": True, "suggestions": service.address_autocomplete(q)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "suggestions": []})

@app.route('/api/validate-address', methods=['POST'])
def validate_addr():
    """Adresi coğrafi bilgi sistemleri ile doğrular (real-time modal doğrulama)."""
    body = request.get_json() or {}
    address = body.get('address', '').strip()

    if not address:
        return jsonify({
            "success": False,
            "valid": False,
            "reason": "Adres boş bırakılamaz",
            "lat": None,
            "lon": None,
        }), 400

    try:
        api_key = get_api_key()
        if not api_key:
            return jsonify({
                "success": False,
                "valid": False,
                "reason": "API anahtarı yapılandırılmamış",
                "lat": None,
                "lon": None,
            }), 500

        result = validate_address(
            address,
            api_key=api_key,
            country_code="TUR",
            focus_point=(29.044531, 40.997314),  
        )

        return jsonify({
            "success": True,
            "valid": result["valid"],
            "reason": result["reason"],
            "lat": result["lat"],
            "lon": result["lon"],
            "location_name": result["location_name"],
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "valid": False,
            "reason": f"Doğrulama hatası: {str(e)}",
            "lat": None,
            "lon": None,
        }), 500

@app.route('/cache/<path:filename>')
def serve_cache(filename):
    """Cache klasöründeki interaktif haritaları ve dosyaları sun."""
    return send_from_directory(BASE_DIR / 'cache', filename)

if __name__ == '__main__':
    print("[INFO] Route Optimizer Canli Dashboard baslatiliyor: http://127.0.0.1:5000")
    try:
        service.run_full_pipeline()
    except Exception as e:
        print(f"[UYARI] Baslangic optimizasyonu: {e}")
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
