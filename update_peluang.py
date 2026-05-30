import re

with open("frontend/src/pages/PeluangDistribusi.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# Add imports for AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
content = content.replace("import { Truck, Target, BarChart2, RouteIcon, ChevronUp, ChevronDown, ChevronsUpDown, Filter } from 'lucide-react'",
"import { Truck, Target, BarChart2, RouteIcon, ChevronUp, ChevronDown, ChevronsUpDown, Filter, Clock } from 'lucide-react'\nimport { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'")

# Add generateDemandData and DemandTooltip
add_code = """
// ── Demand Mock Data ──────────────────────────────────────────────────
const generateDemandData = (days) => {
  const data = []
  const baseDate = new Date('2026-03-15')
  for (let i = 0; i < days; i++) {
    const d = new Date(baseDate)
    d.setDate(d.getDate() + i)
    const demand = 2800 + Math.sin(i * 0.3) * 200 + Math.random() * 100
    const supply = 2600 + Math.cos(i * 0.25) * 180 + Math.random() * 80
    data.push({
      tanggal: d.toISOString().slice(0, 10),
      demand: Math.round(demand),
      supply: Math.round(supply),
      gap: Math.round(demand - supply),
    })
  }
  return data
}

function DemandTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const demand = payload.find(p => p.dataKey === 'demand')?.value
  const supply = payload.find(p => p.dataKey === 'supply')?.value
  const gap = demand && supply ? demand - supply : 0
  const pct = demand ? ((gap / demand) * 100).toFixed(1) : 0
  return (
    <div className="custom-tooltip">
      <div className="tooltip-date">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="tooltip-item">
          <span className="tooltip-dot" style={{ background: p.color }} />
          <span>{p.name}: {p.value.toLocaleString('id-ID')} Ton</span>
        </div>
      ))}
      <div className="tooltip-item" style={{ borderTop: '1px solid rgba(255,255,255,0.15)', marginTop: 6, paddingTop: 6 }}>
        <span>Gap: {gap > 0 ? '-' : '+'}{Math.abs(gap).toLocaleString('id-ID')} Ton ({pct}%)</span>
      </div>
    </div>
  )
}
"""

content = content.replace("const ROUTES_DATA =", add_code + "\nconst ROUTES_DATA =")

# State for period
content = content.replace("const [expandedRow, setExpandedRow] = useState(null)",
"const [expandedRow, setExpandedRow] = useState(null)\n  const [period, setPeriod] = useState('30')")

# Compute demand insights
compute_demand = """
  const demandData = useMemo(() => generateDemandData(parseInt(period)), [period])
  const totalDemand = demandData.reduce((s, d) => s + d.demand, 0)
  const totalSupply = demandData.reduce((s, d) => s + d.supply, 0)
  const avgGap = ((totalDemand - totalSupply) / totalDemand * 100).toFixed(1)
  const efisiensi = (totalSupply / totalDemand * 100).toFixed(1)
"""

content = content.replace("const sorted = useMemo(() => {", compute_demand + "\n  const sorted = useMemo(() => {")

# Modify rendering
header_old = """      <div className="page-header">
        <h2>Peluang Distribusi</h2>
        <p>Analisis rute distribusi dengan margin dan ROI tertinggi berdasarkan selisih harga antar provinsi</p>
      </div>

      {/* Summary Cards */}
      <div className="metrics-grid" style={{ marginBottom: 24 }}>"""

header_new = """      <div className="page-header">
        <h2>Supply & Distribution Optimizer</h2>
        <p>Supply-Demand Overview, Gap Analysis, dan Rekomendasi Rute Distribusi</p>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Supply-Demand Overview</h3>
      {/* Demand KPI Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 24 }}>
        {[
          { label: 'Total Demand', value: `${(totalDemand/1000).toFixed(1)}K Ton`, color: '#3B82F6' },
          { label: 'Total Supply', value: `${(totalSupply/1000).toFixed(1)}K Ton`, color: '#10B981' },
          { label: 'Gap Rata-rata', value: `${avgGap}%`, color: '#EF4444' },
          { label: 'Efisiensi', value: `${efisiensi}%`, color: '#F97316' },
        ].map((c, i) => (
          <div key={i} className="kpi-card fade-in">
            <div className="kpi-label">{c.label}</div>
            <div className="kpi-value font-mono" style={{ color: c.color, fontSize: 22 }}>{c.value}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>Periode {period} hari</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 18 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 5 }}>
          <Clock size={14} /> Filter Periode:
        </span>
        <div className="toggle-group">
          {['7', '14', '30'].map(p => (
            <button key={p} className={`toggle-btn-item${period === p ? ' active' : ''}`} onClick={() => setPeriod(p)}>
              {p} Hari
            </button>
          ))}
        </div>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Gap Analysis</h3>
      {/* Area Chart */}
      <div className="chart-card" style={{ marginBottom: 32 }}>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={demandData} margin={{ top: 10, right: 16, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="gDemand" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gSupply" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis dataKey="tanggal" tick={{ fontSize: 10, fill: '#9CA3AF' }} interval="preserveStartEnd" minTickGap={40} />
            <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickFormatter={v => `${v.toLocaleString('id-ID')}T`} width={60} />
            <Tooltip content={<DemandTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area type="monotone" dataKey="demand" name="Demand (Ton)" stroke="#3B82F6" strokeWidth={2.5} fill="url(#gDemand)" />
            <Area type="monotone" dataKey="supply" name="Supply (Ton)" stroke="#10B981" strokeWidth={2.5} fill="url(#gSupply)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Recommended Distribution Routes</h3>
      {/* Summary Cards */}
      <div className="metrics-grid" style={{ marginBottom: 24 }}>"""

content = content.replace(header_old, header_new)

with open("frontend/src/pages/PeluangDistribusi.jsx", "w", encoding="utf-8") as f:
    f.write(content)
