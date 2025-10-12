import React, { useState, useEffect } from 'react';
import { gameConfig } from '../utils/GameConfig';

const LanguageSwitcher = ({ onLanguageChange }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [availableLanguages, setAvailableLanguages] = useState(['en']);
  const [availablePDFs, setAvailablePDFs] = useState([]);
  const [currentPDF, setCurrentPDF] = useState('');

  useEffect(() => {
    const loadConfigInfo = async () => {
      await gameConfig.loadConfig();
      const config = gameConfig.getAll();
      setCurrentLanguage(config.language);
      setCurrentPDF(config.pdf_name);
      
      // Get available languages for current PDF
      const languages = await gameConfig.getAvailableLanguages();
      setAvailableLanguages(languages);
      
      // Get available PDFs
      const pdfs = await gameConfig.getAvailablePDFs();
      setAvailablePDFs(pdfs);
    };
    
    loadConfigInfo();
  }, []);

  const handleLanguageChange = async (newLanguage) => {
    if (newLanguage !== currentLanguage) {
      setCurrentLanguage(newLanguage);
      gameConfig.updateConfig({ language: newLanguage });
      
      if (onLanguageChange) {
        onLanguageChange(newLanguage);
      }
    }
  };

  const handlePDFChange = async (newPDF) => {
    if (newPDF !== currentPDF) {
      setCurrentPDF(newPDF);
      gameConfig.updateConfig({ pdf_name: newPDF });
      
      // Reload page to switch PDF content
      window.location.reload();
    }
  };

  const getLanguageName = (code) => {
    const names = {
      'en': 'English',
      'hi': 'हिंदी (Hindi)',
      'te': 'తెలుగు (Telugu)'
    };
    return names[code] || code.toUpperCase();
  };

  return (
    <div className="language-switcher" style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'rgba(0, 0, 0, 0.8)',
      color: 'white',
      padding: '10px',
      borderRadius: '8px',
      zIndex: 1000,
      fontSize: '14px'
    }}>
      <div style={{ marginBottom: '10px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          📚 PDF Content:
        </label>
        <select 
          value={currentPDF} 
          onChange={(e) => handlePDFChange(e.target.value)}
          style={{
            background: '#333',
            color: 'white',
            border: '1px solid #555',
            padding: '3px',
            borderRadius: '3px',
            width: '100%'
          }}
        >
          {availablePDFs.map(pdf => (
            <option key={pdf} value={pdf}>{pdf}</option>
          ))}
        </select>
      </div>
      
      <div>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          🌍 Language:
        </label>
        <select 
          value={currentLanguage} 
          onChange={(e) => handleLanguageChange(e.target.value)}
          style={{
            background: '#333',
            color: 'white',
            border: '1px solid #555',
            padding: '3px',
            borderRadius: '3px',
            width: '100%'
          }}
        >
          {availableLanguages.map(lang => (
            <option key={lang} value={lang}>
              {getLanguageName(lang)}
            </option>
          ))}
        </select>
      </div>
      
      <div style={{ 
        marginTop: '10px', 
        fontSize: '12px', 
        opacity: 0.7,
        borderTop: '1px solid #555',
        paddingTop: '5px'
      }}>
        <div>📄 {currentPDF}</div>
        <div>🎵 Audio: {gameConfig.get('audio_enabled') ? 'ON' : 'OFF'}</div>
      </div>
    </div>
  );
};

export default LanguageSwitcher;