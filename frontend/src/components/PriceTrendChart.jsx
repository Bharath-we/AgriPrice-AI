import React, { useState } from 'react';
import { LineChart as ChartIcon } from 'lucide-react';
import { translations } from '../data/i18n';

export default function PriceTrendChart({ historicalData, prediction, lang }) {
  const t = translations[lang] || translations.en;
  const [activeTooltip, setActiveTooltip] = useState(null);

  const series = historicalData?.data || [];

  if (series.length === 0 && !prediction) {
    return null;
  }

  // Combine historical prices with predicted target point
  const prices = series.map((d) => d.price_per_kg);
  if (prediction?.predicted_price_per_kg) {
    prices.push(prediction.predicted_price_per_kg);
    prices.push(prediction.confidence_upper_per_kg);
    prices.push(prediction.confidence_lower_per_kg);
  }

  const minPrice = Math.floor(Math.min(...(prices.length ? prices : [20])) * 0.88);
  const maxPrice = Math.ceil(Math.max(...(prices.length ? prices : [50])) * 1.12);
  const priceRange = maxPrice - minPrice || 1;

  // Chart dimensions
  const width = 760;
  const height = 200;
  const paddingX = 40;
  const paddingY = 25;
  const chartW = width - paddingX * 2;
  const chartH = height - paddingY * 2;

  // Calculate coordinates for historical points
  const totalCount = series.length + (prediction ? 1 : 0);
  const points = series.map((item, idx) => {
    const x = paddingX + (idx / (totalCount - 1 || 1)) * chartW;
    const y = paddingY + chartH - ((item.price_per_kg - minPrice) / priceRange) * chartH;
    return { ...item, x, y };
  });

  // Calculate prediction target point
  let predPoint = null;
  let predUpperY = null;
  let predLowerY = null;
  if (prediction) {
    const x = paddingX + chartW;
    const y = paddingY + chartH - ((prediction.predicted_price_per_kg - minPrice) / priceRange) * chartH;
    predUpperY = paddingY + chartH - ((prediction.confidence_upper_per_kg - minPrice) / priceRange) * chartH;
    predLowerY = paddingY + chartH - ((prediction.confidence_lower_per_kg - minPrice) / priceRange) * chartH;
    predPoint = {
      date: prediction.target_date,
      price_per_kg: prediction.predicted_price_per_kg,
      arrival_quantity_quintals: prediction.estimated_arrival_quintals,
      x,
      y,
      isPrediction: true,
    };
  }

  // Construct SVG paths
  const linePath = points.reduce((acc, pt, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${pt.x} ${pt.y}`, '');
  const areaPath = points.length > 0
    ? `${linePath} L ${points[points.length - 1].x} ${paddingY + chartH} L ${points[0].x} ${paddingY + chartH} Z`
    : '';

  // Projection dotted path
  const lastHistPoint = points[points.length - 1];
  const projectionPath = lastHistPoint && predPoint
    ? `M ${lastHistPoint.x} ${lastHistPoint.y} L ${predPoint.x} ${predPoint.y}`
    : '';

  return (
    <div className="card" style={{ marginTop: '24px' }}>
      <div className="card-header-bar">
        <div className="card-title-group">
          <div className="card-title-icon">
            <ChartIcon size={22} />
          </div>
          <div>
            <h3 className="card-title">{t.chartTitle}</h3>
            <p className="card-subtitle">{t.chartSub}</p>
          </div>
        </div>
      </div>

      <div className="chart-container" style={{ position: 'relative' }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="chart-svg"
          onMouseLeave={() => setActiveTooltip(null)}
        >
          <defs>
            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#52b788" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#52b788" stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 0.33, 0.66, 1].map((pct, i) => {
            const y = paddingY + chartH * (1 - pct);
            const val = minPrice + priceRange * pct;
            return (
              <g key={i}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={width - paddingX}
                  y2={y}
                  stroke="#e2ebe2"
                  strokeDasharray="4 4"
                />
                <text
                  x={paddingX - 8}
                  y={y + 4}
                  fill="#738a79"
                  fontSize="11"
                  textAnchor="end"
                  fontFamily="Outfit, sans-serif"
                >
                  ₹{Math.round(val)}
                </text>
              </g>
            );
          })}

          {/* Shaded Area */}
          {areaPath && <path d={areaPath} fill="url(#chartGradient)" />}

          {/* Historical Line */}
          {linePath && (
            <path
              d={linePath}
              fill="none"
              stroke="#2d6a4f"
              strokeWidth="2.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Projection Line to Forecast Date */}
          {projectionPath && (
            <path
              d={projectionPath}
              fill="none"
              stroke="#e67e22"
              strokeWidth="2.4"
              strokeDasharray="6 6"
            />
          )}

          {/* Confidence interval whisker on target prediction */}
          {predPoint && predUpperY !== null && predLowerY !== null && (
            <g>
              <line
                x1={predPoint.x}
                y1={predUpperY}
                x2={predPoint.x}
                y2={predLowerY}
                stroke="#e67e22"
                strokeWidth="2"
                strokeOpacity="0.6"
              />
              <line
                x1={predPoint.x - 5}
                y1={predUpperY}
                x2={predPoint.x + 5}
                y2={predUpperY}
                stroke="#e67e22"
                strokeWidth="2"
              />
              <line
                x1={predPoint.x - 5}
                y1={predLowerY}
                x2={predPoint.x + 5}
                y2={predLowerY}
                stroke="#e67e22"
                strokeWidth="2"
              />
            </g>
          )}

          {/* Interactive Data Points */}
          {points.map((pt, idx) => (
            <circle
              key={idx}
              cx={pt.x}
              cy={pt.y}
              r="3.5"
              fill="#ffffff"
              stroke="#2d6a4f"
              strokeWidth="2"
              style={{ cursor: 'pointer' }}
              onMouseEnter={() => setActiveTooltip(pt)}
            />
          ))}

          {/* Prediction Point Circle */}
          {predPoint && (
            <circle
              cx={predPoint.x}
              cy={predPoint.y}
              r="6"
              fill="#e67e22"
              stroke="#ffffff"
              strokeWidth="2.5"
              style={{ cursor: 'pointer' }}
              onMouseEnter={() => setActiveTooltip(predPoint)}
            />
          )}
        </svg>

        {/* Hover Tooltip */}
        {activeTooltip && (
          <div
            style={{
              position: 'absolute',
              left: `${(activeTooltip.x / width) * 100}%`,
              top: `${(activeTooltip.y / height) * 100}%`,
              transform: 'translate(-50%, -125%)',
              background: '#0f3823',
              color: '#ffffff',
              padding: '6px 12px',
              borderRadius: '8px',
              fontSize: '0.8rem',
              fontWeight: 600,
              pointerEvents: 'none',
              boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
              whiteSpace: 'nowrap',
              zIndex: 10,
            }}
          >
            <div>{activeTooltip.isPrediction ? `🎯 Forecast: ${activeTooltip.date}` : activeTooltip.date}</div>
            <div style={{ color: '#74c69d', fontSize: '0.95rem' }}>
              ₹{activeTooltip.price_per_kg} / kg
            </div>
            {activeTooltip.arrival_quantity_quintals && (
              <div style={{ fontSize: '0.72rem', opacity: 0.85 }}>
                Arrival: {activeTooltip.arrival_quantity_quintals} Qtl
              </div>
            )}
          </div>
        )}

        <div className="chart-legend">
          <div className="legend-item">
            <span className="legend-color-dot" style={{ background: '#2d6a4f' }}></span>
            <span>{t.historicalLegend}</span>
          </div>
          {prediction && (
            <div className="legend-item">
              <span className="legend-color-dot" style={{ background: '#e67e22' }}></span>
              <span>{t.forecastLegend} ({prediction.target_date})</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
