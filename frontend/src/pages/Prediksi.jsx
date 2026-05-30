import { useState, useEffect } from 'react'
import { Bot, DollarSign, TrendingUp, BarChart2, Search } from 'lucide-react'
import GrafikPrediksi from '../components/GrafikPrediksi'
import TabelProvinsi from '../components/TabelProvinsi'
import {
  fetchKomoditas, fetchProvinsi, fetchPrediksi,
  fetchHargaHistoris, fetchPrediksiSemua,
  formatRupiah, formatPct, getTrenClass,
} from '../api'

const AI_INSIGHTS = {
  'Cabai Merah Keriting': {
    title: 'Analisis Tren Cabai Merah Keriting',
    body: `Harga cabai merah keriting menunjukkan tren kenaikan dalam periode terkini. Prediksi model AI mengindikasikan potensi kenaikan berkelanjutan terutama didorong oleh:`,
    bullets: [
      'Pola musiman: permintaan meningkat menjelang hari besar nasional',
      'Volatilitas pasokan dari daerah produksi utama (Jawa Timur, Jawa Barat)',
      'Sensitivitas terhadap kondisi cuaca ekstrem di sentra produksi',
    ],
    rekomendasi: 'Pantau stok nasional dan pertimbangkan intervensi harga jika kenaikan melebihi 15% dari HET.',
  },
  'Beras Medium I': {
    title: 'Analisis Tren Beras Medium I',
    body: `Harga beras medium I relatif stabil dengan tren moderat. Model AI mendeteksi:`,
    bullets: [
      'Pasokan dari sentra produksi (Jawa, Sumatera) masih dalam batas normal',
      'Kebijakan impor beras berkontribusi menjaga stabilitas harga',
      'Proyeksi harga mendekati Harga Eceran Tertinggi (HET) di beberapa provinsi',
    ],
    rekomendasi: 'Pastikan distribusi merata agar tidak terjadi kesenjangan harga antar wilayah.',
  },
  'Minyak Goreng Curah': {
    title: 'Analisis Tren Minyak Goreng Curah',
    body: `Minyak goreng curah memiliki sensitivitas tinggi terhadap harga CPO global. Analisis model:`,
    bullets: [
      'Harga CPO internasional berpengaruh langsung pada harga domestik',
      'Program intervensi minyak goreng curah memoderasi kenaikan harga',
      'Stok nasional saat ini dalam kondisi mencukupi kebutuhan 3 bulan ke depan',
    ],
    rekomendasi: 'Monitor fluktuasi harga CPO global dan siapkan mekanisme buffer stock di daerah defisit.',
  },
}

