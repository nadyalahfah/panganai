import React, { useState, useMemo } from 'react';
import { AlertTriangle, AlertCircle, Info, Activity, ChevronRight, Zap, Target, ShieldAlert, Navigation, Bell, X, FileText } from 'lucide-react';
import { getKomoditasClass } from '../api';
import SectionWrapper from './SectionWrapper';

export default function EarlyWarningSystem({ alerts, horizonDays = 7 }) {
  const [activeIdx, setActiveIdx] = useState(0);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

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
        {/* FULL WIDTH TABLE */}
        <div style={{ flex: 1, background: 'white', borderRadius: 12, border: '1px solid var(--gray-200)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--gray-200)', background: '#F8FAFC', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Activity size={18} color="#0F172A" />
              <span style={{ fontWeight: 'bold', fontSize: 15, color: '#0F172A' }}>Monitoring Anomali Nasional</span>
            </div>
            <span style={{ fontSize: 11, color: '#64748B', fontWeight: 600, background: '#E2E8F0', padding: '4px 10px', borderRadius: 20 }}>
              Top {Math.min(10, processedAlerts.length)} Peringatan
            </span>
          </div>

          <div style={{ overflowX: 'auto', flex: 1 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
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
                  return (
                    <tr 
                      key={i} 
                      style={{ 
                        borderBottom: '1px solid #F1F5F9', 
                        background: 'white'
                      }}
                    >
                      <td style={{ padding: '12px 16px', fontSize: 13, fontWeight: 700, color: '#9CA3AF' }}>
                        {i + 1}
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <span className={`komoditas-badge ${getKomoditasClass(a.komoditas)}`} style={{ padding: '2px 8px', fontSize: 11 }}>{a.komoditas}</span>
                      </td>
                      <td style={{ padding: '12px 16px', fontWeight: 600, color: '#1E293B', fontSize: 13 }}>
                        {a.provinsi.replace(/^(DI|DKI) /, "")}
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <div style={{ 
                          display: 'inline-flex', alignItems: 'center', gap: 4, 
                          background: a.bg, color: a.color, padding: '2px 8px', 
                          borderRadius: 12, fontSize: 11, fontWeight: 700 
                        }}>
                          <MyIcon size={12} /> {a.level}
                        </div>
                      </td>
                      <td style={{ padding: '12px 16px', fontWeight: 800, color: a.color, fontSize: 13, textAlign: 'right' }}>
                        +{a.kenaikan_pct.toFixed(1)}%
                      </td>
                      <td style={{ padding: '12px 16px', fontSize: 12, color: '#475569', textAlign: 'center', fontWeight: 500 }}>
                        {a.days} Hari
                      </td>
                      <td style={{ padding: '12px 16px', fontSize: 12, fontWeight: 600, color: '#475569' }}>
                        {a.action}
                      </td>
                      <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                        <button 
                          onClick={() => {
                            setActiveIdx(i);
                            setIsDrawerOpen(true);
                          }}
                          style={{ 
                            background: '#EFF6FF',
                            border: '1px solid #BFDBFE',
                            color: '#2563EB', 
                            padding: '6px 10px', borderRadius: 6,
                            cursor: 'pointer', transition: 'all 0.2s',
                            display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, fontWeight: 600
                          }}
                          onMouseEnter={(e) => e.currentTarget.style.background = '#DBEAFE'}
                          onMouseLeave={(e) => e.currentTarget.style.background = '#EFF6FF'}
                        >
                          Investigasi <ChevronRight size={14} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {processedAlerts.length === 0 && (
                  <tr>
                    <td colSpan="8" style={{ padding: 40, textAlign: 'center', color: '#9CA3AF', fontSize: 13 }}>
                      Tidak ada anomali harga yang terdeteksi.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* AZURE-STYLE OVERLAY DRAWER */}
      {isDrawerOpen && (
        <div 
          style={{
            position: 'fixed', inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.20)', 
            backdropFilter: 'blur(6px)', 
            zIndex: 9999,
            transition: 'opacity 0.3s'
          }}
          onClick={() => setIsDrawerOpen(false)}
        />
      )}
      
      <div 
        style={{
          position: 'fixed', top: 0, right: 0, height: '100vh', 
          width: 'min(520px, 100vw)', 
          background: 'white', 
          zIndex: 10000, 
          boxShadow: '-8px 0 32px rgba(0,0,0,0.15)',
          transform: isDrawerOpen ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 300ms cubic-bezier(0.2, 0.8, 0.2, 1)',
          display: 'flex', flexDirection: 'column'
        }}
      >
        {activeAlert && (
          <>
            {/* Drawer Header */}
            <div style={{ 
              padding: '20px 24px', 
              background: '#F8FAFC', 
              borderBottom: '1px solid #E2E8F0',
              display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <FileText size={16} color="#3B82F6" />
                  <span style={{ fontSize: 12, fontWeight: 700, color: '#3B82F6', letterSpacing: '0.05em' }}>
                    AI INVESTIGATION REPORT
                  </span>
                </div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#0F172A', marginBottom: 4 }}>
                  ID-{(activeIdx + 1).toString().padStart(4, '0')}
                </div>
              </div>
              <button 
                onClick={() => setIsDrawerOpen(false)}
                style={{ 
                  background: 'white', border: '1px solid #E2E8F0', borderRadius: '50%',
                  width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  cursor: 'pointer', color: '#64748B', transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = '#F1F5F9'; e.currentTarget.style.color = '#0F172A'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = 'white'; e.currentTarget.style.color = '#64748B'; }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Drawer Scrollable Content */}
            <div style={{ padding: '24px', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 24 }}>
              
              {/* Context Block */}
              <div>
                <div style={{ fontSize: 24, fontWeight: 800, color: '#0F172A', marginBottom: 6 }}>
                  {activeAlert.komoditas}
                </div>
                <div style={{ fontSize: 15, color: '#475569', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Navigation size={16} color="#9CA3AF" /> {activeAlert.provinsi}
                </div>
              </div>

              {/* Metrics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div style={{ background: '#F8FAFC', padding: 16, borderRadius: 8, border: '1px solid #E2E8F0' }}>
                  <div style={{ fontSize: 11, color: '#64748B', fontWeight: 700, marginBottom: 8, letterSpacing: '0.05em' }}>STATUS RISIKO</div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: activeAlert.color, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <activeAlert.Icon size={18} /> {activeAlert.level}
                  </div>
                </div>
                <div style={{ background: '#F8FAFC', padding: 16, borderRadius: 8, border: '1px solid #E2E8F0' }}>
                  <div style={{ fontSize: 11, color: '#64748B', fontWeight: 700, marginBottom: 8, letterSpacing: '0.05em' }}>PREDIKSI ({activeAlert.days} HARI)</div>
                  <div style={{ fontSize: 18, fontWeight: 800, color: '#0F172A' }}>
                    +{activeAlert.kenaikan_pct.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* AI Analysis / Root Cause */}
              <div>
                <div style={{ fontSize: 13, color: '#0F172A', fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <ShieldAlert size={16} color="#EF4444" /> PRIMARY CAUSE ANALYSIS
                </div>
                <div style={{ fontSize: 14, color: '#334155', lineHeight: 1.6, background: '#F8FAFC', padding: 16, borderRadius: 8, border: '1px solid #E2E8F0' }}>
                  {activeAlert.cause}
                </div>
              </div>

              {/* Recommended Action */}
              <div>
                <div style={{ fontSize: 13, color: '#0F172A', fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Target size={16} color="#10B981" /> RECOMMENDED ACTION
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div style={{ fontSize: 14, color: '#1E293B', lineHeight: 1.6, background: `${activeAlert.color}10`, borderLeft: `4px solid ${activeAlert.color}`, padding: '12px 16px', borderRadius: '0 8px 8px 0' }}>
                    {activeAlert.action}
                  </div>
                  {activeAlert.level === 'Kritis' && activeAlert.distRec && (
                    <div style={{ fontSize: 14, color: '#1E293B', lineHeight: 1.6, background: '#EFF6FF', borderLeft: '4px solid #3B82F6', padding: '12px 16px', borderRadius: '0 8px 8px 0' }}>
                      {activeAlert.distRec}
                    </div>
                  )}
                </div>
              </div>

            </div>


          </>
        )}
      </div>
    </SectionWrapper>
  );
}
