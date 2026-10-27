import React from 'react';
import { translations } from '../data/i18n';

const COMMODITY_ICONS = {
  tomato: '🍅',
  small_onion: '🧅',
  bellary_onion: '🧅',
  potato: '🥔',
  coconut: '🥥',
  banana: '🍌',
  turmeric: '🟡',
  paddy: '🌾',
  green_chilli: '🌶️',
  tapioca: '🍠',
};

export default function CommodityGrid({ commodities, selectedCommodity, onSelectCommodity, lang }) {
  const t = translations[lang] || translations.en;

  return (
    <div style={{ marginBottom: '24px' }}>
      <div style={{ marginBottom: '12px' }}>
        <h3 style={{ fontSize: '1.15rem', color: 'var(--color-primary-dark)', fontWeight: 700 }}>
          {t.selectCommodityTitle}
        </h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>
          {t.selectCommoditySub}
        </p>
      </div>

      <div className="commodity-scroll-grid">
        {commodities.map((comm) => {
          const isSelected = selectedCommodity === comm.id;
          const icon = COMMODITY_ICONS[comm.id] || '🌱';
          const modalRate = comm.typical_price_range_per_kg?.modal || 30;

          return (
            <div
              key={comm.id}
              className={`commodity-chip ${isSelected ? 'active' : ''}`}
              onClick={() => onSelectCommodity(comm.id)}
            >
              <span className="commodity-chip-icon">{icon}</span>
              <span className="commodity-chip-name">{comm.name_en}</span>
              <span className="commodity-chip-ta">{comm.name_ta}</span>
              <span className="commodity-chip-price">₹{modalRate}/kg</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
