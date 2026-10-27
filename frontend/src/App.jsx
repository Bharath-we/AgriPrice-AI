import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import DashboardPage from './pages/DashboardPage';
import PredictionPage from './pages/PredictionPage';
import MarketComparisonPage from './pages/MarketComparisonPage';
import ProfitCalculatorPage from './pages/ProfitCalculatorPage';
import PriceAlertsPage from './pages/PriceAlertsPage';
import DataQualityPage from './pages/DataQualityPage';
import ModelPerformancePage from './pages/ModelPerformancePage';
import AboutPage from './pages/AboutPage';

import {
  fetchCommodities,
  fetchMarkets,
  predictPrice,
  fetchHistoricalData,
  fetchMarketSummary,
  fetchModelInfo,
} from './services/api';
import { translations } from './data/i18n';

export default function App() {
  const [lang, setLang] = useState('en');
  const [activePage, setActivePage] = useState('dashboard');
  const t = translations[lang] || translations.en;

  const [commodities, setCommodities] = useState([]);
  const [markets, setMarkets] = useState([]);

  // Calculate default target date 7 days from today
  const defaultTargetDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split('T')[0];

  const [formData, setFormData] = useState({
    commodity: 'tomato',
    market: 'dindigul',
    targetDate: defaultTargetDate,
    arrivalVolume: 650,
    rainfallFactor: 1.0,
  });

  const [prediction, setPrediction] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [marketSummary, setMarketSummary] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);

  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initial load
  useEffect(() => {
    async function initApp() {
      try {
        setInitialLoading(true);
        const [comms, mkts, mInfo] = await Promise.all([
          fetchCommodities(),
          fetchMarkets(),
          fetchModelInfo(),
        ]);
        setCommodities(comms);
        setMarkets(mkts);
        setModelInfo(mInfo);

        // Run initial prediction for default crop & market
        await runInference('tomato', 'dindigul', defaultTargetDate, 650, 1.0);
      } catch (err) {
        console.error('Initialization error:', err);
        setError('Failed to initialize market data. Retrying...');
      } finally {
        setInitialLoading(false);
      }
    }
    initApp();
  }, []);

  const runInference = async (comm, mkt, date, arrival, rain) => {
    setLoading(true);
    setError(null);
    try {
      const [predResult, histResult, summaryResult] = await Promise.all([
        predictPrice({
          commodity: comm,
          market: mkt,
          target_date: date,
          arrival_volume_quintals: arrival,
          rainfall_factor: rain,
        }),
        fetchHistoricalData(comm, mkt, 35),
        fetchMarketSummary(comm),
      ]);
      setPrediction(predResult);
      setHistoricalData(histResult);
      setMarketSummary(summaryResult);
    } catch (err) {
      console.error('Prediction failed:', err);
      setError(err.message || 'Error communicating with AgriPrice inference engine.');
    } finally {
      setLoading(false);
    }
  };

  const handleCommoditySelect = (commodityId) => {
    setFormData((prev) => ({ ...prev, commodity: commodityId }));
    runInference(
      commodityId,
      formData.market,
      formData.targetDate,
      formData.arrivalVolume,
      formData.rainfallFactor
    );
  };

  const handleMarketSelect = (marketId) => {
    setFormData((prev) => ({ ...prev, market: marketId }));
    runInference(
      formData.commodity,
      marketId,
      formData.targetDate,
      formData.arrivalVolume,
      formData.rainfallFactor
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    runInference(
      formData.commodity,
      formData.market,
      formData.targetDate,
      formData.arrivalVolume,
      formData.rainfallFactor
    );
  };

  const handleLaunchCropForecast = (commodityId) => {
    handleCommoditySelect(commodityId);
    setActivePage('prediction');
  };

  return (
    <div className="app-wrapper">
      <Header lang={lang} setLang={setLang} />
      <Navbar activePage={activePage} setActivePage={setActivePage} lang={lang} />

      {/* Hero Banner */}
      <section className="hero-banner">
        <div className="container">
          <h1 className="hero-heading">
            {lang === 'ta' ? 'தமிழ்நாடு வேளாண் சந்தை முன்கணிப்பு மையம்' : 'Tamil Nadu Agricultural Price Prediction'}
          </h1>
          <p className="hero-lead">
            {lang === 'ta'
              ? 'தமிழ்நாடு ஒழுங்குமுறை விற்பனைக்கூடங்களின் நேரடி விலைப்போக்கு மற்றும் அறிவியல் பூர்வமான AI முன்கணிப்பு மூலம் உழவர்களின் நியாயமான விலைக்கான வழிகாட்டி.'
              : 'Empowering Tamil Nadu farmers with real-time spot rates, multi-horizon AI price forecasting, and data-backed sell vs. hold advisory evaluated with zero future data leakage.'}
          </p>
        </div>
      </section>

      <main className="container" style={{ padding: '28px 20px 48px' }}>
        {error && (
          <div
            style={{
              marginBottom: '20px',
              padding: '14px 18px',
              backgroundColor: '#ffebee',
              color: '#c62828',
              borderRadius: '8px',
              border: '1px solid #ffcdd2',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: 700 }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Dynamic Page Rendering */}
        {activePage === 'dashboard' && (
          <DashboardPage
            commodities={commodities}
            markets={markets}
            onSelectCropForForecast={handleLaunchCropForecast}
            lang={lang}
          />
        )}

        {activePage === 'prediction' && (
          <PredictionPage
            commodities={commodities}
            markets={markets}
            formData={formData}
            setFormData={setFormData}
            prediction={prediction}
            historicalData={historicalData}
            onSubmit={handleSubmit}
            onSelectCommodity={handleCommoditySelect}
            loading={loading}
            lang={lang}
          />
        )}

        {activePage === 'comparison' && (
          <MarketComparisonPage
            commodities={commodities}
            selectedCommodity={formData.commodity}
            onSelectCommodity={handleCommoditySelect}
            lang={lang}
          />
        )}

        {activePage === 'calculator' && (
          <ProfitCalculatorPage
            commodities={commodities}
            markets={markets}
            lang={lang}
          />
        )}

        {activePage === 'alerts' && (
          <PriceAlertsPage
            commodities={commodities}
            markets={markets}
            lang={lang}
          />
        )}

        {activePage === 'dataquality' && (
          <DataQualityPage lang={lang} />
        )}

        {activePage === 'performance' && (
          <ModelPerformancePage modelInfo={modelInfo} lang={lang} />
        )}

        {activePage === 'about' && (
          <AboutPage lang={lang} />
        )}
      </main>

      <Footer lang={lang} />
    </div>
  );
}
