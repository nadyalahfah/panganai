import { useMemo } from 'react'
import {
  ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Legend,
} from 'recharts'
import { formatRupiah, formatRupiahShort, formatTanggalShort } from '../api'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null

  // Remove duplicate 'Prediksi' value if 'Aktual' is also present (at the transition point)
  const hasAktual = payload.some(p => p.dataKey === 'aktual')
  const filteredPayload = payload.filter(p => !(p.dataKey === 'prediksi' && hasAktual))

  return (
    <div className="custom-tooltip">
      <div className="tooltip-date">{formatTanggalShort(label)}</div>
      {filteredPayload.map((p, i) => (
        <div key={i} className="tooltip-item">
          <span className="tooltip-dot" style={{ background: p.color || p.stroke }} />
          <span>{p.name}: {formatRupiah(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

export default function GrafikPrediksi({ historis, prediksi, komoditas, tanggalHariIni, het, historyDays = 45 }) {
  const chartData = useMemo(() => {
    const result = []
    if (historis && historis.length > 0) {
      historis.slice(-historyDays).forEach((d) => {
        result.push({ tanggal: d.tanggal, tanggalMs: new Date(d.tanggal).getTime(), aktual: d.harga, prediksi: null })
      })
    }
    if (prediksi && prediksi.length > 0 && result.length > 0) {
      const last = result[result.length - 1]
      // Connect the lines by setting the first prediction point at the last actual date
      last.prediksi = last.aktual
      
      prediksi.forEach((d) => {
        result.push({
          tanggal: d.tanggal,
          tanggalMs: new Date(d.tanggal).getTime(),
          aktual: null,
          prediksi: d.prediksi,
        })
      })
    }
    return result
  }, [historis, prediksi, historyDays])

  if (chartData.length === 0) return <div className="skeleton skeleton-chart" />

  const allVals = chartData.flatMap(d => [d.aktual, d.prediksi].filter(Boolean))
  const minVal = Math.min(...allVals), maxVal = Math.max(...allVals)
  const padding = (maxVal - minVal) * 0.02 || 500
  const yMin = Math.max(0, Math.floor((minVal - padding) / 1000) * 1000)
  const yMax = Math.ceil((maxVal + padding) / 1000) * 1000

  return (
    <div className="pred-chart-wrapper fade-in">
      <div className="chart-card-header" style={{ marginBottom: 16 }}>
        <div className="chart-card-title">
          📈 Grafik Prediksi — {komoditas}
        </div>
        <div style={{ display: 'flex', gap: 16, fontSize: 12 }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ width: 16, height: 2.5, background: '#3B82F6', display: 'inline-block' }} />
            Aktual
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ width: 16, height: 2.5, background: '#10B981', display: 'inline-block' }} />
            Prediksi
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={330}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 12, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="gAktual" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gPrediksi" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
          <XAxis
            dataKey="tanggalMs"
            type="number"
            scale="time"
            domain={['dataMin', 'dataMax']}
            tickFormatter={formatTanggalShort}
            tick={{ fontSize: 10, fill: '#9CA3AF' }}
            interval="preserveStartEnd"
            minTickGap={50}
          />
          <YAxis
            domain={[yMin, yMax]}
            tickFormatter={formatRupiahShort}
            tick={{ fontSize: 10, fill: '#9CA3AF' }}
            width={68}
          />
          <Tooltip content={<CustomTooltip />} />
          {tanggalHariIni && (
            <ReferenceLine
              x={new Date(tanggalHariIni).getTime()}
              stroke="#6B7280"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{ value: 'Hari ini', position: 'top', fill: '#6B7280', fontSize: 10, fontWeight: 600 }}
            />
          )}
          {het && (
            <ReferenceLine
              y={het}
              stroke="#EF4444"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{ value: 'Ambang Batas (HET)', position: 'insideTopRight', fill: '#EF4444', fontSize: 10, fontWeight: 600 }}
            />
          )}
          <Area
            type="monotone"
            dataKey="aktual"
            name="Harga Aktual"
            stroke="#3B82F6"
            strokeWidth={2.5}
            fill="url(#gAktual)"
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0, fill: '#3B82F6' }}
            connectNulls={false}
          />
          <Area
            type="monotone"
            dataKey="prediksi"
            name="Prediksi"
            stroke="#10B981"
            strokeWidth={2.5}
            strokeDasharray="5 5"
            fill="url(#gPrediksi)"
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0, fill: '#10B981' }}
            connectNulls={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
