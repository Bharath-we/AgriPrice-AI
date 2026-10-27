import React from 'react';
import { Store, Award, ArrowRight } from 'lucide-react';
import { translations } from '../data/i18n';

export default function MarketInsights({ marketSummary, selectedMarket, onSelectMarket, lang }) {
  const t = translations[lang] || translations.en;

  if (!marketSummary || marketSummary.length === 0) return null;

  const highestPrice = marketSummary[0]?.price_per_kg || 0;

  return (
    <div className="card" style={{ marginTop: '24px' }}>
      <div className="card-header-bar">
        <div className="card-title-group">
          <div className="card-title-icon">
            <Store size={22} />
          </div>
          <div>
            <h3 className="card-title">{t.marketComparisonTitle}</h3>
            <p className="card-subtitle">{t.marketComparisonSub}</p>
          </div>
        </div>
      </div>

      <div className="market-table-wrap">
        <table className="market-table">
          <thead>
            <tr>
              <th>District</th>
              <th>APMC / Regulated Mandi</th>
              <th>Price (₹ / kg)</th>
              <th>Modal (₹ / Qtl)</th>
              <th>Avg Arrival</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {marketSummary.map((item, index) => {
              const isSelected = selectedMarket === item.market_id;
              const isTop = index === 0;

              return (
                <tr
                  key={item.market_id}
                  style={{
                    backgroundColor: isSelected ? 'var(--color-mint-bg)' : undefined,
                    fontWeight: isSelected ? 600 : 400,
                  }}
                >
                  <td style={{ fontWeight: 700, color: 'var(--color-primary-dark)' }}>
                    {item.district}
                  </td>
                  <td>
                    {item.market_name}
                    {isTop && <span className="best-price-badge">HIGHEST RETURN</span>}
                  </td>
                  <td style={{ fontWeight: 700, color: 'var(--color-primary-accent)' }}>
                    ₹{item.price_per_kg.toFixed(2)}
                  </td>
                  <td>₹{item.modal_price_per_quintal.toLocaleString('en-IN')}</td>
                  <td>{item.avg_arrival_quintals} Qtl</td>
                  <td>
                    <button
                      onClick={() => onSelectMarket(item.market_id)}
                      style={{
                        background: isSelected ? 'var(--color-primary)' : '#e8f5e9',
                        color: isSelected ? '#ffffff' : 'var(--color-primary-dark)',
                        border: 'none',
                        padding: '4px 10px',
                        borderRadius: '14px',
                        cursor: 'pointer',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      {isSelected ? 'Active Mandi' : 'Select'}
                      {!isSelected && <ArrowRight size={12} />}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
