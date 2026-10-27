import React from 'react';
import { Sprout, Globe, Activity } from 'lucide-react';
import { translations } from '../data/i18n';

export default function Header({ lang, setLang }) {
  const t = translations[lang] || translations.en;

  const toggleLanguage = () => {
    setLang(lang === 'en' ? 'ta' : 'en');
  };

  return (
    <header className="app-header">
      <div className="container header-content">
        <div className="brand-wrapper">
          <div className="brand-logo">
            <Sprout size={26} color="#74c69d" />
          </div>
          <div className="brand-title-wrap">
            <h1>
              {t.appName}
              <span className="brand-tag">{t.stateName}</span>
            </h1>
            <p className="brand-subtitle">{t.tagline}</p>
          </div>
        </div>

        <div className="header-actions">
          <div className="mandi-status-badge">
            <span className="status-dot"></span>
            <span>{t.liveMandiStatus}</span>
          </div>

          <button className="lang-btn" onClick={toggleLanguage} title="Change Language">
            <Globe size={16} />
            <span>{t.langToggle}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
