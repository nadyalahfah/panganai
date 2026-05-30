import os
import re

file_path = 'frontend/src/pages/Dashboard.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace KOMODITAS_LIST array
content = re.sub(
    r'const KOMODITAS_LIST = \[\s*"Beras Medium I",\s*"Minyak Goreng Curah",\s*"Cabai Merah Keriting",\s*\];\n',
    '',
    content
)

# 2. Add fetchKomoditas to imports
content = content.replace(
    '  fetchPrediksiSemua,\n  fetchPrediksi,\n  formatRupiah,',
    '  fetchPrediksiSemua,\n  fetchPrediksi,\n  fetchKomoditas,\n  formatRupiah,'
)

# 3. Add komoditasList state
content = content.replace(
    '  const [alerts, setAlerts] = useState([]);',
    '  const [komoditasList, setKomoditasList] = useState([]);\n  const [alerts, setAlerts] = useState([]);'
)

# 4. Update default selKomoditas
content = content.replace(
    '  const [selKomoditas, setSelKomoditas] = useState(KOMODITAS_LIST[0]);',
    '  const [selKomoditas, setSelKomoditas] = useState("");'
)

# 5. Fetch komoditas in Promise.all
content = content.replace(
    '          fetchAlert(),\n          fetchStatistikNasional(),\n          fetchProvinsi(),\n        ]);',
    '          fetchAlert(),\n          fetchStatistikNasional(),\n          fetchProvinsi(),\n          fetchKomoditas(),\n        ]);'
)

content = content.replace(
    '        const [alertData, statsData, provData] = await Promise.all([',
    '        const [alertData, statsData, provData, komoditasData] = await Promise.all(['
)

# 6. Handle fetched komoditas
replacement = """
        setAlerts(alertData);
        onAlertsLoaded?.(alertData.filter((a) => a.kenaikan_pct > 10));
        setStats(statsData);
        setProvinsiList(provData);

        const fetchedKom = komoditasData.map(k => k.nama || k.slug || k).sort((a, b) => a.localeCompare(b));
        setKomoditasList(fetchedKom);
        if (fetchedKom.length > 0) {
          setSelKomoditas(prev => fetchedKom.includes(prev) ? prev : fetchedKom[0]);
        }
"""
content = content.replace(
    """        setAlerts(alertData);
        onAlertsLoaded?.(alertData.filter((a) => a.kenaikan_pct > 10));
        setStats(statsData);
        setProvinsiList(provData);""",
    replacement.strip()
)

# 7. Update chartPromises loop
content = content.replace(
    '        const chartPromises = KOMODITAS_LIST.map(async (komoditas) => {',
    '        const chartPromises = fetchedKom.map(async (komoditas) => {'
)

# 8. Remove HET_MOCK entirely
content = re.sub(
    r'const HET_MOCK = \{.*?\};\n\n',
    '',
    content,
    flags=re.DOTALL
)

# 9. Update references to KOMODITAS_LIST.length
content = content.replace(
    'value={KOMODITAS_LIST.length}',
    'value={komoditasList.length}'
)

# 10. Update mapping for select
content = content.replace(
    '{KOMODITAS_LIST.map((k) => (',
    '{komoditasList.map((k) => ('
)

# 11. Remove HET prop usage
content = content.replace(
    'het={HET_MOCK[selKomoditas]}',
    'het={null}'
)

# 12. Update DistributionOptimizer props
content = content.replace(
    'komoditasList={KOMODITAS_LIST}',
    'komoditasList={komoditasList}'
)

# 13. Add badge to header
content = content.replace(
    '<h2>PanganAI Executive Command Center</h2>',
    '<div style={{display: "flex", alignItems: "center", gap: 12}}><h2>PanganAI Executive Command Center</h2>{komoditasList.length > 0 && <span style={{background: "#E2E8F0", padding: "4px 10px", borderRadius: 20, fontSize: 12, fontWeight: 600, color: "#475569"}}>{komoditasList.length} Komoditas Aktif</span>}</div>'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard.jsx updated successfully.")
