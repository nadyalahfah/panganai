import React, { useState, useMemo } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { formatRupiahShort } from '../api';

const geoUrl = '/indonesia-province-simple.json';

export default function IndonesiaMap({ data, komoditas, horizon = 7 }) {
  const [hoverRegion, setHoverRegion] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [selectedProv, setSelectedProv] = useState(null);

  // Parse backend data into a lookup dictionary keyed by normalized province name
  const provDataMap = useMemo(() => {
    const mapData = {};
    if (!data) return mapData;
    data.forEach(d => {
      let normalizedName = d.name.toUpperCase().trim();
      
      // Alias mapping for GeoJSON compatibility
      const aliases = {
        "KEPULAUAN BANGKA BELITUNG": "BANGKA BELITUNG",
      };
      if (aliases[normalizedName]) {
        normalizedName = aliases[normalizedName];
      }

      const changePct = ((d.prediksi - d.harga) / d.harga) * 100;
      const absChange = Math.abs(changePct);
      
      let status = 'Safe';
      let color = '#10B981'; // Green
      
      if (absChange >= 20) {
        status = 'Critical';
        color = '#EF4444'; // Red
      } else if (absChange >= 10) {
        status = 'High Risk';
        color = '#F97316'; // Orange
      } else if (absChange >= 5) {
        status = 'Watch';
        color = '#EAB308'; // Yellow
      }

      mapData[normalizedName] = {
        ...d,
        changePct,
        status,
        color
      };
    });
    return mapData;
  }, [data]);

  const handleMouseEnter = (geo, e) => {
    const provName = geo.properties.Propinsi.toUpperCase().trim();
    const provData = provDataMap[provName] || {
      name: geo.properties.Propinsi,
      harga: 0,
      prediksi: 0,
      changePct: 0,
      status: 'Safe',
      color: '#10B981' // default green if no data
    };
    
    setHoverRegion({ ...provData, rawName: geo.properties.Propinsi });
    setTooltipPos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e) => {
    setTooltipPos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseLeave = () => {
    setHoverRegion(null);
  };

  const handleClick = (geo) => {
    const provName = geo.properties.Propinsi.toUpperCase().trim();
    // Toggle selection
    if (selectedProv === provName) {
      setSelectedProv(null);
    } else {
      setSelectedProv(provName);
    }
  };

  return (
    <div 
      style={{ 
        position: 'relative', 
        width: '100%', 
        height: 400, 
        background: 'var(--gray-50)', 
        borderRadius: 8, 
        overflow: 'hidden',
        border: '1px solid var(--gray-200)'
      }}
    >
      {/* Map */}
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          center: [118, -2],
          scale: 1200
        }}
        style={{ width: '100%', height: '100%' }}
      >
        <Geographies geography={geoUrl}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const provName = geo.properties.Propinsi.toUpperCase().trim();
              const d = provDataMap[provName];
              const defaultColor = '#10B981'; // safe green default
              const fillColor = d ? d.color : defaultColor;
              const isSelected = selectedProv === provName;
              
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  onMouseEnter={(e) => handleMouseEnter(geo, e)}
                  onMouseMove={handleMouseMove}
                  onMouseLeave={handleMouseLeave}
                  onClick={() => handleClick(geo)}
                  style={{
                    default: {
                      fill: fillColor,
                      stroke: isSelected ? '#111827' : '#FFFFFF',
                      strokeWidth: isSelected ? 1.5 : 0.5,
                      outline: 'none',
                      opacity: isSelected ? 1 : 0.85
                    },
                    hover: {
                      fill: fillColor,
                      stroke: '#111827',
                      strokeWidth: 1,
                      outline: 'none',
                      opacity: 1,
                      cursor: 'pointer'
                    },
                    pressed: {
                      fill: fillColor,
                      stroke: '#111827',
                      strokeWidth: 1.5,
                      outline: 'none',
                      opacity: 1
                    }
                  }}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>

      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: 16,
        left: 16,
        background: 'rgba(255, 255, 255, 0.9)',
        padding: '8px 12px',
        borderRadius: 6,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        fontSize: 12,
        fontWeight: 500,
        display: 'flex',
        flexDirection: 'column',
        gap: 6
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, borderRadius: 2, background: '#10B981' }}></div>
          <span>Safe (&lt; 5% Change)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, borderRadius: 2, background: '#EAB308' }}></div>
          <span>Watch (5–10% Change)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, borderRadius: 2, background: '#F97316' }}></div>
          <span>High Risk (10–20% Change)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 12, height: 12, borderRadius: 2, background: '#EF4444' }}></div>
          <span>Critical (&gt; 20% Change)</span>
        </div>
      </div>

      {/* Custom Tooltip */}
      {hoverRegion && (
        <div style={{
          position: 'fixed',
          top: tooltipPos.y + 15,
          left: tooltipPos.x + 15,
          background: 'white',
          padding: 12,
          borderRadius: 8,
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          border: '1px solid var(--gray-200)',
          pointerEvents: 'none',
          zIndex: 1000,
          minWidth: 200
        }}>
          <div style={{ fontWeight: 'bold', fontSize: 14, marginBottom: 4 }}>
            {hoverRegion.name}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
            Commodity: <span style={{ fontWeight: 500, color: '#111827' }}>{komoditas}</span>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
            <span style={{ color: 'var(--text-muted)' }}>Status:</span>
            <span style={{ fontWeight: 'bold', color: hoverRegion.color }}>
              {hoverRegion.status}
            </span>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
            <span style={{ color: 'var(--text-muted)' }}>Current Price:</span>
            <span style={{ fontWeight: 500 }}>
              {hoverRegion.harga > 0 ? formatRupiahShort(hoverRegion.harga) : '—'}
            </span>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
            <span style={{ color: 'var(--text-muted)' }}>Forecast (+{horizon} Days):</span>
            <span style={{ fontWeight: 500 }}>
              {hoverRegion.prediksi > 0 ? formatRupiahShort(hoverRegion.prediksi) : '—'}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginTop: 6, paddingTop: 6, borderTop: '1px solid var(--gray-100)' }}>
            <span style={{ color: 'var(--text-muted)' }}>Change:</span>
            <span style={{ 
              fontWeight: 'bold', 
              color: hoverRegion.changePct > 0 ? '#EF4444' : hoverRegion.changePct < 0 ? '#10B981' : '#6B7280' 
            }}>
              {hoverRegion.changePct > 0 ? '+' : ''}{hoverRegion.changePct.toFixed(1)}%
            </span>
          </div>
          
          {hoverRegion.score && (
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginTop: 4 }}>
              <span style={{ color: 'var(--text-muted)' }}>Risk Score:</span>
              <span style={{ fontWeight: 'bold' }}>{hoverRegion.score}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
