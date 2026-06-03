import urllib.request
import json
from collections import defaultdict

url = "http://localhost:8000/api/optimizer/routes"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())

routes = data.get('items', [])
print(f"Total Routes (Raw): {len(routes)}")

unique_pairs = set()
commodity_counts = defaultdict(int)

for r in routes:
    src = r.get('source_province') or r.get('provinsi_asal') or r.get('asal')
    dst = r.get('destination_province') or r.get('provinsi_tujuan') or r.get('tujuan')
    c = r.get('commodity')
    pair = f"{src} -> {dst}"
    unique_pairs.add(pair)
    commodity_counts[c] += 1

print("\nUnique Routes:")
for p in unique_pairs:
    print(f"- {p}")

print("\nPer Commodity:")
for c, count in commodity_counts.items():
    print(f"- {c}: {count} route")