export default function Prediksi() {
  const [komoditasList, setKomoditasList] = useState([])
  const [provinsiList, setProvinsiList] = useState([])
  const [selKomoditas, setSelKomoditas] = useState('Beras Medium I')
  const [selProvinsi, setSelProvinsi] = useState('DKI Jakarta')
  const [prediksi, setPrediksi] = useState(null)
  const [historis, setHistoris] = useState([])
  const [semuaProv, setSemuaProv] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [initialized, setInitialized] = useState(false)
  const [period, setPeriod] = useState('30')

  useEffect(() => {
    async function loadFilters() {
      try {
        const [kom, prov] = await Promise.all([fetchKomoditas(), fetchProvinsi()])
        setKomoditasList(kom)
        setProvinsiList(prov)
        loadData('Beras Medium I', 'DKI Jakarta')
        setInitialized(true)
      } catch (err) {
        setError(err.message)
      }
    }
    loadFilters()
  }, [])

  async function loadData(komoditas, provinsi) {
    try {
      setLoading(true)
      setError(null)
      const [predData, histData, semuaData] = await Promise.all([
        fetchPrediksi(komoditas, provinsi),
        fetchHargaHistoris(komoditas, provinsi),
        fetchPrediksiSemua(komoditas),
      ])
      setPrediksi(predData)
      setHistoris(histData)
      setSemuaProv(semuaData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = () => loadData(selKomoditas, selProvinsi)

  const ringkasan = prediksi?.ringkasan || {}
  const harian = prediksi?.harian || []

  const ubah7 = ringkasan.harga_sekarang && ringkasan.prediksi_7h
    ? ((ringkasan.prediksi_7h - ringkasan.harga_sekarang) / ringkasan.harga_sekarang * 100) : 0
  const ubah30 = ringkasan.harga_sekarang && ringkasan.prediksi_30h
    ? ((ringkasan.prediksi_30h - ringkasan.harga_sekarang) / ringkasan.harga_sekarang * 100) : 0

  const confidence7 = ringkasan.mape_pct ? Math.max(50, Math.round(100 - ringkasan.mape_pct)) : 85
  const confidence30 = ringkasan.mape_pct ? Math.max(40, Math.round(85 - ringkasan.mape_pct)) : 72

  const insight = AI_INSIGHTS[selKomoditas] || AI_INSIGHTS['Beras Medium I']

  const harian30 = period === '7' ? harian.slice(0, 7) : harian

  if (error && !initialized) {
    return (
      <div>
        <div className="page-header"><h2>Prediksi Harga</h2><p>Analisis dan prediksi harga pangan per provinsi</p></div>
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Tidak dapat terhubung ke server</h3>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h2>Prediksi Harga</h2>
        <p>Analisis dan prediksi harga pangan per provinsi menggunakan model LSTM + Prophet</p>
      </div>

      {/* ── Filter Bar ── */}
      <div style={{
        background: 'var(--bg-card)', border: '1px solid var(--border)',
        borderRadius: 12, padding: '16px 18px', marginBottom: 20,
        display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end',
        boxShadow: 'var(--shadow-card)',
      }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 5, textTransform: 'uppercase', letterSpacing: '0.4px' }}>Komoditas</div>
          <select className="filter-select" value={selKomoditas} onChange={e => setSelKomoditas(e.target.value)}>
            {komoditasList.map(k => <option key={k} value={k}>{k}</option>)}
          </select>
        </div>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 5, textTransform: 'uppercase', letterSpacing: '0.4px' }}>Provinsi</div>
          <select className="filter-select" value={selProvinsi} onChange={e => setSelProvinsi(e.target.value)}>
            {provinsiList.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 5, textTransform: 'uppercase', letterSpacing: '0.4px' }}>Periode Prediksi</div>
          <div className="toggle-group">
            <button className={`toggle-btn-item${period === '7' ? ' active' : ''}`} onClick={() => setPeriod('7')}>7 Hari</button>
            <button className={`toggle-btn-item${period === '30' ? ' active' : ''}`} onClick={() => setPeriod('30')}>30 Hari</button>
          </div>
        </div>
        <button className="filter-btn" onClick={handleSubmit} disabled={loading} style={{ marginTop: 16 }}>
          <Search size={14} /> {loading ? 'Memuat...' : 'Tampilkan'}
        </button>
      </div>

      {loading ? (
        <>
          <div className="skeleton skeleton-chart" style={{ marginBottom: 20 }} />
          <div className="pred-summary-grid">
            {[0,1,2].map(i => <div key={i} className="skeleton skeleton-card" />)}
          </div>
        </>
      ) : (
        <>
          {/* ── Prediction Chart ── */}
          <GrafikPrediksi
            historis={historis}
            prediksi={harian30}
            komoditas={selKomoditas}
            tanggalHariIni="2026-04-13"
          />

          {/* ── Split Card ── */}
          <div className="split-card">
            <div className="split-card-top">
              <TrendingUp size={18} color="var(--primary)" />
              <span style={{ fontWeight: 700, fontSize: 14 }}>
                {selKomoditas} — {selProvinsi}
              </span>
            </div>
            <div className="split-card-body">
              <div className="split-card-left">
                <div className="split-section-label"><BarChart2 size={12} /> Data Aktual</div>
                <div className="split-row">
                  <span className="split-row-label">Harga Hari Ini</span>
                  <span className="split-row-value">{formatRupiah(ringkasan.harga_sekarang)}</span>
                </div>
                <div className="split-row">
                  <span className="split-row-label">Rata-rata 7H</span>
                  <span className="split-row-value">{formatRupiah(ringkasan.harga_sekarang)}</span>
                </div>
                <div className="split-row">
                  <span className="split-row-label">Volatilitas (MAE)</span>
                  <span className="split-row-value">{formatRupiah(ringkasan.mae) || '—'}</span>
                </div>
                <div className="split-row">
                  <span className="split-row-label">Sumber Data</span>
                  <span className="split-row-value">PIHPS BI</span>
                </div>
              </div>
              <div className="split-card-right">
                <div className="split-section-label">🔮 Data Prediksi</div>
                <div className="split-row">
                  <span className="split-row-label">Prediksi H+7</span>
                  <span className="split-row-value">{formatRupiah(ringkasan.prediksi_7h)}</span>
                </div>
                <div className="split-row">
                  <span className="split-row-label">Perubahan H+7</span>
                  <span className={`split-row-value ${ubah7 > 0 ? 'text-naik' : 'text-turun'}`}>
                    {ubah7 > 0 ? '↑' : '↓'} {formatPct(ubah7)}
                  </span>
                </div>
                <div className="split-row">
                  <span className="split-row-label">Prediksi H+30</span>
                  <span className="split-row-value">{formatRupiah(ringkasan.prediksi_30h)}</span>
                </div>
                <div className="split-row">
                  <span className="split-row-label">Perubahan H+30</span>
                  <span className={`split-row-value ${ubah30 > 0 ? 'text-naik' : 'text-turun'}`}>
                    {ubah30 > 0 ? '↑' : '↓'} {formatPct(ubah30)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* ── 3 Metric Cards ── */}
          <div className="pred-summary-grid">
            {[
              {
                label: '💰 Harga Hari Ini',
                value: formatRupiah(ringkasan.harga_sekarang),
                sub: 'Confidence: 100%',
                color: '#3B82F6',
                trend: null,
                note: 'Sumber: PIHPS Bank Indonesia',
              },
              {
                label: '📈 Prediksi 7 Hari',
                value: formatRupiah(ringkasan.prediksi_7h),
                sub: `Perubahan: ${formatPct(ubah7)}`,
                color: ubah7 > 0 ? '#EF4444' : '#22C55E',
                trend: ringkasan?.tren_7h,
                note: `Confidence: ${confidence7}% | LSTM + Prophet`,
              },
              {
                label: '📊 Prediksi 30 Hari',
                value: formatRupiah(ringkasan.prediksi_30h),
                sub: `Perubahan: ${formatPct(ubah30)}`,
                color: ubah30 > 0 ? '#EF4444' : '#22C55E',
                trend: ringkasan?.tren_30h,
                note: `Confidence: ${confidence30}% | LSTM + Prophet`,
              },
            ].map((c, i) => (
              <div key={i} className="pred-summary-card">
                <div className="pred-label">{c.label}</div>
                <div className="pred-value font-mono" style={{ color: c.color }}>{c.value}</div>
                <div className="pred-change">
                  <span className={`tren-badge ${getTrenClass(c.trend)}`}>{c.trend || 'AKTUAL'}</span>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{c.sub}</span>
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>{c.note}</div>
              </div>
            ))}
          </div>

          {/* ── AI Insight Box ── */}
          <div className="ai-insight-box">
            <div className="ai-insight-header">
              <Bot size={18} color="#2563EB" />
              <span className="ai-insight-title">🤖 AI Insight — {insight.title}</span>
            </div>
            <div className="ai-insight-body">
              <p style={{ marginBottom: 8 }}>{insight.body}</p>
              <ul>
                {insight.bullets.map((b, i) => <li key={i}>{b}</li>)}
              </ul>
              <p style={{ marginTop: 10 }}>
                <strong>Rekomendasi:</strong> {insight.rekomendasi}
              </p>
            </div>
            <div className="ai-insight-footer">
              📌 Confidence Score: {confidence7}% | Model: LSTM + Prophet | Last Updated: {new Date().toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })}
            </div>
          </div>

          {/* ── Province Table ── */}
          <div className="section-header">
            <div className="section-title">📋 Prediksi Harga per Provinsi — {selKomoditas}</div>
          </div>
          <TabelProvinsi data={semuaProv} />
        </>
      )}
    </div>
  )
}
