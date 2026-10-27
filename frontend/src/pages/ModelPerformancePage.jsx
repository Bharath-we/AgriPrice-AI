import React from 'react';
import ModelTransparency from '../components/ModelTransparency';
import { translations } from '../data/i18n';

export default function ModelPerformancePage({ modelInfo, lang }) {
  const t = translations[lang] || translations.en;

  return (
    <div>
      <ModelTransparency modelInfo={modelInfo} lang={lang} />
    </div>
  );
}
