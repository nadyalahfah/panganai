import React, { useState, useMemo } from 'react';
import { AlertTriangle, AlertCircle, Info, Activity, ChevronRight, Zap, Target, ShieldAlert, Navigation, Bell } from 'lucide-react';
import { getKomoditasClass } from '../api';
import SectionWrapper from './SectionWrapper';

export default function EarlyWarningSystem({ alerts, horizonDays = 7 }) {
  const [activeIdx, setActiveIdx] = useState(0);

const processedAlerts = useMemo(() => {
    if (!alerts) return [];
    
    return alerts.map(a => {
      let level = 'Rendah';
      let colorClass = 'info'; 
      let bg = '#F1F5F9';
      let color = '#64748B';
      let Icon = Info;
      let action = 'Pantau';
      let cause = a.ai_reasoning || 'Fluktuasi dalam batas wajar';
      let distRec = '';
      
      // Derive action from level if not explicitly provided
      const risk = (a.risk_level || '').toUpperCase();
      const pct = Number(a.kenaikan_pct || 0);
      
      if (risk === 'CRITICAL' || pct > 15) {
        level = 'Kritis';
        colorClass = 'danger';
        bg = '#FEF2F2';
        color = '#EF4444';
        Icon = AlertTriangle;
        action = 'Intervensi Pasokan';
        if (!cause || cause.length < 10) cause = 'Indikasi defisit pasokan serius.';
      } else if (risk === 'HIGH' || pct >= 10) {
        level = 'Tinggi';
        colorClass = 'warning';
        bg = '#FFF7ED';
        color = '#F97316';
        Icon = AlertCircle;
        action = 'Inspeksi Lapangan';
        if (!cause || cause.length < 10) cause = 'Tren kenaikan harga signifikan.';
      } else if (risk === 'WATCH' || pct >= 5) {
        level = 'Waspada';
        colorClass = 'info';
        bg = '#FEF9C3';
        color = '#CA8A04';
        Icon = Info;
        action = 'Monitor Lanjut';
        if (!cause || cause.length < 10) cause = 'Gejolak harga minor terdeteksi.';
      }

      return {
        ...a, level, colorClass, bg, color, Icon, action, cause, distRec, days: horizonDays
      };
    }).sort((a, b) => Math.abs(b.kenaikan_pct || 0) - Math.abs(a.kenaikan_pct || 0));
  }, [alerts, horizonDays]);

  const activeAlert = processedAlerts[activeIdx] || null;

  return (
    <SectionWrapper
      icon={Bell}
      title="Sistem Peringatan Dini"
      subtitle="Deteksi dini anomali harga dan risiko pasokan"
    >
      <div className="ews-panel" style={{ display: 'flex', gap: 20, minHeight: 450 }}>
      {/* LEFT COLUMN: 70% Table */}
      <div className="ews-list-card" style={{ flex: 7, background: 'white', borderRadius: 12, border: '1px solid var(--gray-200)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div className="ews-card-header" style={{ padding: '14px 20px', borderBottom: '1px solid var(--gray-200)', background: '#F8FAFC', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={18} color="#0F172A" />
            <span style={{ fontWeight: 'bold', fontSize: 15, color: '#0F172A' }}>Monitoring Anomali Nasional</span>
          </div>
          <span style={{ fontSize: 11, color: '#64748B', fontWeight: 600, background: '#E2E8F0', padding: '4px 10px', borderRadius: 20 }}>
            Top {Math.min(10, processedAlerts.length)} Peringatan
          </span>
        </div>

        <div className="ews-table-wrap" style={{ overflowX: 'auto', flex: 1 }}>
          <table className="ews-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--gray-200)', background: 'white' }}>
                <th style={{ padding: '12px 16px', fontSize: 11, color: '#64748B', fontWeight: 700, width: 40 }}>#</th>
                <th style={{ padding: '12px 16px', fontSize: 11, color: '#64748B', fontWeight: 700 }}>KOMODITAS</th>
                <th style={{ padding: '12px 16px', fontSize: 11, color: '#64748B', fontWeight: 700 }}>PROVINSI</th>
                <th style={{ padding: '12px 16px', fontSize: 11, color: '#64748B', fontWeight: 700 }}>RISIKO</th>
                <th style={{ padding: '12px 16px', fontSize: 11, color: '#64748B', fontWeight: 700, textAlign: 'right' }}>Δ HARGA</th>
                <th style={{ padding: '12px 16px', fontSize: 11, color: '#64748B', fontWeight: 700, textAlign: 'center' }}>RENTANG PREDIKSI</th>
                <th style={{ padding: '12px 16px', fontSize: 11, color: '#64748B', fontWeight: 700 }}>AKSI REKOMENDASI</th>
                <th style={{ padding: '12px 16px', fontSize: 11, color: '#64748B', fontWeight: 700 }}></th>
              </tr>
            </thead>
            <tbody>
              {processedAlerts.slice(0, 10).map((a, i) => {
                const MyIcon = a.Icon;
                const isActive = activeIdx === i;
                return (
                  <tr
                    className="ews-alert-row"
                    key={i} 
                    onClick={() => setActiveIdx(i)}
                    style={{ 
                      borderBottom: '1px solid #F1F5F9', 
                      background: isActive ? '#F8FAFC' : 'white',
                      cursor: 'pointer',
                      transition: 'background 0.2s'
                    }}
                  >
                    <td data-label="#" style={{ padding: '12px 16px', fontSize: 13, fontWeight: 700, color: '#9CA3AF' }}>
                      {i + 1}
                    </td>
                    <td data-label="Komoditas" style={{ padding: '12px 16px' }}>
                      <span className={`komoditas-badge ${getKomoditasClass(a.komoditas)}`} style={{ padding: '2px 8px', fontSize: 11 }}>{a.komoditas}</span>
                    </td>
                    <td data-label="Provinsi" style={{ padding: '12px 16px', fontWeight: 600, color: '#1E293B', fontSize: 13 }}>
                      {a.provinsi.replace(/^(DI|DKI) /, "")}
                    </td>
                    <td data-label="Risiko" style={{ padding: '12px 16px' }}>
                      <div style={{ 
                        display: 'inline-flex', alignItems: 'center', gap: 4, 
                        background: a.bg, color: a.color, padding: '2px 8px', 
                        borderRadius: 12, fontSize: 11, fontWeight: 700 
                      }}>
                        <MyIcon size={12} /> {a.level}
                      </div>
                    </td>
                    <td data-label="Harga" style={{ padding: '12px 16px', fontWeight: 800, color: a.color, fontSize: 13, textAlign: 'right' }}>
                      +{a.kenaikan_pct.toFixed(1)}%
                    </td>
                    <td data-label="Rentang" style={{ padding: '12px 16px', fontSize: 12, color: '#475569', textAlign: 'center', fontWeight: 500 }}>
                      {a.days} Hari
                    </td>
                    <td data-label="Aksi" style={{ padding: '12px 16px', fontSize: 12, fontWeight: 600, color: '#3B82F6' }}>
                      {a.action}
                    </td>
                    <td className="ews-row-action" style={{ padding: '12px 16px', textAlign: 'right' }}>
                      <button style={{ 
                        background: isActive ? a.color : 'transparent',
                        border: 'none',
                        color: isActive ? 'white' : '#9CA3AF', 
                        padding: '4px 8px', borderRadius: 6,
                        cursor: 'pointer', transition: 'all 0.2s'
                      }}>
                        <ChevronRight size={16} />
                      </button>
                    </td>
                  </tr>
                );
              })}
              {processedAlerts.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ padding: 40, textAlign: 'center', color: '#9CA3AF', fontSize: 13 }}>
                    Tidak ada anomali harga yang terdeteksi.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* RIGHT COLUMN: 30% AI Insight Panel */}
      <div className="ews-insight-card" style={{ flex: 3, background: 'white', borderRadius: 12, border: '1px solid var(--gray-200)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div className="ews-card-header" style={{ padding: '14px 20px', background: '#F8FAFC', borderBottom: '1px solid var(--gray-200)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Zap size={16} color="#3B82F6" fill="#3B82F6" opacity={0.2} />
            <span style={{ fontWeight: 'bold', fontSize: 14, color: '#0F172A' }}>Rekomendasi AI</span>
          </div>
        </div>

        {activeAlert ? (
          <div className="ews-insight-body" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Header Info */}
            <div style={{ paddingBottom: 16, borderBottom: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#0F172A', marginBottom: 4 }}>
                {activeAlert.komoditas}
              </div>
              <div style={{ fontSize: 14, color: '#64748B', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Navigation size={14} /> {activeAlert.provinsi}
              </div>
            </div>

            {/* Metrics Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div style={{ background: '#F8FAFC', padding: 12, borderRadius: 8, border: '1px solid #E2E8F0' }}>
                <div style={{ fontSize: 11, color: '#64748B', fontWeight: 600, marginBottom: 4 }}>STATUS</div>
                <div style={{ fontSize: 14, fontWeight: 800, color: activeAlert.color, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <activeAlert.Icon size={16} /> {activeAlert.level}
                </div>
              </div>
              <div style={{ background: '#F8FAFC', padding: 12, borderRadius: 8, border: '1px solid #E2E8F0' }}>
                <div style={{ fontSize: 11, color: '#64748B', fontWeight: 600, marginBottom: 4 }}>PREDIKSI & RENTANG</div>
                <div style={{ fontSize: 14, fontWeight: 800, color: '#0F172A' }}>
                  +{activeAlert.kenaikan_pct.toFixed(1)}% <span style={{ fontSize: 12, fontWeight: 500, color: '#64748B' }}>/ {activeAlert.days}H</span>
                </div>
              </div>
            </div>

            {/* Root Cause */}
            <div>
              <div style={{ fontSize: 12, color: '#64748B', fontWeight: 700, marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                <ShieldAlert size={14} /> PENYEBAB
              </div>
              <div style={{ fontSize: 13, color: '#1E293B', lineHeight: 1.5, background: '#F8FAFC', padding: 12, borderRadius: 8 }}>
                {activeAlert.cause}
              </div>
            </div>

            {/* Recommendation */}
            <div>
              <div style={{ fontSize: 12, color: '#64748B', fontWeight: 700, marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Target size={14} /> REKOMENDASI AKSI
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ fontSize: 13, color: '#1E293B', lineHeight: 1.5, background: `${activeAlert.color}10`, borderLeft: `3px solid ${activeAlert.color}`, padding: '10px 12px', borderRadius: '0 8px 8px 0' }}>
                  {activeAlert.action}
                </div>
                {activeAlert.level === 'Kritis' && (
                  <div style={{ fontSize: 13, color: '#1E293B', lineHeight: 1.5, background: '#EFF6FF', borderLeft: '3px solid #3B82F6', padding: '10px 12px', borderRadius: '0 8px 8px 0' }}>
                    {activeAlert.distRec}
                  </div>
                )}
              </div>
            </div>

          </div>
        ) : (
          <div style={{ padding: 40, textAlign: 'center', color: '#9CA3AF', fontSize: 13 }}>
            Pilih alert dari tabel untuk melihat rekomendasi AI.
          </div>
        )}
      </div>
      </div>
    </SectionWrapper>
  );
}
