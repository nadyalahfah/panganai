import urllib.request
import json
import pandas as pd

print('==================================================')
print('STEP 1 — TRACE ONE ROUTE')
print('==================================================')
req = urllib.request.urlopen('http://localhost:8000/api/optimizer/routes')
data = json.loads(req.read())
routes = data['items']

target_route = None
for r in routes:
    if r['source_province'] == 'Jawa Barat' and r['destination_province'] == 'Sulawesi Selatan':
        target_route = r
        break
if not target_route:
    target_route = routes[0]

print(f"commodity: {target_route['commodity']}")
print(f"source_province: {target_route['source_province']}")
print(f"destination_province: {target_route['destination_province']}")
print(f"route_score: {target_route['route_score']}")
print(f"surplus_ton: {target_route.get('surplus_ton', 0):.2f}")
print(f"deficit_ton: {target_route.get('deficit_ton', 0):.2f}")
print(f"forecast_change_pct: {target_route.get('forecast_change_pct', 0):.2f}")
print(f"need_score: {target_route.get('need_score', 0):.4f}")
print(f"supply_score: {target_route.get('supply_score', 0):.4f}")

print('\n==================================================')
print('STEP 2 — TRACE TO CSV')
print('==================================================')
df = pd.read_csv(r'd:\2026\pangan-ai\panganai\backend\data\master_supply_demand.csv')
kom = target_route['commodity']
df_kom = df[(df['komoditas'] == kom) & (df['tahun'] == 2025)].copy()
if df_kom.empty:
    df_kom = df[(df['komoditas'] == kom) & (df['tahun'] == 2024)].copy()

src_prov = target_route['source_province']
dest_prov = target_route['destination_province']

src_row = df_kom[df_kom['provinsi'] == src_prov].iloc[-1]
dest_row = df_kom[df_kom['provinsi'] == dest_prov].iloc[-1]

print('SOURCE PROVINCE:')
print(f"province: {src_row['provinsi']}")
print(f"commodity: {src_row['komoditas']}")
print(f"supply_ton: {src_row['supply_ton']:.2f}")
print(f"demand_ton: {src_row['demand_ton']:.2f}")
print(f"optimizer_mode: {src_row['optimizer_mode']}")

print('\nDESTINATION PROVINCE:')
print(f"province: {dest_row['provinsi']}")
print(f"commodity: {dest_row['komoditas']}")
print(f"supply_ton: {dest_row['supply_ton']:.2f}")
print(f"demand_ton: {dest_row['demand_ton']:.2f}")
print(f"optimizer_mode: {dest_row['optimizer_mode']}")

print('\n==================================================')
print('STEP 3 — DEFICIT VALIDATION')
print('==================================================')
calc_deficit = max(0, dest_row['demand_ton'] - dest_row['supply_ton'])
print(f"CSV values: demand_ton={dest_row['demand_ton']}, supply_ton={dest_row['supply_ton']}")
print(f"Formula: MAX(0, {dest_row['demand_ton']} - {dest_row['supply_ton']})")
print(f"Result: {calc_deficit}")
print(f"Is deficit_ton > 0? {'YES' if calc_deficit > 0 else 'NO, deficit_ton = 0'}")

print('\n==================================================')
print('STEP 4 — NEED SCORE TRACE')
print('==================================================')
df_kom['demand_ton'] = df_kom['demand_ton'].fillna(0)
df_kom['supply_ton'] = df_kom['supply_ton'].fillna(0)
df_kom['deficit_ton'] = df_kom.apply(lambda r: max(0, r['demand_ton'] - r['supply_ton']), axis=1)
max_def = df_kom['deficit_ton'].max()
if max_def > 0:
    def_idx = calc_deficit / max_def
else:
    def_idx = dest_row['demand_index']

f_pct = target_route.get('forecast_change_pct', 0)
f_risk = min(max(f_pct, 0), 30) / 30.0
ns = (0.7 * def_idx) + (0.3 * f_risk)

print(f"raw values: deficit_ton={calc_deficit}, max_deficit={max_def}, forecast_change_pct={f_pct}")
print(f"normalization: Deficit Index = {def_idx:.4f}, Forecast Risk Index = {f_risk:.4f}")
print("weights: Deficit (0.7), Forecast Risk (0.3)")
print("Need Score =")
print(f"({def_idx:.4f} * 0.7) + ({f_risk:.4f} * 0.3) = {ns:.4f}")

print('\n==================================================')
print('STEP 5 — DESTINATION RANKING AUDIT')
print('==================================================')
try:
    req2 = urllib.request.urlopen('http://localhost:8000/api/prediction/compare?komoditas_slug=cabai-merah-keriting')
    preds = json.loads(req2.read())['predictions']
    preds_dict = {p['provinsi'].strip().lower(): p for p in preds}
except Exception as e:
    print("Could not fetch prediction from local API, using dummy dict")
    preds_dict = {}

cands = []
for _, r in df_kom.iterrows():
    p = r['provinsi'].strip()
    pr = preds_dict.get(p.lower(), {})
    fp = float(pr.get('ubah_7_pct', 0))
    dt = max(0, r['demand_ton'] - r['supply_ton'])
    di = dt / max_def if max_def > 0 else r['demand_index']
    fri = min(max(fp, 0), 30) / 30.0
    nscore = (0.7 * di) + (0.3 * fri)
    cands.append({'prov': p, 'def': dt, 'fpct': fp, 'ns': nscore})

cands = sorted(cands, key=lambda x: x['ns'], reverse=True)[:10]
for i, c in enumerate(cands):
    print(f"{i+1}. province: {c['prov']}, deficit_ton: {c['def']:.2f}, forecast_change_pct: {c['fpct']:.2f}, need_score: {c['ns']:.4f}")

print('\n==================================================')
print('STEP 6 — INVESTIGATE DEFICIT=0 ROUTES')
print('==================================================')
def0 = [r for r in routes if r.get('deficit_ton', 0) <= 0]
print(f"Found {len(def0)} routes where deficit_ton <= 0")
print(f"{'Source':<20} | {'Destination':<20} | {'Commodity':<20} | {'Deficit':<10} | {'NeedScore':<10} | {'RouteScore'}")
for r in def0:
    print(f"{r['source_province'][:19]:<20} | {r['destination_province'][:19]:<20} | {r['commodity'][:19]:<20} | {r.get('deficit_ton',0):<10.2f} | {r.get('need_score',0):<10.4f} | {r.get('route_score',0)}")
