import React, { useState, useEffect, useCallback } from 'react';
import { BellRing, Plus, Trash2, RefreshCw, CheckCircle2, Clock, AlertTriangle, Info } from 'lucide-react';
import { fetchAlerts, createAlert, deleteAlert } from '../services/api';
import { translations } from '../data/i18n';

const CONDITION_OPTIONS = [
  { value: 'GREATER_THAN_OR_EQUAL', label_en: 'Price ≥ target (rises to or above)', label_ta: 'விலை ≥ இலக்கு (உயரும்போது)' },
  { value: 'LESS_THAN_OR_EQUAL', label_en: 'Price ≤ target (drops to or below)', label_ta: 'விலை ≤ இலக்கு (இறங்கும்போது)' },
];

const statusStyle = (alert) => {
  if (alert.is_triggered) return { bg: '#fef3c7', border: '#fde68a', badge: '#b45309', badgeBg: '#fef3c7' };
  return { bg: '#ffffff', border: 'var(--color-surface-border)', badge: '#166534', badgeBg: '#dcfce7' };
};

export default function PriceAlertsPage({ commodities, markets, lang }) {
  const t = translations[lang] || translations.en;

  const [alertsData, setAlertsData] = useState(null); // full PriceAlertCheckResponse
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [createError, setCreateError] = useState(null);
  const [feedback, setFeedback] = useState(null);

  // Form state
  const [crop, setCrop] = useState('tomato');
  const [market, setMarket] = useState('dindigul');
  const [condition, setCondition] = useState('GREATER_THAN_OR_EQUAL');
  const [targetPrice, setTargetPrice] = useState('');

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await fetchAlerts();
      setAlertsData(data);
    } catch (e) {
      setLoadError(e.message || 'Failed to load alerts. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  const handleCreate = async (e) => {
    e.preventDefault();
    const priceVal = Number(targetPrice);
    if (!targetPrice || isNaN(priceVal) || priceVal <= 0) {
      setCreateError('Please enter a valid positive target price (₹/kg).');
      return;
    }
    setSubmitting(true);
    setCreateError(null);
    try {
      await createAlert({
        commodity: crop,
        market: market,
        condition: condition,
        target_price_per_kg: priceVal,
      });
      setTargetPrice('');
      setFeedback('✅ Alert created and evaluated against current mandi prices.');
      setTimeout(() => setFeedback(null), 4000);
      await loadAlerts(); // Refresh
    } catch (e) {
      setCreateError(e.message || 'Failed to create alert.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (alertId) => {
    try {
      await deleteAlert(alertId);
      setFeedback('Alert deleted.');
      setTimeout(() => setFeedback(null), 2500);
      await loadAlerts();
    } catch (e) {
      setFeedback(`Delete failed: ${e.message}`);
      setTimeout(() => setFeedback(null), 3000);
    }
  };

  const alerts = alertsData?.alerts || [];
  const triggeredCount = alertsData?.triggered_alerts_count || 0;

  return (
    <div>
      {/* Header & Create Form */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header-bar">
          <div className="card-title-group">
            <div className="card-title-icon"><BellRing size={22} /></div>
            <div>
              <h3 className="card-title">{t.priceAlertsTitle || 'Price Target Alerts'}</h3>
              <p className="card-subtitle">
                Set price thresholds — alerts trigger when verified APMC mandi prices meet your condition.
                In-app notification only. SMS/Email delivery is <strong>not</strong> configured.
              </p>
            </div>
          </div>

          <button
            id="alerts-refresh-btn"
            onClick={loadAlerts}
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
            <RefreshCw size={14} />
            {loading ? 'Scanning…' : 'Scan Mandi Prices'}
          </button>
        </div>

        {/* Summary badges */}
        {alertsData && (
          <div style={{ display: 'flex', gap: '12px', marginBottom: '18px', flexWrap: 'wrap' }}>
            <div style={{
              padding: '6px 14px', borderRadius: '20px',
              background: '#f0fdf4', border: '1px solid #86efac',
              fontSize: '0.82rem', fontWeight: 700, color: '#166534',
            }}>
              {alerts.length} Alert{alerts.length !== 1 ? 's' : ''} Saved
            </div>
            {triggeredCount > 0 && (
              <div style={{
                padding: '6px 14px', borderRadius: '20px',
                background: '#fef3c7', border: '1px solid #fde68a',
                fontSize: '0.82rem', fontWeight: 700, color: '#b45309',
                display: 'flex', alignItems: 'center', gap: '6px',
              }}>
                <BellRing size={12} />
                {triggeredCount} Triggered!
              </div>
            )}
            <div style={{
              padding: '6px 14px', borderRadius: '20px',
              background: '#f8fafc', border: '1px solid var(--color-surface-border)',
              fontSize: '0.78rem', color: 'var(--color-text-muted)',
            }}>
              Last scanned: {alertsData.audit_timestamp ? new Date(alertsData.audit_timestamp).toLocaleTimeString() : '—'}
            </div>
          </div>
        )}

        {/* Feedback */}
        {feedback && (
          <div style={{
            background: feedback.includes('failed') || feedback.includes('Delete failed') ? '#fef2f2' : '#dcfce7',
            border: `1px solid ${feedback.includes('failed') ? '#fecaca' : '#86efac'}`,
            color: feedback.includes('failed') ? '#b91c1c' : '#15803d',
            padding: '10px 14px', borderRadius: '8px',
            fontSize: '0.85rem', marginBottom: '14px', fontWeight: 600,
          }}>
            {feedback}
          </div>
        )}

        {/* Create Alert Form */}
        <form id="create-alert-form" onSubmit={handleCreate}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', alignItems: 'flex-end' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Crop</label>
              <select id="alert-crop" className="form-select" value={crop} onChange={(e) => setCrop(e.target.value)}>
                {commodities.map((c) => (
                  <option key={c.id} value={c.id}>{c.name_en}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Mandi</label>
              <select id="alert-market" className="form-select" value={market} onChange={(e) => setMarket(e.target.value)}>
                {markets.map((m) => (
                  <option key={m.id} value={m.id}>{m.district}</option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Condition</label>
              <select id="alert-condition" className="form-select" value={condition} onChange={(e) => setCondition(e.target.value)}>
                {CONDITION_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {lang === 'ta' ? opt.label_ta : opt.label_en}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Target Price (₹/kg)</label>
              <input
                id="alert-target-price"
                type="number"
                className="form-input"
                value={targetPrice}
                onChange={(e) => { setTargetPrice(e.target.value); setCreateError(null); }}
                placeholder="e.g. 35.00"
                step="0.5"
                min="0.01"
              />
            </div>

            <button
              id="alert-create-btn"
              type="submit"
              className="btn-primary"
              style={{ height: '45px' }}
              disabled={submitting}
            >
              {submitting ? (
                <span>Saving…</span>
              ) : (
                <><Plus size={16} /> <span>Add Alert</span></>
              )}
            </button>
          </div>

          {createError && (
            <div style={{
              marginTop: '10px', padding: '8px 14px',
              background: '#fef2f2', border: '1px solid #fecaca',
              borderRadius: '7px', color: '#b91c1c', fontSize: '0.83rem',
              display: 'flex', alignItems: 'center', gap: '8px',
            }}>
              <AlertTriangle size={14} /> {createError}
            </div>
          )}
        </form>
      </div>

      {/* Alerts List */}
      <div className="card">
        <div className="card-header-bar">
          <h3 className="card-title">
            Active Alert Monitors ({alerts.length})
          </h3>
          {triggeredCount > 0 && (
            <span style={{
              fontSize: '0.8rem', fontWeight: 700, padding: '4px 12px',
              borderRadius: '14px', background: '#fef3c7', color: '#b45309',
              border: '1px solid #fde68a',
            }}>
              {triggeredCount} triggered
            </span>
          )}
        </div>

        {/* Load error */}
        {loadError && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '14px', background: '#fef2f2', border: '1px solid #fecaca',
            borderRadius: '8px', color: '#b91c1c', fontSize: '0.85rem', marginBottom: '16px',
          }}>
            <AlertTriangle size={16} /> {loadError}
          </div>
        )}

        {/* Loading */}
        {loading && !alertsData && (
          <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
            <RefreshCw size={20} style={{ margin: '0 auto 10px', display: 'block', opacity: 0.4 }} />
            Scanning mandi prices for alerts…
          </div>
        )}

        {/* Empty */}
        {!loading && alerts.length === 0 && !loadError && (
          <div style={{ textAlign: 'center', padding: '36px', color: 'var(--color-text-muted)' }}>
            <BellRing size={28} style={{ margin: '0 auto 10px', display: 'block', opacity: 0.3 }} />
            <p>No price alerts configured yet.</p>
            <p style={{ fontSize: '0.82rem' }}>Add your first threshold above to monitor mandi prices.</p>
          </div>
        )}

        {/* Alert Items */}
        {alerts.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {alerts.map((alert) => {
              const styles = statusStyle(alert);
              const condLabel = CONDITION_OPTIONS.find((o) => o.value === alert.condition);
              return (
                <div
                  key={alert.id}
                  style={{
                    padding: '16px 18px',
                    borderRadius: '10px',
                    border: `1px solid ${styles.border}`,
                    background: styles.bg,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                    {/* Left Info */}
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', flex: 1 }}>
                      <BellRing size={20} color={alert.is_triggered ? '#b45309' : 'var(--color-primary)'} style={{ marginTop: '2px', flexShrink: 0 }} />
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--color-primary-dark)' }}>
                          {alert.commodity_name_en}
                          <span style={{ fontWeight: 400, fontSize: '0.85rem', color: 'var(--color-text-muted)', marginLeft: '8px' }}>
                            {alert.commodity_name_ta}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.83rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                          {alert.market_name_en} · Target:{' '}
                          <strong style={{ color: 'var(--color-text-main)' }}>
                            {lang === 'ta'
                              ? (condLabel?.label_ta || alert.condition)
                              : (condLabel?.label_en || alert.condition)}{' '}
                            ₹{alert.target_price_per_kg?.toFixed(2)}/kg
                          </strong>
                        </div>

                        {/* Current Price */}
                        {alert.current_mandi_price_per_kg > 0 && (
                          <div style={{ fontSize: '0.82rem', marginTop: '4px', color: 'var(--color-text-muted)' }}>
                            Current mandi price:{' '}
                            <strong style={{ color: 'var(--color-primary-dark)' }}>
                              ₹{alert.current_mandi_price_per_kg?.toFixed(2)}/kg
                            </strong>
                            {' '}(as of {alert.observation_date || '—'})
                          </div>
                        )}

                        {/* In-App Message */}
                        <div style={{
                          marginTop: '8px',
                          padding: '8px 12px',
                          background: alert.is_triggered ? '#fef9c3' : '#f0fdf4',
                          border: `1px solid ${alert.is_triggered ? '#fde047' : '#bbf7d0'}`,
                          borderRadius: '7px',
                          fontSize: '0.8rem',
                          color: alert.is_triggered ? '#713f12' : '#166534',
                          lineHeight: '1.55',
                        }}>
                          {lang === 'ta' ? alert.in_app_message_ta : alert.in_app_message_en}
                        </div>

                        {/* Disclaimer */}
                        <div style={{ marginTop: '6px', fontSize: '0.72rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '5px' }}>
                          <Info size={11} /> {alert.disclaimer}
                        </div>
                      </div>
                    </div>

                    {/* Right: Status + Delete */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '10px', flexShrink: 0 }}>
                      <span style={{
                        fontSize: '0.72rem', fontWeight: 800,
                        padding: '4px 10px', borderRadius: '12px',
                        background: styles.badgeBg, color: styles.badge,
                        border: `1px solid ${styles.border}`,
                      }}>
                        {alert.is_triggered ? '🔔 TRIGGERED' : '⏳ WATCHING'}
                      </span>
                      <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textAlign: 'right' }}>
                        Set {new Date(alert.created_at).toLocaleDateString()}
                        {alert.triggered_at && (
                          <div>Triggered {new Date(alert.triggered_at).toLocaleTimeString()}</div>
                        )}
                      </div>
                      <button
                        id={`alert-delete-${alert.id}`}
                        onClick={() => handleDelete(alert.id)}
                        style={{
                          background: 'none', border: 'none',
                          color: '#94a3b8', cursor: 'pointer', padding: '4px',
                        }}
                        title="Delete Alert"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Disclaimer footer */}
        <div style={{
          marginTop: '20px', padding: '10px 14px',
          background: '#f8fafc', borderRadius: '8px',
          fontSize: '0.75rem', color: 'var(--color-text-muted)',
          display: 'flex', alignItems: 'center', gap: '8px',
        }}>
          <Info size={13} />
          Alerts are checked against the latest verified APMC mandi observation records.
          Trigger evaluation uses real historical transaction data — not AI forecasts.
          <strong>SMS/Email delivery is not available.</strong> Alerts are persisted on the backend server.
        </div>
      </div>
    </div>
  );
}
