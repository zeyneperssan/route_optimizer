"""Modül 4/9 — Çözüm: arama stratejisi, zaman limiti ve okunabilir rota çıktısı.

Modül 4'te sadece "geçerli bir çözüm bulmak" için gereken temel arama
ayarları (first_solution_strategy + local_search_metaheuristic + time_limit)
kullanılıyor; öncelik/ceza gibi ince ayarlar Modül 7 ve maliyet hedefi
(distance/time/cost seçimi) Modül 9'da eklenecek.
"""
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def solve(routing, manager, config: dict, objective: str = "distance"):
    """Modeli, objective'e göre optimized arama stratejisiyle çözer.

    Modül 9: Hedefe göre farklı metaheuristic stratejileri seçer:
      - distance: GUIDED_LOCAL_SEARCH (hızlı, rutin optimizasyon)
      - time: SIMULATED_ANNEALING (orta, zaman kısıtlarıyla)
      - cost: TABU_SEARCH (derinlemesine maliyet araştırması)
    """
    solver_cfg = config["solver"]

    # [MİMARİ_BİLGİ]: Default parametrelerle başlanır. 'first_solution_strategy' başlangıç
    # çözümünü bulmak için heuristics (örn. PATH_CHEAPEST_ARC) kullanırken, 
    # 'local_search_metaheuristic' bulunan başlangıç çözümünü iyileştirmeye çalışır.
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = getattr(
        routing_enums_pb2.FirstSolutionStrategy, solver_cfg["first_solution_strategy"]
    )

    if objective == "cost":
        strategy = "TABU_SEARCH"          
    else:  
        strategy = "GUIDED_LOCAL_SEARCH"  

    params.local_search_metaheuristic = getattr(
        routing_enums_pb2.LocalSearchMetaheuristic, strategy
    )
    params.time_limit.FromSeconds(int(solver_cfg["time_limit_seconds"]))

    solution = routing.SolveWithParameters(params)
    if solution is None:
        raise RuntimeError(
            "Çözüm bulunamadı — toplam talep filo kapasitesini aşıyor olabilir "
            "ya da tek bir paket tek bir aracın kapasitesinden büyük olabilir."
        )
    return solution


def extract_routes(routing, manager, solution, points, vehicles, dist_m=None, dur_s=None) -> list[dict]:
    """OR-Tools çözümünü okunabilir rota listesine çevirir.

    # [TEKNİK_DETAY]: OR-Tools'un `solution.Value(routing.NextVar(index))` fonksiyonu, 
    # ağacın bir sonraki dalını vererek rotayı adım adım gezmemizi (traverse) sağlar.
    
    ÖNEMLİ (Fix): mesafe ve süre, objective'e göre değişen arc cost'tan DEĞİL,
    her zaman gerçek mesafe (dist_m, metre) ve süre (dur_s, saniye) matrislerinden
    hesaplanır. Böylece 'time'/'cost' senaryolarında da 'mesafe_km' gerçek km olur.
    (Önceden GetArcCostForVehicle kullanılıyordu; time senaryosunda 'km' aslında
    saniye/1000 çıkıyordu — yanlıştı.)

    Her rota: arac_id, duraklar, mesafe_km, sure_dk ve (zaman boyutu varsa)
    durak_zamanlar_dk (gün başından mutlak dakika = gerçek saat).
    """
    rotalar = []
    time_dim = routing.GetDimensionOrDie("Zaman") if "Zaman" in routing.GetAllDimensionNames() else None

    for arac_no in range(routing.vehicles()):
        index = routing.Start(arac_no)
        duraklar = []
        node_sirasi = []
        durak_zamanlar = []

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            node_sirasi.append(node)
            duraklar.append(points.iloc[node]["kargo_takip_no"])
            if time_dim:
                durak_zamanlar.append(solution.Value(time_dim.CumulVar(index)))
            index = solution.Value(routing.NextVar(index))

        son_node = manager.IndexToNode(index)
        node_sirasi.append(son_node)
        duraklar.append(points.iloc[son_node]["kargo_takip_no"])  
        if time_dim:
            durak_zamanlar.append(solution.Value(time_dim.CumulVar(index)))

        toplam_mesafe_m = 0.0
        toplam_sure_s = 0.0
        bacak_mesafeler_km = []
        for a, b in zip(node_sirasi[:-1], node_sirasi[1:]):
            seg_m = dist_m[a][b] if dist_m is not None else 0.0
            seg_s = dur_s[a][b] if dur_s is not None else 0.0
            toplam_mesafe_m += seg_m
            toplam_sure_s += seg_s
            bacak_mesafeler_km.append(round(seg_m / 1000.0, 2))

        if len(duraklar) > 2:  
            donus_mesafe_m = dist_m[node_sirasi[-2]][node_sirasi[-1]] if dist_m is not None and len(node_sirasi) >= 2 else 0.0
            gidis_mesafe_m = max(0.0, toplam_mesafe_m - donus_mesafe_m)

            donus_sure_s = dur_s[node_sirasi[-2]][node_sirasi[-1]] if dur_s is not None and len(node_sirasi) >= 2 else 0.0
            gidis_sure_s = max(0.0, toplam_sure_s - donus_sure_s)

            toplam_servis_dk = sum(float(points.iloc[idx].get("servis_suresi_dk", 5)) for idx in node_sirasi[1:-1])

            gidis_sure_dk = round((gidis_sure_s / 60.0) + toplam_servis_dk, 1)
            donus_sure_dk = round(donus_sure_s / 60.0, 1)
            toplam_sure_dk = round(gidis_sure_dk + donus_sure_dk, 1)

            rota = {
                "arac_id": vehicles.iloc[arac_no]["arac_id"],
                "duraklar": duraklar,
                "node_sirasi": node_sirasi,
                "mesafe_km": round(toplam_mesafe_m / 1000.0, 2),
                "gidis_km": round(gidis_mesafe_m / 1000.0, 2),
                "donus_km": round(donus_mesafe_m / 1000.0, 2),
                "bacak_mesafeler_km": bacak_mesafeler_km,
                "sure_dk": toplam_sure_dk,
                "gidis_sure_dk": gidis_sure_dk,
                "donus_sure_dk": donus_sure_dk,
            }
            if time_dim:
                rota["durak_zamanlar_dk"] = durak_zamanlar
            rotalar.append(rota)

    return rotalar
