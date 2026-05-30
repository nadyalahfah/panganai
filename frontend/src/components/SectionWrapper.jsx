import React from 'react';

export default function SectionWrapper({ icon: Icon, title, subtitle, rightContent, children, id, badge }) {
  return (
    <div id={id} style={{ background: 'white', borderRadius: 12, border: '1px solid var(--gray-200)', marginBottom: 24, overflow: 'hidden' }}>
      <div style={{ padding: '20px 24px', background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {Icon && (
            <div style={{ width: 36, height: 36, borderRadius: 8, background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#3B82F6', flexShrink: 0 }}>
              <Icon size={20} />
            </div>
          )}
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0F172A', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
              {title}
              {badge && <span style={{ fontSize: 10, background: '#3B82F6', color: 'white', padding: '2px 8px', borderRadius: 12, fontWeight: 800 }}>{badge}</span>}
            </h2>
            {subtitle && <div style={{ fontSize: 13, color: '#64748B', fontWeight: 500, marginTop: 2 }}>{subtitle}</div>}
          </div>
        </div>
        {rightContent && <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>{rightContent}</div>}
      </div>
      <div style={{ padding: 24 }}>
        {children}
      </div>
    </div>
  );
}
