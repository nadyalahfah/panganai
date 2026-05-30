import re

file_path = 'frontend/src/pages/Prediksi.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Change initial state from hardcoded strings to empty strings
content = content.replace(
    "const [selKomoditas, setSelKomoditas] = useState('Beras Medium I')",
    "const [selKomoditas, setSelKomoditas] = useState('')"
)
content = content.replace(
    "const [selProvinsi, setSelProvinsi] = useState('DKI Jakarta')",
    "const [selProvinsi, setSelProvinsi] = useState('')"
)

# 2. Update loadFilters to map objects to strings and set default selection
replacement = """
    async function loadFilters() {
      try {
        const [komData, provData] = await Promise.all([fetchKomoditas(), fetchProvinsi()])
        const kom = komData.map(k => k.nama || k.slug || k).sort((a, b) => a.localeCompare(b));
        const prov = provData.map(p => p.nama || p.slug || p).sort((a, b) => a.localeCompare(b));
        setKomoditasList(kom)
        setProvinsiList(prov)
        
        const defaultKom = kom.length > 0 ? kom[0] : 'Beras Medium I';
        const defaultProv = prov.length > 0 ? prov[0] : 'DKI Jakarta';
        
        setSelKomoditas(defaultKom)
        setSelProvinsi(defaultProv)
        
        loadData(defaultKom, defaultProv)
        setInitialized(true)
      } catch (err) {
        setError(err.message)
      }
    }
"""
content = re.sub(
    r'    async function loadFilters\(\) \{[\s\S]*?\}\n',
    replacement.strip() + '\n',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Prediksi.jsx updated successfully.")
