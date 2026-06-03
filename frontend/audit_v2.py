import requests
import json
import collections

# Mirror the getSmartReasoning logic from DistributionOptimizer.jsx
def get_smart_reasoning(commodity, province, forecast_pct, risk_level):
    c = (commodity or '').lower()
    p = province or ''
    pct = round(forecast_pct, 1) if forecast_pct else 0
    
    if risk_level == 'High Risk Alert' or risk_level == 'Intervensi Segera':
        if 'cabai' in c or 'merah' in c or 'rawit' in c:
            return f"Prediksi kenaikan harga {commodity} di {p} mencapai {pct}%.\n\nPrioritas tindakan:\n• Verifikasi stok distributor utama\n• Koordinasi pasokan antar wilayah\n• Monitoring sentra produksi terdekat"
        elif 'beras' in c:
            return f"Potensi tekanan harga {commodity} di {p} mencapai {pct}%.\n\nPrioritas tindakan:\n• Evaluasi stok Bulog\n• Pertimbangkan operasi pasar\n• Monitoring distribusi antar wilayah"
        elif 'telur' in c or 'ayam' in c:
            return f"Potensi kenaikan harga {commodity} di {p} mencapai {pct}%.\n\nPrioritas tindakan:\n• Monitoring pasokan peternak\n• Evaluasi distribusi regional\n• Penguatan koordinasi rantai pasok"
        else:
            return f"Prediksi kenaikan harga mencapai {pct}%. Intervensi segera direkomendasikan."
            
    elif risk_level == 'Medium Risk Alert' or risk_level == 'Monitoring Prioritas':
        if 'cabai' in c or 'merah' in c or 'rawit' in c:
            return f"Sinyal tekanan harga mulai muncul pada {commodity} di {p}.\n\nDisarankan pemantauan distribusi dan evaluasi pasokan."
        elif 'beras' in c:
            return f"Terindikasi peningkatan tekanan harga.\n\nEvaluasi ketersediaan stok dan distribusi direkomendasikan."
        elif 'telur' in c or 'ayam' in c:
            return f"Tekanan harga mulai terdeteksi.\n\nPemantauan distribusi dan stok direkomendasikan."
        else:
            return f"Sinyal tekanan harga mulai muncul.\nPemantauan distribusi dan evaluasi stok direkomendasikan."
            
    else:
        if 'beras' in c: return "Kondisi pasokan dan harga relatif stabil."
        if 'telur' in c or 'ayam' in c: return "Kondisi pasar relatif terkendali."
        return "Kondisi pasar relatif stabil.\nPemantauan berkala tetap direkomendasikan."

try:
    res = requests.get('http://localhost:8000/api/optimizer/routes')
    data = res.json()
    alerts = data.get('market_alerts', [])
    
    print(f"Total Alerts Fetched: {len(alerts)}")
    
    unique_texts = set()
    cards = []
    
    for a in alerts:
        commodity = a.get('commodity', '')
        province = a.get('province', '')
        risk_level = a.get('risk_level', '')
        pct = a.get('forecast_change_pct', 0)
        price = a.get('current_price', 0)
        
        display_level = 'Intervensi Segera' if risk_level == 'High Risk Alert' else 'Monitoring Prioritas'
        
        text = get_smart_reasoning(commodity, province, pct, display_level)
        unique_texts.add(text)
        
        cards.append({
            'commodity': commodity,
            'province': province,
            'risk': risk_level,
            'pct': pct,
            'text': text
        })
        
    print(f"Total Unique Texts: {len(unique_texts)}")
    print(f"Duplication Percentage: {((len(alerts) - len(unique_texts)) / len(alerts) * 100) if alerts else 0:.1f}%")
    
    print("\nSAMPLE CARDS:")
    for c in cards[:5]:
        print(f"[{c['commodity']}] {c['province']} | {c['risk']} | {c['pct']:.1f}% -> {c['text'][:50]}...")
        
except Exception as e:
    print(f"Error: {e}")
