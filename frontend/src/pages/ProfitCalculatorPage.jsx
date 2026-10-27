import React, { useState, useCallback } from 'react';
import { Calculator, AlertCircle, CheckCircle2, Info, ChevronDown, ChevronUp, Leaf } from 'lucide-react';
import { calculateProfit } from '../services/api';
import { translations } from '../data/i18n';

const PERISHABLE_IDS = ['tomato', 'banana', 'tapioca', 'green_chilli'];

const fmtINR = (val) =>
  val < 0
    ? `-₹${Math.abs(val).toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
    : `₹${val.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

export default function ProfitCalculatorPage({ commodities, markets, lang }) {
  const t = translations[lang] || translations.en;

  const [selectedCrop, setSelectedCrop] = useState('tomato');
  const [selectedMarket, setSelectedMarket] = useState('dindigul');
  const [volumeQuintals, setVolumeQuintals] = useState(50);
  const [cultivationCost, setCultivationCost] = useState(35000);
  const [transportPerQtl, setTransportPerQtl] = useState(60);
  const [loadingPerQtl, setLoadingPerQtl] = useState(20);
  const [commissionPct, setCommissionPct] = useState(2.0);
  const [wastagePct, setWastagePct] = useState(0);
  const [holdingDays, setHoldingDays] = useState(0);
  const [storageCostPerQtlWeek, setStorageCostPerQtlWeek] = useState(25);
  const [overridePrice, setOverridePrice] = useState('');

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAdvisory, setShowAdvisory] = useState(true);
  const [showBreakdown, setShowBreakdown] = useState(true);
  const [showAssumptions, setShowAssumptions] = useState(false);

  const isPerishable = PERISHABLE_IDS.includes(selectedCrop);

  const handleCalculate = useCallback(async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload = {
        commodity: selectedCrop,
        market: selectedMarket,
        quantity_quintals: Number(volumeQuintals),
        transport_cost_per_quintal: Number(transportPerQtl),
        loading_cost_per_quintal: Number(loadingPerQtl),
        commission_percent: Number(commissionPct),
        wastage_percent: Number(wastagePct),
        cultivation_cost_total: Number(cultivationCost),
        holding_days: Number(holdingDays),
        storage_cost_per_quintal_week: Number(storageCostPerQtlWeek),
      };
      if (overridePrice !== '') {
        payload.unit_price_per_kg = Number(overridePrice);
      }
      const data = await calculateProfit(payload);
      setResult(data);
      setShowAdvisory(true);
    } catch (err) {
      setError(err.message || 'Calculation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [selectedCrop, selectedMarket, volumeQuintals, cultivationCost, transportPerQtl,
      loadingPerQtl, commissionPct, wastagePct, holdingDays, storageCostPerQtlWeek, overridePrice]);

  const profitColor = result
    ? result.net_farmer_profit >= 0 ? '#15803d' : '#b91c1c'
    : 'var(--color-text-main)';

  return (
    <div>
      {/* Input Form */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header-bar">
          <div className="card-title-group">
            <div className="card-title-icon"><Calculator size={22} /></div>
            <div>
              <h3 className="card-title">
                {t.profitCalculatorTitle || 'Farmer Harvest Profit Calculator'}
              </h3>
              <p className="card-subtitle">
                Calculate itemised revenue, expenses, and net profit using verified mandi prices
              </p>
            </div>
          </div>
        </div>

        <form id="profit-calculator-form" onSubmit={handleCalculate}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Crop / Commodity</label>
              <select id="profit-crop" className="form-select" value={selectedCrop} onChange={(e) => setSelectedCrop(e.target.value)}>
                {commodities.map((c) => (
                  <option key={c.id} value={c.id}>{c.name_en} ({c.name_ta})</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Destination Mandi</label>
              <select id="profit-market" className="form-select" value={selectedMarket} onChange={(e) => setSelectedMarket(e.target.value)}>
                {markets.map((m) => (
                  <option key={m.id} value={m.id}>{m.district} — {m.market_name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Harvest Volume (Quintals)</label>
              <input id="profit-volume" type="number" className="form-input" value={volumeQuintals}
                onChange={(e) => setVolumeQuintals(Math.max(1, Number(e.target.value)))} min="1" step="1" />
            </div>

            <div className="form-group">
              <label className="form-label">Total Cultivation Cost (₹)</label>
              <input id="profit-cultivation" type="number" className="form-input" value={cultivationCost}
                onChange={(e) => setCultivationCost(Math.max(0, Number(e.target.value)))} min="0" step="500" />
            </div>

            <div className="form-group">
              <label className="form-label">Transport (₹/Quintal)</label>
              <input id="profit-transport" type="number" className="form-input" value={transportPerQtl}
                onChange={(e) => setTransportPerQtl(Math.max(0, Number(e.target.value)))} min="0" />
            </div>

            <div className="form-group">
              <label className="form-label">Loading / Hamali (₹/Quintal)</label>
              <input id="profit-loading" type="number" className="form-input" value={loadingPerQtl}
                onChange={(e) => setLoadingPerQtl(Math.max(0, Number(e.target.value)))} min="0" />
            </div>

            <div className="form-group">
              <label className="form-label">Mandi Commission (%)</label>
              <input id="profit-commission" type="number" className="form-input" value={commissionPct}
                onChange={(e) => setCommissionPct(Math.min(25, Math.max(0, Number(e.target.value))))} min="0" max="25" step="0.5" />
            </div>

            <div className="form-group">
              <label className="form-label">Post-Harvest Wastage (%)</label>
              <input id="profit-wastage" type="number" className="form-input" value={wastagePct}
                onChange={(e) => setWastagePct(Math.min(40, Math.max(0, Number(e.target.value))))} min="0" max="40" step="0.5" />
            </div>

            <div className="form-group">
              <label className="form-label">Holding Period (Days)</label>
              <select id="profit-holding" className="form-select" value={holdingDays} onChange={(e) => setHoldingDays(Number(e.target.value))}>
                <option value={0}>Immediate Sale (0 Days)</option>
                <option value={7}>Hold for 7 Days</option>
                <option value={15}>Hold for 15 Days</option>
                <option value={30}>Hold for 30 Days</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Storage Cost (₹/Quintal/Week)</label>
              <input id="profit-storage" type="number" className="form-input" value={storageCostPerQtlWeek}
                onChange={(e) => setStorageCostPerQtlWeek(Math.max(0, Number(e.target.value)))} min="0" />
            </div>

            <div className="form-group">
              <label className="form-label">
                Override Price (₹/kg) <span style={{ fontWeight: 400, color: 'var(--color-text-muted)' }}>– optional</span>
              </label>
              <input
                id="profit-override-price"
                type="number"
                className="form-input"
                placeholder="Uses latest mandi price if blank"
                value={overridePrice}
                onChange={(e) => setOverridePrice(e.target.value)}
                min="0.01"
                step="0.5"
              />
            </div>
          </div>

          {/* Perishability Warning */}
          {isPerishable && holdingDays > 5 && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '10px',
              marginTop: '12px', padding: '12px 16px',
              background: '#fff7ed', border: '1px solid #fed7aa',
              borderRadius: '8px', color: '#9a3412', fontSize: '0.85rem',
            }}>
              <AlertCircle size={18} />
              <span>
                <strong>Perishability Risk:</strong> {selectedCrop.replace(/_/g, ' ')} is a highly perishable crop.
                Holding for {holdingDays} days without cold-chain storage carries significant post-harvest loss risk.
              </span>
            </div>
          )}

          <button
            id="profit-calculate-btn"
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ marginTop: '20px', opacity: loading ? 0.7 : 1 }}
          >
            {loading ? 'Calculating…' : '📊 Calculate Profit & Revenue'}
          </button>
        </form>
      </div>

      {error && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '14px 18px', background: '#fef2f2', border: '1px solid #fecaca',
          borderRadius: '10px', color: '#b91c1c', fontSize: '0.88rem', marginBottom: '20px',
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Price Source Banner */}
          <div style={{
            padding: '10px 16px', marginBottom: '20px',
            background: '#f0fdf4', border: '1px solid #bbf7d0',
            borderRadius: '8px', fontSize: '0.82rem', color: '#166534',
            display: 'flex', alignItems: 'center', gap: '8px',
          }}>
            <Info size={14} />
            Price used: <strong>₹{result.applied_modal_price_per_kg?.toFixed(2)}/kg</strong>
            ({result.applied_modal_price_per_quintal?.toLocaleString('en-IN')}/Quintal) —
            {result.price_type} as of <strong>{result.price_source_date}</strong>
          </div>

          {/* Perishability Warning from backend */}
          {result.perishability_warning && (
            <div style={{
              display: 'flex', alignItems: 'flex-start', gap: '10px',
              padding: '12px 16px', marginBottom: '20px',
              background: '#fff7ed', border: '1px solid #fed7aa',
              borderRadius: '8px', color: '#9a3412', fontSize: '0.85rem',
            }}>
              <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>{result.perishability_warning}</span>
            </div>
          )}

          {/* Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{ background: 'linear-gradient(135deg, #166534, #16a34a)', borderRadius: '12px', padding: '20px', color: '#fff' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, opacity: 0.8, textTransform: 'uppercase' }}>Gross Revenue</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '6px' }}>{fmtINR(result.gross_revenue)}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.85, marginTop: '4px' }}>
                {result.salable_quantity_kg?.toFixed(0)} kg @ ₹{result.applied_modal_price_per_kg?.toFixed(2)}/kg
              </div>
            </div>

            <div style={{ background: 'linear-gradient(135deg, #7f1d1d, #b91c1c)', borderRadius: '12px', padding: '20px', color: '#fff' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, opacity: 0.8, textTransform: 'uppercase' }}>Total Expenses</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '6px' }}>{fmtINR(result.total_marketing_expenses + result.cultivation_cost_total)}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.85, marginTop: '4px' }}>
                Marketing + Cultivation
              </div>
            </div>

            <div style={{
              background: result.net_farmer_profit >= 0
                ? 'linear-gradient(135deg, #1e3a5f, #1d4ed8)'
                : 'linear-gradient(135deg, #431407, #c2410c)',
              borderRadius: '12px',
              padding: '20px',
              color: '#fff',
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, opacity: 0.8, textTransform: 'uppercase' }}>Net Farmer Profit</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '6px' }}>{fmtINR(result.net_farmer_profit)}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.85, marginTop: '4px' }}>
                {result.profit_margin_pct?.toFixed(1)}% margin on gross revenue
              </div>
            </div>
          </div>

          {/* Detailed Breakdown */}
          <div className="card" style={{ marginBottom: '20px' }}>
            <button
              id="profit-breakdown-toggle"
              onClick={() => setShowBreakdown((v) => !v)}
              style={{
                width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                padding: '0 0 12px', display: 'flex', justifyContent: 'space-between',
                alignItems: 'center', fontWeight: 700, fontSize: '0.95rem',
                color: 'var(--color-primary-dark)',
              }}
            >
              <span>📋 Itemised Revenue & Expense Breakdown</span>
              {showBreakdown ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>

            {showBreakdown && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.88rem' }}>
                {/* Quantity section */}
                <div style={{ padding: '8px 0', borderBottom: '1px dashed var(--color-surface-border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Total Harvest</span>
                    <span>{result.quantity_quintals} Quintals ({result.total_volume_kg?.toFixed(0)} kg)</span>
                  </div>
                  {result.wastage_percent > 0 && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#b45309' }}>
                      <span>Wastage ({result.wastage_percent}%)</span>
                      <span>− {result.wastage_loss_quintals?.toFixed(2)} Qtl</span>
                    </div>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700 }}>
                    <span>Salable Quantity</span>
                    <span>{result.salable_quantity_quintals?.toFixed(2)} Qtl ({result.salable_quantity_kg?.toFixed(0)} kg)</span>
                  </div>
                </div>

                {/* Revenue */}
                <div style={{ display: 'flex', justifyContent: 'space-between', color: '#166534', fontWeight: 600 }}>
                  <span>+ Gross Revenue</span>
                  <span>{fmtINR(result.gross_revenue)}</span>
                </div>

                {/* Expenses */}
                <div style={{ display: 'flex', justifyContent: 'space-between', color: '#b91c1c' }}>
                  <span>− Transport Expenses</span>
                  <span>{fmtINR(result.transport_expenses)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', color: '#b91c1c' }}>
                  <span>− Loading / Hamali</span>
                  <span>{fmtINR(result.loading_expenses)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', color: '#b91c1c' }}>
                  <span>− Mandi Commission ({result.mandi_commission_fee > 0 ? commissionPct + '%' : '0%'})</span>
                  <span>{fmtINR(result.mandi_commission_fee)}</span>
                </div>
                {result.storage_expenses > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#b91c1c' }}>
                    <span>− Storage Cost ({holdingDays} days)</span>
                    <span>{fmtINR(result.storage_expenses)}</span>
                  </div>
                )}
                <div style={{ display: 'flex', justifyContent: 'space-between', color: '#b91c1c', borderTop: '1px dashed var(--color-surface-border)', paddingTop: '8px', fontWeight: 600 }}>
                  <span>Total Marketing Expenses</span>
                  <span>{fmtINR(result.total_marketing_expenses)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Net Revenue (after marketing)</span>
                  <span style={{ fontWeight: 700 }}>{fmtINR(result.estimated_net_revenue)}</span>
                </div>
                {result.cultivation_cost_total > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#b91c1c' }}>
                    <span>− Cultivation Cost</span>
                    <span>{fmtINR(result.cultivation_cost_total)}</span>
                  </div>
                )}
                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  borderTop: '2px solid var(--color-surface-border)', paddingTop: '10px',
                  fontWeight: 800, fontSize: '1rem', color: profitColor,
                }}>
                  <span>Net Farmer Profit</span>
                  <span>{fmtINR(result.net_farmer_profit)} ({result.profit_margin_pct?.toFixed(1)}%)</span>
                </div>
              </div>
            )}
          </div>

          {/* Advisory */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{
              background: result.net_farmer_profit >= 0 ? '#f0fdf4' : '#fff7ed',
              border: `1px solid ${result.net_farmer_profit >= 0 ? '#86efac' : '#fed7aa'}`,
              borderRadius: '10px',
              overflow: 'hidden',
            }}>
              <button
                id="profit-advisory-toggle"
                onClick={() => setShowAdvisory((v) => !v)}
                style={{
                  width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                  padding: '12px 18px',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  fontWeight: 700, fontSize: '0.9rem',
                  color: result.net_farmer_profit >= 0 ? '#166534' : '#9a3412',
                }}
              >
                <span>
                  {result.net_farmer_profit >= 0 ? '✅' : '⚠️'}{' '}
                  {lang === 'ta' ? 'விளைவு ஆலோசனை' : 'Profit Advisory'}
                </span>
                {showAdvisory ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>
              {showAdvisory && (
                <div style={{
                  padding: '0 18px 16px',
                  fontSize: '0.88rem',
                  color: result.net_farmer_profit >= 0 ? '#14532d' : '#7c2d12',
                  lineHeight: '1.65',
                }}>
                  {lang === 'ta' ? result.advisory_ta : result.advisory_en}
                </div>
              )}
            </div>
          </div>

          {/* Assumptions */}
          <button
            id="profit-assumptions-toggle"
            onClick={() => setShowAssumptions((v) => !v)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: '0.8rem', color: 'var(--color-text-muted)',
              display: 'flex', alignItems: 'center', gap: '6px', padding: '4px 0',
            }}
          >
            <Info size={13} />
            {showAssumptions ? 'Hide' : 'Show'} Calculation Assumptions & Limitations
            {showAssumptions ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>
          {showAssumptions && (
            <div style={{
              marginTop: '8px', padding: '14px 18px',
              background: '#f8fafc', border: '1px solid var(--color-surface-border)',
              borderRadius: '8px', fontSize: '0.8rem', color: 'var(--color-text-muted)', lineHeight: '1.6',
            }}>
              <strong style={{ color: 'var(--color-text-main)', display: 'block', marginBottom: '8px' }}>Assumptions:</strong>
              <ul style={{ margin: 0, paddingLeft: '18px' }}>
                {(result.assumptions || []).map((a, i) => <li key={i}>{a}</li>)}
              </ul>
              <strong style={{ color: 'var(--color-text-main)', display: 'block', margin: '10px 0 6px' }}>Limitations:</strong>
              <p style={{ margin: 0 }}>{result.forecast_limitations}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
