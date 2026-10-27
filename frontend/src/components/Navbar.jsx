import React from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  Store,
  Calculator,
  BellRing,
  FileCheck2,
  Sliders,
  HelpCircle,
} from 'lucide-react';
import { translations } from '../data/i18n';

export default function Navbar({ activePage, setActivePage, lang }) {
  const t = translations[lang] || translations.en;

  const navItems = [
    { id: 'dashboard', label: t.navDashboard, icon: LayoutDashboard },
    { id: 'prediction', label: t.navPrediction, icon: TrendingUp },
    { id: 'comparison', label: t.navComparison, icon: Store },
    { id: 'calculator', label: t.navCalculator, icon: Calculator },
    { id: 'alerts', label: t.navAlerts, icon: BellRing },
    { id: 'dataquality', label: t.navDataQuality, icon: FileCheck2 },
    { id: 'performance', label: t.navPerformance, icon: Sliders },
    { id: 'about', label: t.navAbout, icon: HelpCircle },
  ];

  return (
    <nav
      style={{
        background: '#ffffff',
        borderBottom: '1px solid var(--color-surface-border)',
        boxShadow: '0 2px 8px rgba(15, 56, 35, 0.04)',
      }}
    >
      <div className="container">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            overflowX: 'auto',
            padding: '8px 0',
            scrollbarWidth: 'none',
          }}
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 16px',
                  borderRadius: '10px',
                  border: 'none',
                  background: isActive ? 'var(--color-mint-bg)' : 'transparent',
                  color: isActive ? 'var(--color-primary-dark)' : 'var(--color-text-muted)',
                  fontFamily: 'var(--font-heading)',
                  fontSize: '0.88rem',
                  fontWeight: isActive ? 700 : 500,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.2s ease',
                  borderBottom: isActive ? '3px solid var(--color-primary-light)' : '3px solid transparent',
                }}
              >
                <Icon size={17} color={isActive ? 'var(--color-primary)' : '#738a79'} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
