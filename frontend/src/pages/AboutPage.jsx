import React from 'react';
import { Sprout, ShieldAlert, Cpu, MapPin, CheckCircle2 } from 'lucide-react';
import { translations } from '../data/i18n';

export default function AboutPage({ lang }) {
  const t = translations[lang] || translations.en;

  const mandis = [
    { district: "Coimbatore", name: "Coimbatore MGR Mandi & Pollachi Copra Market" },
    { district: "Dindigul", name: "Ottanchatram Vegetable & Shallot Terminal" },
    { district: "Madurai", name: "Madurai Paravai Central Wholesale Market" },
    { district: "Salem", name: "Salem Shevapet & SAGOSERVE Tapioca Mandi" },
    { district: "Tiruchirappalli", name: "Trichy Gandhi Market & Banana Mandi" },
    { district: "Erode", name: "Erode Regulated Market (Turmeric GI Hub)" },
    { district: "Tirunelveli", name: "Tirunelveli Nainarkulam Vegetable Market" },
    { district: "Thanjavur", name: "Thanjavur Delta Paddy Regulated Market" },
    { district: "Vellore", name: "Vellore Nethaji Vegetable Market" },
    { district: "Chennai", name: "Koyambedu Wholesale APMC Market Complex" },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Mission Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #0f3823 0%, #1b4332 100%)', color: '#ffffff' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '14px' }}>
          <div style={{ width: '44px', height: '44px', background: 'rgba(255,255,255,0.1)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Sprout size={26} color="#74c69d" />
          </div>
          <div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.6rem', fontWeight: 800 }}>
              About AgriPrice AI — Tamil Nadu
            </h2>
            <p style={{ color: 'var(--color-mint-pale)', fontSize: '0.88rem' }}>
              Empowering farmers & agricultural trade with fair price forecasting and transparent mandi intelligence
            </p>
          </div>
        </div>

        <p style={{ lineHeight: '1.7', fontSize: '0.95rem', color: '#e2f0e6', maxWidth: '820px' }}>
          Agricultural commodity spot prices across Tamil Nadu fluctuate sharply due to seasonal arrival surges, weather shocks, and festive demand cycles. AgriPrice AI provides farmers and cooperatives with predictive clarity on whether to sell immediately or hold for better returns, while routing produce to the highest-paying APMC regulated market center.
        </p>
      </div>

      {/* Mandi Coverage */}
      <div className="card">
        <div className="card-header-bar">
          <div className="card-title-group">
            <div className="card-title-icon">
              <MapPin size={22} />
            </div>
            <div>
              <h3 className="card-title">Covered Tamil Nadu APMC Regulated Markets</h3>
              <p className="card-subtitle">10 primary agricultural wholesale terminals across the state</p>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '14px', marginTop: '12px' }}>
          {mandis.map((m, idx) => (
            <div
              key={idx}
              style={{
                border: '1px solid var(--color-surface-border)',
                borderRadius: '10px',
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                background: 'var(--color-bg-base)',
              }}
            >
              <CheckCircle2 size={18} color="var(--color-primary-light)" style={{ flexShrink: 0 }} />
              <div>
                <strong style={{ fontSize: '0.92rem', color: 'var(--color-primary-dark)' }}>{m.district}</strong>
                <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>{m.name}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack */}
      <div className="card">
        <div className="card-header-bar">
          <div className="card-title-group">
            <div className="card-title-icon">
              <Cpu size={22} />
            </div>
            <div>
              <h3 className="card-title">Technology & Architecture</h3>
              <p className="card-subtitle">Intermediate Full-Stack AI project specifications</p>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginTop: '12px' }}>
          <div style={{ padding: '14px', background: 'var(--color-bg-base)', borderRadius: '8px', border: '1px solid var(--color-surface-border)' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Frontend</h4>
            <p style={{ fontWeight: 700, color: 'var(--color-primary-dark)', marginTop: '4px' }}>React 18 + Vite</p>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>Responsive green-and-white farmer UI with bilingual Tamil support</span>
          </div>

          <div style={{ padding: '14px', background: 'var(--color-bg-base)', borderRadius: '8px', border: '1px solid var(--color-surface-border)' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Backend</h4>
            <p style={{ fontWeight: 700, color: 'var(--color-primary-dark)', marginTop: '4px' }}>FastAPI + Python 3.13</p>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>High-performance async REST API with Pydantic v2 schemas</span>
          </div>

          <div style={{ padding: '14px', background: 'var(--color-bg-base)', borderRadius: '8px', border: '1px solid var(--color-surface-border)' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Machine Learning</h4>
            <p style={{ fontWeight: 700, color: 'var(--color-primary-dark)', marginTop: '4px' }}>Scikit-learn 1.9</p>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>Multi-horizon RandomForestRegressor with zero future data leakage</span>
          </div>

          <div style={{ padding: '14px', background: 'var(--color-bg-base)', borderRadius: '8px', border: '1px solid var(--color-surface-border)' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>Data Processing</h4>
            <p style={{ fontWeight: 700, color: 'var(--color-primary-dark)', marginTop: '4px' }}>Pandas 3.1</p>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>Time-series feature engineering, lag features & missing data audit</span>
          </div>
        </div>
      </div>

      {/* Disclaimers */}
      <div
        className="card"
        style={{
          borderLeft: '5px solid #d97706',
          background: '#fffbeb',
          padding: '18px 24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#92400e', fontWeight: 700, fontSize: '0.92rem', marginBottom: '4px' }}>
          <ShieldAlert size={18} />
          <span>Important Agricultural & Market Advisory Disclaimer</span>
        </div>
        <p style={{ fontSize: '0.82rem', color: '#78350f', lineHeight: '1.6' }}>
          AgriPrice AI forecasts are probabilistic econometric estimates derived from historical trading behavior. Spot bidding in regulated mandis depends on real-time factors including daily arrivals, produce moisture, grade quality, and local transporter strikes. Farmers should verify spot bidding at their local APMC regulated mandi before executing large commercial sales.
        </p>
      </div>
    </div>
  );
}
