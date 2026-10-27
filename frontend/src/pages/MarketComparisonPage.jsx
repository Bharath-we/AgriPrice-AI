import React, { useState, useEffect, useCallback } from 'react';
import { Store, Award, ArrowRight, BarChart2, RefreshCw, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { fetchMarketComparison } from '../services/api';
import { translations } from '../data/i18n';

const ALL_MARKET_IDS = [
  'dindigul', 'coimbatore', 'madurai', 'salem', 'tiruchirappalli',
  'erode', 'tirunelveli', 'thanjavur', 'vellore', 'chennai',
];

export default function MarketComparisonPage({ commodities, selectedCommodity, onSelectCommodity, lang }) {
  const t = translations[lang] || translations.en;

  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAdvisory, setShowAdvisory] = useState(true);
  const [showAssumptions, setShowAssumptions] = useState(false);

  const loadComparison = useCallback(async (commodity) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMarketComparison(commodity);
      setComparison(data);
    } catch (e) {
      setError(e.message || 'Failed to load market comparison data.');
      setComparison(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedCommodity) loadComparison(selectedCommodity);
  }, [selectedCommodity, loadComparison]);

  const markets = comparison?.markets_data || [];
  const maxPrice = markets.length > 0 ? Math.max(...markets.map((m) => m.modal_price_rs_per_quintal)) : 1;

  return (
    <div>
      {/* Header Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-primary-dark)' }}>
              {t.marketComparisonTitle || 'Cross-Mandi Price Comparison'}
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              Compare verified APMC modal prices across Tamil Nadu mandis for the same commodity and date.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <label style={{ fontSize: '0.88rem', fontWeight: 600 }}>Commodity:</label>
              <select
                id="mkt-compare-commodity"
                className="form-select"
                style={{ width: 'auto', minWidth: '190px' }}
                value={selectedCommodity}
                onChange={(e) => onSelectCommodity(e.target.value)}
              >
                {commodities.map((c) => (
                  <option key={c.id} value={c.id}>{c.name_en} ({c.name_ta})</option>
                ))}
              </select>
            </div>
            <button
              id="mkt-compare-refresh"
              onClick={() => loadComparison(selectedCommodity)}
              disabled={loading}
              style={{
                background: 'var(--color-primary)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 14px',
                fontWeight: 700,
                fontSize: '0.82rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                opacity: loading ? 0.7 : 1,
              }}
            >
              <RefreshCw size={14} className={loading ? 'spin' : ''} />
              {loading ? 'Loading…' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* Data source badge */}
        {comparison && (
          <div style={{
            marginTop: '14px',
            padding: '8px 14px',
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '8px',
            fontSize: '0.8rem',
            color: '#166534',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            flexWrap: 'wrap',
          }}>
            <Info size={14} />
            <span>
              Data from verified APMC mandi records as of{' '}
              <strong>{comparison.effective_observation_date}</strong> •
              {comparison.markets_count} markets compared •
              {comparison.price_unit}
            </span>
          </div>
        )}
      </div>

      {/* Error state */}
      {error && !loading && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '14px 18px', background: '#fef2f2', border: '1px solid #fecaca',
          borderRadius: '10px', color: '#b91c1c', fontSize: '0.88rem', marginBottom: '20px',
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="card" style={{ padding: '48px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
          <RefreshCw size={24} style={{ margin: '0 auto 12px', display: 'block', opacity: 0.5 }} />
          Fetching cross-market modal prices from Tamil Nadu APMC mandis…
        </div>
      )}

      {/* Results */}
      {!loading && comparison && markets.length > 0 && (
        <>
          {/* Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            {/* Highest Market */}
            <div style={{
              background: 'linear-gradient(135deg, #14532d, #15803d)',
              borderRadius: '12px',
              padding: '20px',
              color: '#fff',
            }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 700, opacity: 0.8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Highest Paying Mandi
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '8px' }}>
                ₹{comparison.highest_market.modal_price_per_kg?.toFixed(2)}/kg
              </div>
              <div style={{ fontSize: '0.88rem', marginTop: '4px', opacity: 0.9 }}>
                {comparison.highest_market.market_name} · {comparison.highest_market.district}
              </div>
              <div style={{ fontSize: '0.78rem', marginTop: '6px', opacity: 0.75 }}>
                ₹{comparison.highest_market.modal_price_rs_per_quintal?.toLocaleString('en-IN')}/Quintal
              </div>
            </div>

            {/* Lowest Market */}
            <div style={{
              background: 'linear-gradient(135deg, #78350f, #b45309)',
              borderRadius: '12px',
              padding: '20px',
              color: '#fff',
            }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 700, opacity: 0.8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Lowest Priced Mandi
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '8px' }}>
                ₹{comparison.lowest_market.modal_price_per_kg?.toFixed(2)}/kg
              </div>
              <div style={{ fontSize: '0.88rem', marginTop: '4px', opacity: 0.9 }}>
                {comparison.lowest_market.market_name} · {comparison.lowest_market.district}
              </div>
              <div style={{ fontSize: '0.78rem', marginTop: '6px', opacity: 0.75 }}>
                ₹{comparison.lowest_market.modal_price_rs_per_quintal?.toLocaleString('en-IN')}/Quintal
              </div>
            </div>

            {/* Price Spread */}
            <div style={{
              background: 'linear-gradient(135deg, #1e3a5f, #1d4ed8)',
              borderRadius: '12px',
              padding: '20px',
              color: '#fff',
            }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 700, opacity: 0.8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Inter-Mandi Spread
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '8px' }}>
                ₹{comparison.max_price_spread_per_kg?.toFixed(2)}/kg
              </div>
              <div style={{ fontSize: '0.88rem', marginTop: '4px', opacity: 0.9 }}>
                ₹{(comparison.max_price_spread_per_kg * 100)?.toLocaleString('en-IN')}/Quintal spread
              </div>
              <div style={{ fontSize: '0.78rem', marginTop: '6px', opacity: 0.75 }}>
                Routing to highest mandi could improve returns
              </div>
            </div>
          </div>

          {/* Table + Bar Chart */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px', marginBottom: '24px' }}>
            {/* Table */}
            <div className="card">
              <div className="card-header-bar">
                <h3 className="card-title">Mandi Price Leaderboard</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-primary)', fontWeight: 700 }}>
                  Spread: ₹{comparison.max_price_spread_per_kg?.toFixed(2)}/kg
                </span>
              </div>
              <div className="market-table-wrap">
                <table className="market-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>District · Market</th>
                      <th>Modal (₹/kg)</th>
                      <th>₹/Quintal</th>
                      <th>Min–Max (₹/kg)</th>
                      <th>Arrivals</th>
                    </tr>
                  </thead>
                  <tbody>
                    {markets.map((item, idx) => (
                      <tr key={item.market_id} style={{ background: item.is_highest_paying ? '#f0fdf4' : undefined }}>
                        <td style={{ fontWeight: 700, color: item.is_highest_paying ? '#16a34a' : 'inherit' }}>
                          {idx + 1}
                        </td>
                        <td>
                          <div style={{ fontWeight: 700, fontSize: '0.88rem' }}>{item.district}</div>
                          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>{item.market_name}</div>
                          {item.is_highest_paying && (
                            <span className="best-price-badge" style={{ marginTop: '2px', display: 'inline-block' }}>HIGHEST</span>
                          )}
                        </td>
                        <td style={{ fontWeight: 800, color: item.is_highest_paying ? 'var(--color-primary)' : 'inherit' }}>
                          ₹{item.modal_price_per_kg?.toFixed(2)}
                        </td>
                        <td style={{ fontSize: '0.85rem' }}>₹{item.modal_price_rs_per_quintal?.toLocaleString('en-IN')}</td>
                        <td style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                          {item.min_price_per_kg?.toFixed(1)}–{item.max_price_per_kg?.toFixed(1)}
                        </td>
                        <td style={{ fontSize: '0.82rem' }}>
                          {item.arrival_quintals > 0 ? `${item.arrival_quintals?.toFixed(0)} Qtl` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div style={{ padding: '10px 0 4px', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                Obs. date: {comparison.effective_observation_date} · Source: Verified APMC records
              </div>
            </div>

            {/* Visual Bar Chart */}
            <div className="card">
              <div className="card-header-bar">
                <div className="card-title-group">
                  <div className="card-title-icon"><BarChart2 size={22} /></div>
                  <div>
                    <h3 className="card-title">Price Spread Visualisation</h3>
                    <p className="card-subtitle">Relative modal rates across Tamil Nadu</p>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '12px' }}>
                {markets.map((item) => {
                  const pct = maxPrice > 0 ? (item.modal_price_rs_per_quintal / maxPrice) * 100 : 50;
                  return (
                    <div key={item.market_id}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
                        <span style={{ fontWeight: item.is_highest_paying ? 700 : 500 }}>
                          {item.district}
                        </span>
                        <span style={{ fontWeight: 700, color: item.is_highest_paying ? 'var(--color-primary)' : 'var(--color-text-muted)' }}>
                          ₹{item.modal_price_per_kg?.toFixed(2)}/kg
                          {item.spread_vs_lowest_per_kg > 0 && (
                            <span style={{ marginLeft: '6px', fontSize: '0.75rem', color: '#16a34a' }}>
                              +₹{item.spread_vs_lowest_per_kg?.toFixed(2)}
                            </span>
                          )}
                        </span>
                      </div>
                      <div style={{ width: '100%', height: '10px', background: '#e5e7eb', borderRadius: '5px', overflow: 'hidden' }}>
                        <div style={{
                          width: `${pct}%`,
                          height: '100%',
                          background: item.is_highest_paying
                            ? 'linear-gradient(90deg, #16a34a, #22c55e)'
                            : 'linear-gradient(90deg, #2d6a4f, #52b788)',
                          borderRadius: '5px',
                          transition: 'width 0.5s ease',
                        }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Advisory Panel */}
          <div style={{ marginBottom: '16px' }}>
            <div
              style={{
                background: '#f0fdf4',
                border: '1px solid #86efac',
                borderRadius: '10px',
                overflow: 'hidden',
              }}
            >
              <button
                id="mkt-compare-advisory-toggle"
                onClick={() => setShowAdvisory((v) => !v)}
                style={{
                  width: '100%',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '12px 18px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontWeight: 700,
                  fontSize: '0.9rem',
                  color: '#166534',
                }}
              >
                <span>📋 {lang === 'ta' ? 'சந்தை ஆலோசனை' : 'Verified Market Advisory'}</span>
                {showAdvisory ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>
              {showAdvisory && (
                <div style={{ padding: '0 18px 16px', fontSize: '0.88rem', color: '#14532d', lineHeight: '1.65' }}>
                  {lang === 'ta' ? comparison.advisory_ta : comparison.advisory_en}
                </div>
              )}
            </div>
          </div>

          {/* Assumptions Panel */}
          <div>
            <button
              id="mkt-compare-assumptions-toggle"
              onClick={() => setShowAssumptions((v) => !v)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.8rem',
                color: 'var(--color-text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 0',
              }}
            >
              <Info size={13} />
              {showAssumptions ? 'Hide' : 'Show'} Assumptions & Limitations
              {showAssumptions ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            </button>
            {showAssumptions && (
              <div style={{
                marginTop: '8px',
                padding: '14px 18px',
                background: '#f8fafc',
                border: '1px solid var(--color-surface-border)',
                borderRadius: '8px',
                fontSize: '0.8rem',
                color: 'var(--color-text-muted)',
                lineHeight: '1.6',
              }}>
                <strong style={{ color: 'var(--color-text-main)', display: 'block', marginBottom: '8px' }}>Assumptions:</strong>
                <ul style={{ margin: 0, paddingLeft: '18px' }}>
                  {(comparison.assumptions || []).map((a, i) => <li key={i}>{a}</li>)}
                </ul>
                <strong style={{ color: 'var(--color-text-main)', display: 'block', margin: '10px 0 6px' }}>Forecast Limitations:</strong>
                <p style={{ margin: 0 }}>{comparison.forecast_limitations}</p>
              </div>
            )}
          </div>
        </>
      )}

      {/* Empty state */}
      {!loading && !error && !comparison && (
        <div className="card" style={{ padding: '48px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
          Select a commodity above to compare mandi prices across Tamil Nadu.
        </div>
      )}
    </div>
  );
}
