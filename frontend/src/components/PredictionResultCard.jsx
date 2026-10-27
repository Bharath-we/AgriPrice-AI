import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus, ShieldCheck, CheckCircle2, AlertTriangle, Clock, Info, AlertCircle } from 'lucide-react';
import { translations } from '../data/i18n';

export default function PredictionResultCard({ prediction, lang }) {
  const t = translations[lang] || translations.en;

  if (!prediction) {
    return (
      <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '340px' }}>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.95rem' }}>
          Select a commodity and click "Calculate Price Forecast" to view AI predictions.
        </p>
      </div>
    );
  }

  const {
    predicted_modal_price_per_quintal,
    predicted_price_per_kg,
    confidence_lower_per_kg,
    confidence_upper_per_kg,
    baseline_last_observed_price_per_kg,
    baseline_last_observed_price_per_quintal,
    forecast_horizon_days,
    last_observation_date,
    price_change_pct,
    performance_vs_baseline,
    farmer_action,
    farmer_advice_en,
    farmer_advice_ta,
    seasonal_phase,
    estimated_arrival_quintals,
    commodity_name_en,
    commodity_name_ta,
    market_name_en,
    target_date,
    warnings = [],
    is_synthetic,
    disclaimer,
  } = prediction;

  const isPositive = price_change_pct > 2.0;
  const isNegative = price_change_pct < -2.0;

  const actionStyle =
    farmer_action === 'HOLD'
      ? 'hold'
      : farmer_action === 'SELL_NOW'
      ? 'sell'
      : farmer_action === 'INSUFFICIENT_DATA'
      ? 'sell'
      : 'monitor';

  const actionLabel =
    farmer_action === 'HOLD'
      ? t.actionHold
      : farmer_action === 'SELL_NOW'
      ? t.actionSell
      : farmer_action === 'INSUFFICIENT_DATA'
      ? 'INSUFFICIENT DATA'
      : t.actionMonitor;

  return (
    <div className="card">
      <div className="card-header-bar">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span
              style={{
                background: 'var(--color-primary)',
                color: '#ffffff',
                fontSize: '0.72rem',
                fontWeight: 800,
                padding: '2px 8px',
                borderRadius: '12px',
                textTransform: 'uppercase',
              }}
            >
              {forecast_horizon_days}-Day Forecast Horizon
            </span>
            {is_synthetic && (
              <span
                style={{
                  background: '#fef3c7',
                  color: '#92400e',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: '12px',
                }}
              >
                TEST FIXTURE
              </span>
            )}
          </div>
          <h2 className="card-title">{t.resultTitle}</h2>
          <p className="card-subtitle">
            {commodity_name_en} ({commodity_name_ta}) • {market_name_en} • Target: {target_date}
          </p>
        </div>
      </div>

      <div className="result-card-inner">
        {/* Warnings Banner if any */}
        {warnings && warnings.length > 0 && (
          <div
            style={{
              background: '#fffbeb',
              border: '1px solid #fde68a',
              borderRadius: '8px',
              padding: '10px 14px',
              fontSize: '0.82rem',
              color: '#92400e',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '8px',
            }}
          >
            <AlertCircle size={16} style={{ marginTop: '2px', flexShrink: 0 }} />
            <div>
              {warnings.map((w, idx) => (
                <div key={idx}>{w}</div>
              ))}
            </div>
          </div>
        )}

        {/* Main Price Highlight */}
        <div className="price-hero-box">
          <div className="price-hero-label">{t.modalPriceLabel}</div>
          <div className="price-hero-val">
            <span>₹{predicted_price_per_kg.toFixed(2)}</span>
            <span className="price-unit">/ kg</span>
          </div>
          <div className="price-quintal-sub">
            ₹{predicted_modal_price_per_quintal.toLocaleString('en-IN')} {t.perQuintal}
          </div>

          <div className="confidence-band">
            <ShieldCheck size={16} color="#2d6a4f" />
            <span>
              {t.confidenceRange}: ₹{confidence_lower_per_kg.toFixed(2)} - ₹{confidence_upper_per_kg.toFixed(2)} / kg
            </span>
          </div>
        </div>

        {/* Farmer Strategy Advisory */}
        <div className={`advisory-badge-box ${actionStyle}`}>
          <div className="advisory-header">
            <span className={`action-pill ${actionStyle}`}>
              {farmer_action === 'HOLD' && <Clock size={16} />}
              {farmer_action === 'SELL_NOW' && <AlertTriangle size={16} />}
              {farmer_action === 'MONITOR' && <CheckCircle2 size={16} />}
              {actionLabel}
            </span>

            <span
              className={`trend-percent ${
                isPositive ? 'positive' : isNegative ? 'negative' : 'neutral'
              }`}
            >
              {isPositive ? '+' : ''}
              {price_change_pct}% vs baseline
            </span>
          </div>

          <p className="advisory-desc-en">{farmer_advice_en}</p>
          <p className="advisory-desc-ta">{farmer_advice_ta}</p>
        </div>

        {/* Supporting Market Metrics */}
        <div className="meta-grid">
          <div className="meta-box">
            <div className="meta-label">Last Observed Baseline</div>
            <div className="meta-val">
              ₹{baseline_last_observed_price_per_kg.toFixed(2)} / kg
              <span style={{ fontSize: '0.72rem', display: 'block', color: 'var(--color-text-light)' }}>
                Observed on {last_observation_date}
              </span>
            </div>
          </div>

          <div className="meta-box">
            <div className="meta-label">Baseline Comparison</div>
            <div className="meta-val" style={{ fontSize: '0.9rem' }}>
              {price_change_pct > 0 ? `+₹${(predicted_price_per_kg - baseline_last_observed_price_per_kg).toFixed(2)}` : `-₹${Math.abs(predicted_price_per_kg - baseline_last_observed_price_per_kg).toFixed(2)}`} / kg
              <span style={{ fontSize: '0.72rem', display: 'block', color: 'var(--color-text-light)' }}>
                vs Naive Persistence
              </span>
            </div>
          </div>

          <div className="meta-box">
            <div className="meta-label">Supply at Origin</div>
            <div className="meta-val">{estimated_arrival_quintals} Qtl</div>
          </div>

          <div className="meta-box">
            <div className="meta-label">Tamil Nadu Season</div>
            <div className="meta-val" style={{ fontSize: '0.82rem' }}>{seasonal_phase}</div>
          </div>
        </div>

        {/* Non-financial disclaimer */}
        <div style={{ fontSize: '0.72rem', color: 'var(--color-text-light)', borderTop: '1px solid var(--color-surface-border)', paddingTop: '10px' }}>
          <strong>Notice: </strong>
          {disclaimer || 'Advisory is a statistical decision-support indicator and not guaranteed financial advice.'}
        </div>
      </div>
    </div>
  );
}
