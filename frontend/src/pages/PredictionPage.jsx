import React from 'react';
import CommodityGrid from '../components/CommodityGrid';
import PricePredictorForm from '../components/PricePredictorForm';
import PredictionResultCard from '../components/PredictionResultCard';
import PriceTrendChart from '../components/PriceTrendChart';
import { translations } from '../data/i18n';

export default function PredictionPage({
  commodities,
  markets,
  formData,
  setFormData,
  prediction,
  historicalData,
  onSubmit,
  onSelectCommodity,
  loading,
  lang,
}) {
  const t = translations[lang] || translations.en;

  return (
    <div>
      {/* Quick Commodity Ribbon */}
      <CommodityGrid
        commodities={commodities}
        selectedCommodity={formData.commodity}
        onSelectCommodity={onSelectCommodity}
        lang={lang}
      />

      {/* Main Grid: Form + Result */}
      <div className="main-grid">
        <PricePredictorForm
          commodities={commodities}
          markets={markets}
          formData={formData}
          setFormData={setFormData}
          onSubmit={onSubmit}
          loading={loading}
          lang={lang}
        />

        <PredictionResultCard prediction={prediction} lang={lang} />
      </div>

      {/* Historical Trend and Forecast Path */}
      <PriceTrendChart
        historicalData={historicalData}
        prediction={prediction}
        lang={lang}
      />
    </div>
  );
}
