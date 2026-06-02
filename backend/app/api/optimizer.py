import math
import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException

from app.services.catboost_prediction_service import get_all_province_predictions_legacy_contract
from app.services.dataset_service import resolve_komoditas_value

router = APIRouter()

def normalize_prov_name(name):
    if not isinstance(name, str):
        return ""
    return name.strip()

@router.get("/routes")
def get_optimizer_routes(request: Request):
    """
    Generate optimized distribution routes by pairing highest supply provinces
    with highest need destinations (Deficit + Forecast Risk) within each commodity.
    """
    ML_KOMODITAS_MAP = {
        "Bawang Merah Ukuran Sedang": "Bawang Merah Ukuran Sedang",
        "Beras Medium I": "Beras Kualitas Medium I",
        "Beras Medium II": "Beras Kualitas Medium II",
        "Beras Premium": "Beras Kualitas Super I",
        "Cabai Merah Besar": "Cabai Merah Besar",
        "Cabai Merah Keriting": "Cabai Merah Keriting",
        "Cabai Rawit": "Cabai Rawit Merah",
        "Minyak Goreng Curah": "Minyak Goreng Curah",
        "Telur Ayam Ras": "Telur Ayam Ras Segar"
    }

    try:
        df = pd.read_csv(r"d:\2026\pangan-ai\panganai\backend\data\master_supply_demand.csv")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Gagal memuat master_supply_demand.csv")

    try:
        # Sort by year so latest is last
        if 'tahun' in df.columns:
            df = df.sort_values(by='tahun')
        
        df_current = df.copy()

        physical_routes = []
        market_alerts = []
        supported_commodities = set()
        provinces_covered = set()
        chart_data = []

        commodities = df_current['komoditas'].unique()
        for kom in commodities:
            ml_komoditas = ML_KOMODITAS_MAP.get(kom, kom)
            komoditas_slug = resolve_komoditas_value(request.app.state.df_semua, ml_komoditas)
            if not komoditas_slug:
                continue

            subset_physical = df_current[(df_current['komoditas'] == kom) & (df_current['demand_ton'] > 0) & (df_current['supply_ton'] > 0)].copy()
            
            if not subset_physical.empty:
                subset = subset_physical.drop_duplicates(subset=['provinsi'], keep='last').copy()
            else:
                subset = df_current[df_current['komoditas'] == kom].copy()
                if subset.empty:
                    continue
                subset = subset.drop_duplicates(subset=['provinsi'], keep='last').copy()
            
            # Fill NaNs for safety
            subset['supply_ton'] = subset['supply_ton'].fillna(0)
            subset['demand_ton'] = subset['demand_ton'].fillna(0)
            subset['supply_index'] = subset['supply_index'].fillna(0)
            subset['demand_index'] = subset['demand_index'].fillna(0)

            # DATA GOVERNANCE RULE: Check if deficit can be calculated physically
            total_demand = subset['demand_ton'].sum()
            total_supply = subset['supply_ton'].sum()
            
            # Engine Selection: 
            # If we have both supply and demand data, we can calculate real deficit. -> Physical Redistribution Engine
            # Otherwise -> Forecast Risk Monitoring Engine
            is_physical_engine = total_demand > 0 and total_supply > 0
    
            # Calculate raw surplus and deficit
            subset['surplus_ton'] = subset.apply(lambda row: max(0, row['supply_ton'] - row['demand_ton']), axis=1)
            subset['deficit_ton'] = subset.apply(lambda row: max(0, row['demand_ton'] - row['supply_ton']), axis=1)
            
            # Populate chart data
            if is_physical_engine:
                top_surplus_provs = subset.sort_values(by='surplus_ton', ascending=False).head(5)
                top_deficit_provs = subset.sort_values(by='deficit_ton', ascending=False).head(5)
                
                for _, r in top_surplus_provs.iterrows():
                    if r['surplus_ton'] > 0:
                        chart_data.append({
                            "commodity": kom,
                            "provinsi": normalize_prov_name(r['provinsi']),
                            "type": "Surplus",
                            "tonnage": float(r['surplus_ton'])
                        })
                for _, r in top_deficit_provs.iterrows():
                    if r['deficit_ton'] > 0:
                        chart_data.append({
                            "commodity": kom,
                            "provinsi": normalize_prov_name(r['provinsi']),
                            "type": "Deficit",
                            "tonnage": float(r['deficit_ton'])
                        })
    
            # Calculate Deficit Index
            max_deficit = subset['deficit_ton'].max()
            if max_deficit > 0:
                subset['deficit_index'] = subset['deficit_ton'] / max_deficit
            else:
                subset['deficit_index'] = 0
    
            # Fetch forecasts
            try:
                preds = get_all_province_predictions_legacy_contract(request.app.state, komoditas_slug)
            except Exception:
                preds = []
                preds = []
                
            if not preds:
                continue
                
            preds_dict = {p['provinsi'].strip().lower(): p for p in preds}
    
            if is_physical_engine:
                # ==================================================
                # ENGINE 1: PHYSICAL REDISTRIBUTION
                # ==================================================
                sources = subset[subset['supply_index'] > 0].sort_values(by='supply_index', ascending=False)
                top_sources = sources.head(3)
                if top_sources.empty:
                    continue
    
                destinations = []
                for _, row in subset.iterrows():
                    prov = normalize_prov_name(row['provinsi'])
                    pred = preds_dict.get(prov.lower(), {})
                    forecast_change_pct = float(pred.get('ubah_7_pct', 0))
                    forecast_risk_index = min(max(forecast_change_pct, 0), 30) / 30.0
                    
                    # Deficit + Risk
                    need_score = (0.7 * row['deficit_index']) + (0.3 * forecast_risk_index)
                        
                    if need_score > 0 and row['deficit_ton'] > 0:
                        destinations.append({
                            'provinsi': prov,
                            'row': row,
                            'pred': pred,
                            'forecast_change_pct': forecast_change_pct,
                            'need_score': need_score
                        })
                        
                destinations = sorted(destinations, key=lambda x: x['need_score'], reverse=True)[:3]
                if not destinations:
                    continue
    
                routes_for_kom = []
                for _, src_row in top_sources.iterrows():
                    src_prov = normalize_prov_name(src_row['provinsi'])
                    supply_score = src_row['supply_index']
                    
                    for dest in destinations:
                        dest_prov = dest['provinsi']
                        if src_prov == dest_prov:
                            continue
                            
                        route_score = (0.6 * supply_score) + (0.4 * dest['need_score'])
                        
                        reason = f"Because the destination has a verified deficit ({int(dest['row']['deficit_ton']):,} Ton shortage) and a {dest['forecast_change_pct']:.1f}% projected price risk."
                        
                        routes_for_kom.append({
                            "commodity": kom,
                            "source_province": src_prov,
                            "destination_province": dest_prov,
                            "supply_ton": float(src_row['supply_ton']),
                            "demand_ton": float(dest['row']['demand_ton']),
                            "surplus_ton": float(src_row['surplus_ton']),
                            "deficit_ton": float(dest['row']['deficit_ton']),
                            "forecast_change_pct": float(dest['forecast_change_pct']),
                            "supply_score": float(supply_score),
                            "need_score": float(dest['need_score']),
                            "route_score": round(route_score * 100),
                            "reason": reason,
                            "current_price": dest['pred'].get('harga_sekarang', 0),
                            "forecast_price": dest['pred'].get('prediksi_7h', 0)
                        })
                
                routes_for_kom = sorted(routes_for_kom, key=lambda x: x['route_score'], reverse=True)[:5]
                if routes_for_kom:
                    supported_commodities.add(kom)
                    for r in routes_for_kom:
                        physical_routes.append(r)
                        provinces_covered.add(r['source_province'])
                        provinces_covered.add(r['destination_province'])
    
            else:
                # ==================================================
                # ENGINE 2: FORECAST RISK MONITORING
                # ==================================================
                alerts_for_kom = []
                for _, row in subset.iterrows():
                    prov = normalize_prov_name(row['provinsi'])
                    pred = preds_dict.get(prov.lower(), {})
                    forecast_change_pct = float(pred.get('ubah_7_pct', 0))
                    
                    if forecast_change_pct >= 5:
                        if forecast_change_pct >= 10:
                            risk_level = "High Risk Alert"
                        else:
                            risk_level = "Medium Risk Alert"
                            
                        reason = f"Because we do not possess verified demand data for this commodity, therefore we issue a risk alert instead of recommending shipments. Projected +{forecast_change_pct:.1f}% spike."
                        
                        alerts_for_kom.append({
                            "commodity": kom,
                            "province": prov,
                            "forecast_change_pct": forecast_change_pct,
                            "risk_level": risk_level,
                            "reason": reason,
                            "current_price": pred.get('harga_sekarang', 0),
                            "forecast_price": pred.get('prediksi_7h', 0)
                        })
                
                alerts_for_kom = sorted(alerts_for_kom, key=lambda x: x['forecast_change_pct'], reverse=True)[:5]
                if alerts_for_kom:
                    supported_commodities.add(kom)
                    for a in alerts_for_kom:
                        market_alerts.append(a)
    
        avg_route_score = 0
        if physical_routes:
            avg_route_score = round(sum(r['route_score'] for r in physical_routes) / len(physical_routes))
            
        kpi = {
            "total_routes": len(physical_routes),
            "total_alerts": len(market_alerts),
            "supported_commodities": len(supported_commodities),
            "provinces_covered": len(provinces_covered),
            "avg_route_score": avg_route_score
        }

        return {
            "kpi": kpi,
            "chart_data": chart_data,
            "items": sorted(physical_routes, key=lambda x: x['route_score'], reverse=True),
            "market_alerts": sorted(market_alerts, key=lambda x: x['forecast_change_pct'], reverse=True)
        }
    except Exception as e:
        return {"error": str(e)}
