import React from 'react';
import { translations } from '../data/i18n';

export default function Footer({ lang }) {
  const t = translations[lang] || translations.en;

  return (
    <footer className="app-footer">
      <div className="container footer-content">
        <p className="footer-copy">{t.footerText}</p>
        <p className="footer-disclaimer">{t.footerDisclaimer}</p>
      </div>
    </footer>
  );
}
