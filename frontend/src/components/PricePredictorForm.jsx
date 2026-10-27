import React from 'react';
import { Calendar, MapPin, TrendingUp, CloudRain, Package, Cpu, Clock } from 'lucide-react';
import { translations } from '../data/i18n';

export default function PricePredictorForm({
  commodities,
  markets,
  formData,
  setFormData,
  onSubmit,
  loading,
  lang,
}) {
  const t = translations[lang] || translations.en;

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const setHorizonDays = (days) => {
    const target = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    setFormData((prev) => ({ ...prev, targetDate: target }));
  };

  // Compute selected horizon in days
  const today = new Date();
  const selectedDate = new Date(formData.targetDate);
  const diffDays = Math.max(1, Math.round((selectedDate - today) / (1000 * 60 * 60 * 24)));

  return (
    <div className="card">
      <div className="card-header-bar">
        <div className="card-title-group">
          <div className="card-title-icon">
            <Cpu size={22} />
          </div>
          <div>
            <h2 className="card-title">{t.predictorTitle}</h2>
            <p className="card-subtitle">{t.predictorSub}</p>
          </div>
        </div>
      </div>

      <form onSubmit={onSubmit}>
        {/* Commodity Select */}
        <div className="form-group">
          <label className="form-label">{t.commodityLabel}</label>
          <select
            className="form-select"
            value={formData.commodity}
            onChange={(e) => handleChange('commodity', e.target.value)}
          >
            {commodities.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name_en} ({c.name_ta})
              </option>
            ))}
          </select>
        </div>

        {/* Market Select */}
        <div className="form-group">
          <label className="form-label">{t.marketLabel}</label>
          <select
            className="form-select"
            value={formData.market}
            onChange={(e) => handleChange('market', e.target.value)}
          >
            {markets.map((m) => (
              <option key={m.id} value={m.id}>
                {m.district} - {m.market_name}
              </option>
            ))}
          </select>
        </div>

        {/* Forecast Horizon Preset Pills */}
        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={15} />
            <span>Forecast Horizon: ~{diffDays} Days Ahead</span>
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '8px' }}>
            <button
              type="button"
              onClick={() => setHorizonDays(7)}
              style={{
                padding: '8px 4px',
                borderRadius: '8px',
                border: '1.5px solid var(--color-surface-border)',
                background: diffDays <= 10 ? 'var(--color-primary-light)' : '#ffffff',
                color: diffDays <= 10 ? '#ffffff' : 'var(--color-text-main)',
                fontWeight: 700,
                fontSize: '0.82rem',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              7-Day (Verified)
            </button>
            <button
              type="button"
              onClick={() => setHorizonDays(15)}
              style={{
                padding: '8px 4px',
                borderRadius: '8px',
                border: '1.5px solid var(--color-surface-border)',
                background: diffDays > 10 && diffDays <= 22 ? 'var(--color-primary-light)' : '#ffffff',
                color: diffDays > 10 && diffDays <= 22 ? '#ffffff' : 'var(--color-text-main)',
                fontWeight: 700,
                fontSize: '0.82rem',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              15-Day Mid
            </button>
            <button
              type="button"
              onClick={() => setHorizonDays(30)}
              style={{
                padding: '8px 4px',
                borderRadius: '8px',
                border: '1.5px solid var(--color-surface-border)',
                background: diffDays > 22 ? 'var(--color-primary-light)' : '#ffffff',
                color: diffDays > 22 ? '#ffffff' : 'var(--color-text-main)',
                fontWeight: 700,
                fontSize: '0.82rem',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              30-Day Long
            </button>
          </div>
        </div>

        {/* Date Input */}
        <div className="form-group">
          <label className="form-label">{t.dateLabel}</label>
          <div style={{ position: 'relative' }}>
            <input
              type="date"
              className="form-input"
              value={formData.targetDate}
              onChange={(e) => handleChange('targetDate', e.target.value)}
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>

        {/* Arrival Volume Slider */}
        <div className="form-group">
          <label className="form-label">{t.arrivalLabel}</label>
          <div className="range-slider-wrapper">
            <div className="range-slider-header">
              <span>Market Supply Influx</span>
              <span className="range-val">{formData.arrivalVolume} Quintals</span>
            </div>
            <input
              type="range"
              className="form-range"
              min="150"
              max="2800"
              step="50"
              value={formData.arrivalVolume}
              onChange={(e) => handleChange('arrivalVolume', Number(e.target.value))}
            />
            <p className="form-hint">{t.arrivalHint}</p>
          </div>
        </div>

        {/* Rainfall / Monsoon Condition */}
        <div className="form-group">
          <label className="form-label">{t.weatherLabel}</label>
          <select
            className="form-select"
            value={formData.rainfallFactor}
            onChange={(e) => handleChange('rainfallFactor', parseFloat(e.target.value))}
          >
            <option value="1.0">{t.weatherNormal}</option>
            <option value="1.4">{t.weatherMonsoon}</option>
            <option value="0.8">{t.weatherDrought}</option>
          </select>
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? (
            <>
              <div className="status-dot" style={{ background: '#ffffff' }}></div>
              <span>{t.predicting}</span>
            </>
          ) : (
            <>
              <TrendingUp size={18} />
              <span>{t.predictBtn}</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
