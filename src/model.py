"""Modül 4-8 — OR-Tools model kurulumu (kısıtlar).

Kademeli olarak eklenecek kısıtlar:
  Modül 4: çift kapasite (kg + desi), çok araç
  Modül 5: heterojen filo + araç-paket uyumluluğu, max durak
  Modül 6: zaman pencereleri + servis süresi + mesai
  Modül 7: soft SLA cezaları (express/VIP) (THIS MODULE)
  Modül 8: toplama/iade (backhaul) yük mantığı

Bu aşamada (Modül 7): Modül 6'ya ek olarak soft time window (SLA/gecikme cezası) eklenmektedir:
  - Beklenen teslimat saatinden daha geç varırsa ceza pay oluşur
  - EXPRESS paketler: 10 TL/dakika gecikmeden sonra
  - STANDART paketler: 1 TL/dakika gecikmeden sonra
  - Soft constraint: zamanı ihlal etmek yasak değil, sadece pahalı
"""
import pandas as pd
from ortools.constraint_solver import pywrapcp


def _add_time_dimension(routing, manager, points: pd.DataFrame, dur_s: list, vehicles: pd.DataFrame) -> None:
    """Modül 6: Zaman boyutu ekleme + servis süresi + zaman pencereleri + vardiya sınırı.

    OR-Tools'ta 'time dimension', rota boyunca birikmiş zamanı izler. Her durak
    arası geçiş süresi = gerçek yol süresi (dur_s'den) + önceki durağın servis süresi.

    Neden böyle yapılıyor: Kargo 10:00'de müşteriye varır, 5 dakika hizmet verir.
    OR-Tools'a "10:00-10:05 arası servisiz, 10:05'ten sonra gidebilir" dememeliyiz.
    Bunun yerine transit callback'inde servis süresi başa eklenir, çözücü otomatik
    olarak "önceki durak süresi + yol süresi" hesaplar.
    """
    servis_dk = points["servis_suresi_dk"].fillna(0).tolist()

    def time_callback(from_index, to_index):
        """Bir duraktan diğerine geçiş süresi = yol süresi + kalkan duraktaki servis."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        travel_time_s = dur_s[from_node][to_node]
        travel_time_dk = travel_time_s / 60

        service_time_dk = servis_dk[from_node]

        return int(round(travel_time_dk + service_time_dk))

    time_cb_idx = routing.RegisterTransitCallback(time_callback)

    routing.AddDimension(
        time_cb_idx,
        slack_max=600,                   
        capacity=1600,                   
        fix_start_cumul_to_zero=False,   
        name="Zaman"
    )

    time_dim = routing.GetDimensionOrDie("Zaman")

    depo_acilis = points.iloc[0].get("zaman_baslangic")
    depo_acilis_dk = int(depo_acilis) if pd.notna(depo_acilis) else 480  

    for vehicle_idx in range(routing.vehicles()):
        start_index = routing.Start(vehicle_idx)
        time_dim.CumulVar(start_index).SetRange(depo_acilis_dk, depo_acilis_dk)
        max_time_dk = int(vehicles.iloc[vehicle_idx]["max_calisma_dk"])
        time_dim.SetSpanUpperBoundForVehicle(max_time_dk, vehicle_idx)

    _add_soft_time_windows(routing, manager, points, time_dim)


def _add_soft_time_windows(routing, manager, points: pd.DataFrame, time_dim) -> None:
    """Modül 7: Soft time windows (SLA/gecikme cezası).

    Beklenen teslimat saatinden geç varırsa, her dakika gecikmenden sonra
    ceza pay oluşur. Ceza miktarı kategoriye göre değişir:
      - EXPRESS: 10 TL/dakika gecikme (express hizmet yüksek ceza)
      - STANDART: 1 TL/dakika gecikme (normal hizmet düşük ceza)
      - Diğer kategoriler: ceza yok (AGIR_YUK, DEPO'da gecikme cezası yok)

    Zaman pencereleri (zaman_baslangic, zaman_bitis) CSV'den dakika cinsinden gelir:
      - 09:30 -> 570 dakika (gün başından)
      - 23:59 -> 1439 dakika
      - Boş -> NaN (hiç kısıt yok, ceza da yok)

    Soft constraint: eğer geç varırsa, hard constraint ihlali değil,
    sadece maliyete ceza eklenir. Çözücü bu maliyeti minimize ederken
    gecikmeyi minimuma indirir ama mümkün değilse kabul eder.

    OR-Tools: SetCumulVarSoftLowerBound / SetCumulVarSoftUpperBound kullanarak
    soft time windows uygularız.
    """
    penalty_per_min = {
        "EXPRESS": 500,     
        "STANDART": 50,     
        "AGIR_YUK": 50,     
        "DEPO": 0,          
    }

    for node_idx in range(1, len(points)):  
        point = points.iloc[node_idx]
        kategori = point.get("kategori", "STANDART")
        penalty_tl_per_min = penalty_per_min.get(kategori, 50)

        zaman_baslangic = point.get("zaman_baslangic")
        zaman_bitis = point.get("zaman_bitis")
        routing_index = manager.NodeToIndex(node_idx)

        if pd.notna(zaman_baslangic):
            time_dim.CumulVar(routing_index).SetMin(int(zaman_baslangic))

        if pd.notna(zaman_bitis) and penalty_tl_per_min > 0:
            time_dim.SetCumulVarSoftUpperBound(routing_index, int(zaman_bitis), int(penalty_tl_per_min))


def _add_fixed_costs(routing, vehicles: pd.DataFrame, objective: str = "distance", custom_weights: dict = None) -> None:
    """Her araç için sabit sefer maliyeti ekler (Modül 5).

    BUG FIX: Sabit maliyetin arc cost ile AYNI ölçekte olması lazım:
      - distance: mesafe (metre) — 5 km = 5000 metre araç açılış eşdeğeri
      - time: süre (saniye) — 5 dk = 300 saniye araç hazırlık eşdeğeri
      - cost: maliyet (kuruş) — sabit_maliyet * 100 (TL'den kuruşa)
      - custom: kullanıcı tanımlı ağırlıklı maliyet kombinasyonu
    """
    weights = custom_weights or {"cost": 50, "time": 40, "distance": 10}
    w_sum = max(1.0, float(weights.get("cost", 0) + weights.get("time", 0) + weights.get("distance", 0)))
    w_cost = float(weights.get("cost", 0)) / w_sum
    w_time = float(weights.get("time", 0)) / w_sum
    w_dist = float(weights.get("distance", 0)) / w_sum

    for vehicle_idx in range(routing.vehicles()):
        sabit = float(vehicles.iloc[vehicle_idx]["sabit_maliyet"])
        if objective == "cost":
            routing.SetFixedCostOfVehicle(int(round(sabit * 100)), vehicle_idx)
        elif objective == "distance":
            routing.SetFixedCostOfVehicle(5000, vehicle_idx)  
        elif objective == "time":
            routing.SetFixedCostOfVehicle(300, vehicle_idx)   
        elif objective == "custom":
            custom_fixed = (w_cost * (sabit * 100)) + (w_dist * 5000) + (w_time * 2400)
            routing.SetFixedCostOfVehicle(int(round(custom_fixed)), vehicle_idx)


def _add_vehicle_restrictions(routing, manager, points: pd.DataFrame, vehicles: pd.DataFrame) -> None:
    """Ağır/hacimli paketleri motokuryeye kapatır ve kapasite / kullanıcı araç tercihini uygular (Modül 5)."""
    # [İŞ_MANTIĞI]: Filodaki araçların tipleri ve kapasiteleri dinamik olarak alınır.
    # Sipariş bazında özel araç ataması (tercih_edilen_arac) yapılmışsa, routing arama uzayı (search space) 
    # kısıtlanarak o siparişin sadece ilgili araca atanması sağlanır.
    arac_tipleri = list(vehicles["arac_tipi"])
    arac_ids = [str(x).strip() for x in vehicles["arac_id"]]
    kapasite_desi = list(vehicles["kapasite_desi"])
    kapasite_kg = list(vehicles["kapasite_kg"])
    num_v = len(vehicles)

    for node_idx in range(1, len(points)):  
        p = points.iloc[node_idx]
        node_desi = float(p.get("desi", 0) or 0)
        node_kg = float(p.get("agirlik_kg", 0) or 0)
        kategori = str(p.get("kategori", ""))
        tercih_arac = str(p.get("atanan_arac", "") or p.get("tercih_edilen_arac", "") or p.get("arac_id", "")).strip()

        allowed = []
        for v in range(num_v):
            v_id = arac_ids[v]
            if tercih_arac and tercih_arac not in ("", "OTOMATIK", "-", "None", "nan", "Atanmadı"):
                if v_id != tercih_arac and arac_tipleri[v] != tercih_arac:
                    continue

            if kapasite_desi[v] < node_desi or kapasite_kg[v] < node_kg:
                continue  
            if kategori == "AGIR_YUK" and arac_tipleri[v] == "MOTO_KURYE":
                continue  
            allowed.append(v)

        if allowed and len(allowed) < num_v:
            vehicle_var = routing.VehicleVar(manager.NodeToIndex(node_idx))
            for v in range(num_v):
                if v not in allowed:
                    vehicle_var.RemoveValue(v)



def _add_backhaul_dimension(routing, manager, points: pd.DataFrame, vehicles: pd.DataFrame) -> None:
    """Modül 8: Toplama/iade (backhaul) yük yönetimi."""
    pass


def _add_stop_limit_dimension(routing, manager, vehicles: pd.DataFrame) -> None:
    """Her araç için maksimum durak sayısı dimension'ı ekler (Modül 5)."""
    stop_capacities = [int(c) for c in vehicles["max_durak_sayisi"]]

    def stop_callback(from_index):
        node = manager.IndexToNode(from_index)
        return 1 if node != 0 else 0

    stop_cb_idx = routing.RegisterUnaryTransitCallback(stop_callback)
    routing.AddDimensionWithVehicleCapacity(
        stop_cb_idx,
        0,                      
        stop_capacities,        
        True,                   
        "MaxDurak"
    )


def _add_capacity_dimension(routing, manager, demands: pd.Series, capacities: pd.Series, name: str) -> None:
    """Bir kapasite boyutu ekler (kg için bir kez, desi için bir kez çağrılacak)."""
    demands_int = [int(round(d)) for d in demands]
    capacities_int = [int(round(c)) for c in capacities]

    def demand_callback(from_index):
        node = manager.IndexToNode(from_index)
        return demands_int[node]

    demand_cb_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_cb_idx,
        0,                  
        capacities_int,     
        True,               
        name,
    )


def build_model(points: pd.DataFrame, vehicles: pd.DataFrame, dist_m: list, dur_s: list, objective: str = "distance", custom_weights: dict = None):
    """RoutingIndexManager + RoutingModel kurar; arc cost'u objective'e göre ayarlar.

    Parametreler:
      points: depo + tüm durağın koordinat/talep bilgileri (ilk satır depo)
      vehicles: araç filosu
      dist_m: mesafe matrisi (metre cinsinden)
      dur_s: süre matrisi (Modül 3'ten; saniye cinsinden)
      objective: "distance" | "time" | "cost" | "custom" — optimizasyon hedefi
      custom_weights: objective == "custom" için dict, ör: {"cost": 50, "time": 40, "distance": 10}
    """
    num_vehicles = len(vehicles)
    depot_index = 0

    # [MİMARİ_BİLGİ]: OR-Tools RoutingIndexManager, sipariş listesindeki (points)
    # her bir satırı bir 'node' (düğüm) olarak haritalandırır. Toplam araç sayısı ve
    # rotanın başlayıp biteceği depo konumu (0. indeks) burada modele entegre edilir.
    manager = pywrapcp.RoutingIndexManager(len(points), num_vehicles, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    # [TEKNİK_KARAR]: Optimizasyon hedefi (objective) arc cost (kenar maliyeti) yapısını belirler.
    # 'distance' seçiliyse model doğrudan mesafeyi minimize edecek şekilde kurulur.
    if objective == "distance":
        def arc_cost_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(round(dist_m[from_node][to_node]))

        arc_cost_cb_idx = routing.RegisterTransitCallback(arc_cost_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(arc_cost_cb_idx)

    elif objective == "time":
        def arc_cost_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time_s = dur_s[from_node][to_node]
            return int(round(travel_time_s))

        arc_cost_cb_idx = routing.RegisterTransitCallback(arc_cost_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(arc_cost_cb_idx)

    elif objective == "cost":
        km_maliyetleri = [float(x) for x in vehicles["km_maliyet"]]

        def _make_cost_cb(km_maliyet):
            def cb(from_index, to_index):
                fn = manager.IndexToNode(from_index)
                tn = manager.IndexToNode(to_index)
                distance_km = dist_m[fn][tn] / 1000.0
                return int(round(distance_km * km_maliyet * 100))  
            return cb

        for v in range(num_vehicles):
            cb_idx = routing.RegisterTransitCallback(_make_cost_cb(km_maliyetleri[v]))
            routing.SetArcCostEvaluatorOfVehicle(cb_idx, v)

    elif objective == "custom":
        weights = custom_weights or {"cost": 50, "time": 40, "distance": 10}
        w_sum = max(1.0, float(weights.get("cost", 0) + weights.get("time", 0) + weights.get("distance", 0)))
        w_cost = float(weights.get("cost", 0)) / w_sum
        w_time = float(weights.get("time", 0)) / w_sum
        w_dist = float(weights.get("distance", 0)) / w_sum

        km_maliyetleri = [float(x) for x in vehicles["km_maliyet"]]

        def _make_custom_cb(km_maliyet):
            def cb(from_index, to_index):
                fn = manager.IndexToNode(from_index)
                tn = manager.IndexToNode(to_index)
                d_m = dist_m[fn][tn]
                t_s = dur_s[fn][tn]
                d_km = d_m / 1000.0
                
                cost_part = (d_km * km_maliyet) * 120.0
                dist_part = d_m * 1.0
                time_part = t_s * 8.0

                total_score = (w_dist * dist_part) + (w_time * time_part) + (w_cost * cost_part)
                return int(round(total_score))
            return cb

        for v in range(num_vehicles):
            cb_idx = routing.RegisterTransitCallback(_make_custom_cb(km_maliyetleri[v]))
            routing.SetArcCostEvaluatorOfVehicle(cb_idx, v)

    from src.pickup import compute_adjusted_demands
    adjusted_kg, adjusted_desi = compute_adjusted_demands(points)

    _add_capacity_dimension(routing, manager, adjusted_kg, vehicles["kapasite_kg"], "Agirlik")
    _add_capacity_dimension(routing, manager, adjusted_desi, vehicles["kapasite_desi"], "Desi")

    _add_fixed_costs(routing, vehicles, objective, custom_weights)
    _add_vehicle_restrictions(routing, manager, points, vehicles)
    _add_stop_limit_dimension(routing, manager, vehicles)

    _add_time_dimension(routing, manager, points, dur_s, vehicles)

    _add_backhaul_dimension(routing, manager, points, vehicles)

    drop_penalty = 10_000_000
    for node_idx in range(1, len(points)):  
        routing.AddDisjunction([manager.NodeToIndex(node_idx)], drop_penalty)

    return routing, manager
