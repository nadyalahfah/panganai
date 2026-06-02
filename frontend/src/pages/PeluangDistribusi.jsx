import React, { useState, useEffect, useMemo } from 'react'
import { Truck, Target, BarChart2, ChevronUp, ChevronDown, ChevronsUpDown, Package, Map } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import DistributionOptimizer from '../components/DistributionOptimizer'

const STATUS_CONFIG = {
  open:     { badge: '✅ Terbuka', color: '#16A34A', bg: 'rgba(34,197,94,0.1)' },
  moderate: { badge: '⚠️ Moderate', color: '#B45309', bg: 'rgba(234,179,8,0.12)' },
  closed:   { badge: '❌ Tertutup', color: '#DC2626', bg: 'rgba(239,68,68,0.1)' },
}

const RISK_CONFIG = {
  LOW: { label: '🟢 Low', color: '#16A34A' },
  MED: { label: '🟡 Medium', color: '#B45309' },
  HIGH: { label: '🔴 High', color: '#DC2626' },
}

export default function PeluangDistribusi() {
  const [sortKey, setSortKey] = useState('route_score')
  const [sortDir, setSortDir] = useState('desc')
  const [filterKomoditas, setFilterKomoditas] = useState('Semua')
  const [expandedRow, setExpandedRow] = useState(null)
  
  const [routesData, setRoutesData] = useState([])
  const [alertsData, setAlertsData] = useState([])
  const [kpiData, setKpiData] = useState({ total_routes: 0, total_alerts: 0, supported_commodities: 0, provinces_covered: 0, avg_route_score: 0 })
  const [chartDataRaw, setChartDataRaw] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:8000/api/optimizer/routes')
      .then(res => res.json())
      .then(data => {
        setKpiData(data.kpi || { total_routes: 0, total_alerts: 0, supported_commodities: 0, provinces_covered: 0, avg_route_score: 0 })
        setChartDataRaw(data.chart_data || [])
        
        // Map backend output to frontend expected format
        const mappedRoutes = (data.items || []).map((r, i) => ({
          rank: i + 1,
          asal: r.source_province,
          tujuan: r.destination_province,
          provinsi_asal: r.source_province,
          provinsi_tujuan: r.destination_province,
          komoditas: r.commodity,
          route_score: r.route_score,
          frekuensi: '1-3x/minggu',
          kapasitas: 8,
          status: r.route_score >= 50 ? 'open' : 'moderate',
          risk: r.forecast_change_pct > 15 ? 'HIGH' : (r.forecast_change_pct > 5 ? 'MED' : 'LOW'),
          detail: `${r.reason}`,
          surplus_ton: r.surplus_ton,
          deficit_ton: r.deficit_ton,
          forecast_change_pct: r.forecast_change_pct,
          forecast_price: r.forecast_price
        }))
        setRoutesData(mappedRoutes)
        setAlertsData(data.market_alerts || [])
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  const komoditasOptions = ['Semua', ...new Set([...routesData.map(r => r.komoditas), ...alertsData.map(a => a.commodity)])]
  
  const chartData = useMemo(() => {
    const filtered = filterKomoditas === 'Semua' 
      ? chartDataRaw 
      : chartDataRaw.filter(d => d.commodity === filterKomoditas);
      
    const grouped = {};
    filtered.forEach(d => {
      if (!grouped[d.provinsi]) grouped[d.provinsi] = { provinsi: d.provinsi, Surplus: 0, Deficit: 0 };
      grouped[d.provinsi][d.type] += d.tonnage;
    });
    
    return Object.values(grouped).sort((a,b) => (b.Surplus + b.Deficit) - (a.Surplus + a.Deficit)).slice(0, 10);
  }, [chartDataRaw, filterKomoditas])

  const sorted = useMemo(() => {
    return [...routesData]
      .filter(r => filterKomoditas === 'Semua' || r.komoditas === filterKomoditas)
      .sort((a, b) => {
        const va = a[sortKey], vb = b[sortKey]
        if (va < vb) return sortDir === 'asc' ? -1 : 1
        if (va > vb) return sortDir === 'asc' ? 1 : -1
        return 0
      })
  }, [routesData, sortKey, sortDir, filterKomoditas])

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('desc') }
  }

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <ChevronsUpDown size={11} style={{ opacity: 0.4 }} />
    return sortDir === 'asc' ? <ChevronUp size={11} /> : <ChevronDown size={11} />
  }

  return (
    <div>
      <div className="page-header">
        <h2>Supply & Distribution Optimizer</h2>
        <p>Supply-Demand Overview, Gap Analysis, dan Rekomendasi Rute Distribusi (Forecast-Aware)</p>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Optimizer Performance Metrics</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 14, marginBottom: 24 }}>
        {[
          { label: 'Physical Routes', value: kpiData.total_routes, color: '#3B82F6', icon: Truck },
          { label: 'Market Alerts', value: kpiData.total_alerts, color: '#DC2626', icon: Target },
          { label: 'Supported Commodities', value: kpiData.supported_commodities, color: '#10B981', icon: Package },
          { label: 'Provinces Covered', value: kpiData.provinces_covered, color: '#F97316', icon: Map },
          { label: 'Avg Route Score', value: kpiData.avg_route_score, color: '#8B5CF6', icon: BarChart2 },
        ].map((c, i) => (
          <div key={i} className="kpi-card fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: 16, background: 'white', borderRadius: 12, border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ background: `${c.color}15`, padding: 6, borderRadius: 8, color: c.color }}>
                <c.icon size={18} />
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>{c.label}</div>
            </div>
            <div style={{ fontSize: 28, fontWeight: 800, color: '#0F172A', fontFamily: 'monospace' }}>{c.value}</div>
          </div>
        ))}
      </div>

      <div className="filter-bar">
        <select className="filter-select" value={filterKomoditas} onChange={e => setFilterKomoditas(e.target.value)} style={{ minWidth: 200 }}>
          {komoditasOptions.map(k => <option key={k} value={k}>{k}</option>)}
        </select>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{sorted.length} rute ditemukan</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 24, marginBottom: 32 }}>
        <div>
          <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Top Surplus vs Deficit Provinces</h3>
          <div className="chart-card" style={{ padding: 20 }}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
                <XAxis dataKey="provinsi" tick={{ fontSize: 10, fill: '#64748B' }} angle={-25} textAnchor="end" />
                <YAxis tickFormatter={v => `${(v/1000)}k`} tick={{ fontSize: 10, fill: '#64748B' }} />
                <Tooltip cursor={{ fill: '#F1F5F9' }} formatter={(value) => `${value.toLocaleString('id-ID')} Ton`} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="Surplus" fill="#10B981" radius={[4, 4, 0, 0]} barSize={30} />
                <Bar dataKey="Deficit" fill="#EF4444" radius={[4, 4, 0, 0]} barSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {!loading && (
        <DistributionOptimizer 
          selKomoditas={filterKomoditas} 
          routesData={sorted} 
          alertsData={alertsData}
          komoditasList={null} 
        />
      )}

      <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Route Details Table</h3>
      <div className="data-table-wrapper fade-in">
        <div className="table-scroll">
          {loading ? (
             <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
               Generating Forecast-Aware Routes...
             </div>
          ) : (
          <table className="data-table">
            <thead>
              <tr>
                {[
                  ['rank', 'Rank'],
                  ['asal', 'Asal (Source)'],
                  ['tujuan', 'Tujuan (Dest)'],
                  ['komoditas', 'Komoditas'],
                  ['route_score', 'Route Score'],
                  [null, 'Status'],
                  [null, 'Detail'],
                ].map(([key, label]) => (
                  <th key={label} onClick={() => key && handleSort(key)} style={{ cursor: key ? 'pointer' : 'default' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      {label} {key && <SortIcon col={key} />}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sorted.map((r) => {
                const statusCfg = STATUS_CONFIG[r.status] || STATUS_CONFIG['open']
                const riskCfg = RISK_CONFIG[r.risk] || RISK_CONFIG['LOW']
                const isExpanded = expandedRow === r.rank
                return (
                  <React.Fragment key={r.rank}>
                    <tr style={{ cursor: 'pointer' }} onClick={() => setExpandedRow(isExpanded ? null : r.rank)}>
                      <td>
                        <div style={{
                          width: 28, height: 28, borderRadius: 7, background: 'var(--primary-light)',
                          color: 'var(--primary-dark)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 800, fontSize: 12,
                        }}>{r.rank}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>{r.asal}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>{r.tujuan}</div>
                      </td>
                      <td style={{ fontSize: 12 }}>{r.komoditas}</td>
                      <td>
                        <span style={{
                          background: r.route_score >= 70 ? 'rgba(16,185,129,0.12)' : 'rgba(59,130,246,0.1)',
                          color: r.route_score >= 70 ? 'var(--primary-dark)' : '#2563EB',
                          fontWeight: 700, fontSize: 12, padding: '3px 8px', borderRadius: 20,
                        }}>
                          {r.route_score}
                        </span>
                      </td>
                      <td>
                        <span style={{ background: statusCfg.bg, color: statusCfg.color, fontWeight: 600, fontSize: 11, padding: '3px 8px', borderRadius: 20 }}>
                          {statusCfg.badge}
                        </span>
                      </td>
                      <td>
                        <button style={{
                          background: 'none', border: 'none', cursor: 'pointer', color: 'var(--primary)',
                          fontWeight: 600, fontSize: 12, display: 'flex', alignItems: 'center', gap: 3,
                        }}>
                          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          {isExpanded ? 'Tutup' : 'Detail'}
                        </button>
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr key={`detail-${r.rank}`}>
                        <td colSpan={7} style={{ background: 'rgba(16,185,129,0.03)', padding: '12px 16px' }}>
                          <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                            <strong>📋 Detail Rute #{r.rank}:</strong> {r.detail}
                            <span style={{ marginLeft: 12, color: riskCfg.color, fontWeight: 600 }}>
                              Risk Score: {riskCfg.label}
                            </span>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                )
              })}
            </tbody>
          </table>
          )}
        </div>
      </div>
    </div>
  )
}
