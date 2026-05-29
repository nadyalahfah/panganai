import React, { useState, useMemo, useEffect } from 'react';
import { ShieldCheck, Target, TrendingDown, ArrowRight, Briefcase, Landmark, CheckCircle, ChevronRight, X } from 'lucide-react';
import { getKomoditasClass } from '../api';

const DIST_SOURCES = {
  "Beras Medium I": "Sulawesi Selatan",
  "Minyak Goreng Curah": "Jawa Barat",
  "Cabai Merah Keriting": "Jawa Timur",
  "Daging Ayam Ras": "Jawa Tengah",
  "Telur Ayam Ras": "Jawa Timur",
  "Bawang Merah": "Nusa Tenggara Barat",
  "Bawang Putih": "DKI Jakarta"
};

export default function PolicyRecommendation({ alerts }) {
  const [activeIdx, setActiveIdx] = useState(null);

  const recommendations = useMemo(() => {
    if (!alerts) return [];
    
    return alerts
      .filter(a => a.kenaikan_pct >= 5)
      .map(a => {
        const hash = a.provinsi.length + a.komoditas.length + a.kenaikan_pct;
        const days = (Math.floor(hash) % 3 + 2) * 7; 

        let level = 'WASPADA';
        let color = '#F97316';
        let bg = '#FFF7ED';
        let policy = 'Intervensi Terbatas & Monitoring';
        let shortPolicy = 'INTERVENSI TERBATAS';
        let reason = 'Tren harga mulai naik, indikasi awal gangguan pasokan lokal.';
        let impact = 'Mencegah potensi lonjakan harga >5% dalam bulan ini.';
        let confidence = 80 + (Math.floor(hash) % 10);
        
        if (a.kenaikan_pct > 15) {
          level = 'KRITIS';
          color = '#EF4444';
          bg = '#FEF2F2';
          policy = 'Operasi Pasar & Percepatan Distribusi';
          shortPolicy = 'OPERASI PASAR';
          reason = 'Defisit pasokan signifikan dan lonjakan permintaan di pasar hilir.';
          impact = `Menurunkan tekanan harga 8–12% dalam ${days} hari.`;
          confidence = 90 + (Math.floor(hash) % 8);
        }

        const sourceProv = DIST_SOURCES[a.komoditas] || "Jawa Timur";
        let distSource = sourceProv;
        let distDest = a.provinsi.replace(/^(DI|DKI) /, "");
        
        const mockSurplus = '+' + (Math.floor((a.harga_sekarang % 100) / 2) + 120) + ' Ton';
        const mockDeficit = '-' + (Math.floor((a.harga_sekarang % 100) / 2) + 95) + ' Ton';

        let distType = 'inter_prov';
        let distSupport = `${sourceProv} → ${a.provinsi.replace(/^(DI|DKI) /, "")}`;
        if (a.provinsi.includes(sourceProv)) {
          distType = 'intra_prov';
          distSupport = `Optimalisasi sentra produksi lokal (${sourceProv})`;
          distSource = `${sourceProv} (Sentra)`;
          distDest = `${sourceProv} (Pasar)`;
        }
        
        return {
          ...a, level, color, bg, policy, shortPolicy, reason, impact, distSupport, days, confidence, distSource, distDest, mockSurplus, mockDeficit, distType
        };
      })
      .sort((a, b) => b.kenaikan_pct - a.kenaikan_pct)
      .slice(0, 5);
  }, [alerts]);

  const activeRec = activeIdx !== null ? recommendations[activeIdx] : null;

  // Prevent background scrolling when drawer is open
  useEffect(() => {
    if (activeIdx !== null) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [activeIdx]);

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <>
      <div className="policy-panel" style={{ marginBottom: 24 }}>
        {/* FULL WIDTH: Recommendation List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <Landmark size={20} color="#0F172A" />
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0F172A', margin: 0 }}>Rekomendasi Kebijakan (AI Policy Engine)</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recommendations.map((rec, i) => {
              const isActive = activeIdx === i;
              return (
                <div 
                  key={i}
                  onClick={() => setActiveIdx(i)}
                  style={{ 
                    background: 'white', borderRadius: 10, padding: '0 20px',
                    border: `1px solid ${isActive ? rec.color : 'var(--gray-200)'}`,
                    boxShadow: isActive ? `0 4px 12px ${rec.color}15` : '0 1px 2px rgba(0,0,0,0.05)',
                    cursor: 'pointer', transition: 'all 0.2s',
                    display: 'grid', 
                    gridTemplateColumns: '40px 150px 130px 1.2fr 1fr 140px 24px',
                    gap: 16, alignItems: 'center',
                    height: 90
                  }}
                  className="policy-row"
                >
                  {/* Rank Badge */}
                  <div style={{ 
                    width: 40, height: 40, borderRadius: 20,
                    background: rec.bg, color: rec.color,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 16, fontWeight: 900
                  }}>
                    #{i + 1}
                  </div>

                  <div style={{ overflow: 'hidden' }}>
                    <span className={`komoditas-badge ${getKomoditasClass(rec.komoditas)}`} style={{ padding: '4px 10px', fontSize: 11, display: 'inline-block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%' }}>
                      {rec.komoditas}
                    </span>
                  </div>

                  <div style={{ fontSize: 14, fontWeight: 700, color: '#0F172A', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {rec.provinsi.replace(/^(DI|DKI) /, "")}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, overflow: 'hidden' }}>
                    <Target size={14} color="#3B82F6" flexShrink={0} /> 
                    <span style={{ fontSize: 13, color: '#1E293B', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {rec.policy}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, overflow: 'hidden' }}>
                    <TrendingDown size={14} color="#10B981" flexShrink={0} />
                    <span style={{ fontSize: 13, color: '#10B981', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {rec.impact}
                    </span>
                  </div>

                  <div style={{ 
                    fontSize: 10, fontWeight: 800, padding: '6px 0', borderRadius: 12,
                    background: rec.bg, color: rec.color, whiteSpace: 'nowrap', textAlign: 'center',
                    width: '100%'
                  }}>
                    PRIORITAS {rec.level === 'KRITIS' ? 'TINGGI' : 'MENENGAH'}
                  </div>
                  
                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <ChevronRight size={20} color={isActive ? rec.color : '#CBD5E1'} flexShrink={0} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* DRAWER BACKDROP */}
      <div 
        onClick={() => setActiveIdx(null)}
        style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.4)',
          zIndex: 9998,
          opacity: activeIdx !== null ? 1 : 0,
          pointerEvents: activeIdx !== null ? 'auto' : 'none',
          transition: 'opacity 0.3s ease-in-out'
        }}
      />

      {/* RIGHT DRAWER PANEL */}
      <div 
        style={{ 
          position: 'fixed', top: 0, right: 0, bottom: 0,
          width: '100%', maxWidth: 450,
          background: 'white', zIndex: 9999,
          display: 'flex', flexDirection: 'column',
          boxShadow: '-4px 0 24px rgba(0,0,0,0.15)',
          transform: activeIdx !== null ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          overflowY: 'auto'
        }}
      >
        {activeRec && (
          <>
            {/* Drawer Header */}
            <div style={{ padding: '24px 32px', background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', borderTop: `4px solid ${activeRec.color}`, position: 'relative' }}>
              <button 
                onClick={() => setActiveIdx(null)}
                style={{ 
                  position: 'absolute', top: 16, right: 16, 
                  background: 'transparent', border: 'none', cursor: 'pointer',
                  color: '#64748B', padding: 8, borderRadius: 20, transition: 'background 0.2s'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = '#E2E8F0'}
                onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <X size={20} />
              </button>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
                <ShieldCheck size={18} color="#3B82F6" />
                <span style={{ fontWeight: 'bold', fontSize: 14, color: '#0F172A' }}>Detail Kebijakan</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 24, fontWeight: 800, color: '#0F172A', marginBottom: 4, lineHeight: 1.2 }}>{activeRec.komoditas}</div>
                  <div style={{ fontSize: 15, color: '#64748B', fontWeight: 600 }}>{activeRec.provinsi}</div>
                </div>
                <div style={{ display: 'inline-flex' }}>
                  <div style={{ 
                    background: '#EFF6FF', color: '#1D4ED8', padding: '6px 12px', borderRadius: 20, 
                    fontSize: 11, fontWeight: 800, border: '1px solid #BFDBFE'
                  }}>
                    {activeRec.shortPolicy}
                  </div>
                </div>
              </div>
            </div>

            {/* Drawer Body */}
            <div style={{ padding: 32, display: 'flex', flexDirection: 'column', gap: 32 }}>
              {/* KPI Cards row */}
              <div style={{ display: 'flex', gap: 12 }}>
                <div style={{ flex: 1, background: activeRec.bg, padding: '16px 12px', borderRadius: 8, border: `1px solid ${activeRec.color}30`, minHeight: 90, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: 11, color: activeRec.color, fontWeight: 800 }}>STATUS</div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: activeRec.color }}>{activeRec.level}</div>
                </div>
                <div style={{ flex: 1, background: '#F8FAFC', padding: '16px 12px', borderRadius: 8, border: '1px solid #E2E8F0', minHeight: 90, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: 11, color: '#64748B', fontWeight: 800 }}>PREDIKSI</div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: '#0F172A' }}>+{activeRec.kenaikan_pct.toFixed(1)}%</div>
                </div>
                <div style={{ flex: 1, background: '#F8FAFC', padding: '16px 12px', borderRadius: 8, border: '1px solid #E2E8F0', minHeight: 90, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: 11, color: '#64748B', fontWeight: 800 }}>CONFIDENCE</div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: '#0F172A' }}>{activeRec.confidence}%</div>
                </div>
              </div>

              {/* Action Section */}
              <div>
                <div style={{ fontSize: 13, color: '#64748B', fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Briefcase size={16} /> KEBIJAKAN UTAMA
                </div>
                <div style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 8 }}>
                  {activeRec.policy}
                </div>
                <div style={{ fontSize: 14, color: '#475569', lineHeight: 1.6 }}>
                  <span style={{ fontWeight: 700, color: '#1E293B' }}>Alasan: </span>
                  {activeRec.reason}
                </div>
              </div>

              {/* Distribution Support */}
              <div style={{ background: '#EFF6FF', padding: 20, borderRadius: 8, border: '1px solid #BFDBFE' }}>
                <div style={{ fontSize: 13, color: '#1E40AF', fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <ArrowRight size={16} /> DUKUNGAN DISTRIBUSI
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                  <div style={{ textAlign: 'center', flex: 1 }}>
                    <div style={{ fontSize: 12, color: '#3B82F6', fontWeight: 700, marginBottom: 6 }}>SUMBER</div>
                    <div style={{ fontSize: 14, color: '#1E3A8A', fontWeight: 800 }}>{activeRec.distSource}</div>
                  </div>
                  <div style={{ color: '#93C5FD', display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0, padding: '0 16px' }}>
                    <ArrowRight size={24} />
                  </div>
                  <div style={{ textAlign: 'center', flex: 1 }}>
                    <div style={{ fontSize: 12, color: '#3B82F6', fontWeight: 700, marginBottom: 6 }}>TUJUAN</div>
                    <div style={{ fontSize: 14, color: '#1E3A8A', fontWeight: 800 }}>{activeRec.distDest}</div>
                  </div>
                </div>

                {activeRec.distType === 'inter_prov' && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', background: 'white', padding: '12px 16px', borderRadius: 8, border: '1px solid #DBEAFE' }}>
                    <div style={{ fontSize: 13, color: '#475569', fontWeight: 600 }}>
                      Surplus: <span style={{ color: '#10B981', fontWeight: 800 }}>{activeRec.mockSurplus}</span>
                    </div>
                    <div style={{ fontSize: 13, color: '#475569', fontWeight: 600 }}>
                      Defisit: <span style={{ color: '#EF4444', fontWeight: 800 }}>{activeRec.mockDeficit}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Impact */}
              <div style={{ background: '#F0FDF4', padding: 20, borderRadius: 8, border: '1px solid #BBF7D0', marginBottom: 32 }}>
                <div style={{ fontSize: 13, color: '#166534', fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CheckCircle size={16} /> ESTIMASI DAMPAK
                </div>
                <div style={{ fontSize: 15, color: '#14532D', fontWeight: 700, lineHeight: 1.5 }}>
                  {activeRec.impact}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
