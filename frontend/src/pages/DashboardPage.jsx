import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, ArrowUpRight, ArrowRight, ShieldCheck, Activity, MapPin, Sparkles } from 'lucide-react';
import { fetchLatestPrices } from '../services/api';
import { translations } from '../data/i18n';

export default function DashboardPage({ commodities, markets, onSelectCropForForecast, lang }) {
  const t = translations[lang] || translations.en;
  const [latestPrices, setLatestPrices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await fetchLatestPrices();
        setLatestPrices(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div>
      {/* Overview Stat Tiles */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
          marginBottom: '28px',
        }}
      >
        <div className="card" style={{ padding: '18px' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>
            Regulated APMC Mandis
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-primary-dark)', marginTop: '4px' }}>
            10 Hubs
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-primary)', marginTop: '4px' }}>
            Coimbatore, Dindigul, Madurai, Erode & more
          </div>
        </div>

        <div className="card" style={{ padding: '18px' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>
            Tamil Nadu Staple Crops
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-primary-dark)', marginTop: '4px' }}>
            10 Commodities
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Tomato, Shallots, Turmeric, Paddy, Coconut...
          </div>
        </div>

        <div className="card" style={{ padding: '18px' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>
            ML Model R² Score
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-primary-dark)', marginTop: '4px' }}>
            99.7%
          </div>
          <div style={{ fontSize: '0.78rem', color: '#16a34a', fontWeight: 600, marginTop: '4px' }}>
            +62.06% vs Last-Observed Baseline
          </div>
        </div>

        <div className="card" style={{ padding: '18px' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-text-light)', textTransform: 'uppercase' }}>
            Test Evaluation MAE
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-primary-dark)', marginTop: '4px' }}>
            ±₹1.28 / kg
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            Evaluated on 29,000 unseen observations
          </div>
        </div>
      </div>

      {/* Live Market Price Matrix */}
      <div className="card" style={{ marginBottom: '28px' }}>
        <div className="card-header-bar">
          <div className="card-title-group">
            <div className="card-title-icon">
              <Activity size={22} />
            </div>
            <div>
              <h3 className="card-title">Live Tamil Nadu Agricultural Price Board</h3>
              <p className="card-subtitle">
                Latest spot trading benchmarks from regulated mandis across Tamil Nadu
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
            Loading market prices from FastAPI backend...
          </div>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
              gap: '16px',
            }}
          >
            {latestPrices.map((item) => {
              const isGain = item.trend_7d_pct > 0;
              const isLoss = item.trend_7d_pct < 0;

              return (
                <div
                  key={item.commodity_id}
                  style={{
                    background: '#ffffff',
                    border: '1.5px solid var(--color-surface-border)',
                    borderRadius: '12px',
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    boxShadow: 'var(--shadow-sm)',
                    transition: 'all 0.2s',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-primary-dark)' }}>
                          {item.name_en}
                        </h4>
                        <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                          {item.name_ta}
                        </span>
                      </div>
                      <span
                        style={{
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          padding: '3px 8px',
                          borderRadius: '12px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '2px',
                          background: isGain ? '#dcfce7' : isLoss ? '#ffe4e6' : '#f3f4f6',
                          color: isGain ? '#15803d' : isLoss ? '#be123c' : '#4b5563',
                        }}
                      >
                        {isGain ? <TrendingUp size={12} /> : isLoss ? <TrendingDown size={12} /> : null}
                        {isGain ? '+' : ''}{item.trend_7d_pct}% (7d)
                      </span>
                    </div>

                    <div style={{ marginTop: '14px', display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                      <span style={{ fontFamily: 'var(--font-heading)', fontSize: '1.9rem', fontWeight: 800, color: 'var(--color-primary-dark)' }}>
                        ₹{item.price_per_kg.toFixed(2)}
                      </span>
                      <span style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>/ kg</span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--color-text-light)', marginLeft: 'auto' }}>
                        ₹{item.modal_price_per_quintal.toLocaleString('en-IN')}/Qtl
                      </span>
                    </div>

                    <div style={{ marginTop: '8px', fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
                      📍 Mandi: <strong style={{ textTransform: 'capitalize' }}>{item.benchmark_market}</strong> • Arrival: {item.arrival_quintals} Qtl
                    </div>
                  </div>

                  <button
                    onClick={() => onSelectCropForForecast(item.commodity_id)}
                    style={{
                      marginTop: '14px',
                      background: 'var(--color-mint-bg)',
                      color: 'var(--color-primary-dark)',
                      border: '1px solid var(--color-mint-pale)',
                      borderRadius: '8px',
                      padding: '8px 12px',
                      fontSize: '0.82rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px',
                      transition: 'all 0.2s',
                    }}
                  >
                    <Sparkles size={14} color="var(--color-primary)" />
                    <span>Run AI Price Forecast</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
