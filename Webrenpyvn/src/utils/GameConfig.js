/**
 * Game Configuration Manager
 * Handles loading and parsing of game.conf file
 */

export class GameConfig {
  constructor() {
    this.config = {
      pdf_name: '2509.21175v1',
      language: 'en',
      audio_enabled: true,
      auto_play: false,
      auto_play_delay: 3000,
      debug_mode: false
    };
    this.loaded = false;
  }

  /**
   * Load configuration from game.conf file
   */
  async loadConfig() {
    try {
      const response = await fetch('/game.conf');
      if (!response.ok) {
        console.warn('Could not load game.conf, using defaults');
        return this.config;
      }
      
      const configText = await response.text();
      this.parseConfig(configText);
      this.loaded = true;
      
      if (this.config.debug_mode) {
        console.log('🎮 Game config loaded:', this.config);
      }
      
      return this.config;
    } catch (error) {
      console.error('Error loading game config:', error);
      return this.config;
    }
  }

  /**
   * Parse configuration file content
   */
  parseConfig(configText) {
    const lines = configText.split('\n');
    
    for (const line of lines) {
      const trimmed = line.trim();
      
      // Skip comments and empty lines
      if (trimmed.startsWith('#') || trimmed === '') {
        continue;
      }
      
      // Parse key=value pairs
      const [key, ...valueParts] = trimmed.split('=');
      if (key && valueParts.length > 0) {
        const value = valueParts.join('=').trim();
        this.setConfigValue(key.trim(), value);
      }
    }
  }

  /**
   * Set configuration value with type conversion
   */
  setConfigValue(key, value) {
    // Convert string values to appropriate types
    if (value === 'true') {
      this.config[key] = true;
    } else if (value === 'false') {
      this.config[key] = false;
    } else if (!isNaN(value) && value !== '') {
      this.config[key] = parseInt(value, 10);
    } else {
      this.config[key] = value;
    }
  }

  /**
   * Get configuration value
   */
  get(key) {
    return this.config[key];
  }

  /**
   * Get all configuration
   */
  getAll() {
    return { ...this.config };
  }

  /**
   * Get script path based on current configuration
   */
  getScriptPath() {
    const pdfName = this.get('pdf_name');
    const language = this.get('language');
    
    if (language === 'en') {
      return `/outputs/${pdfName}/en/${pdfName}_vn_script.json`;
    } else {
      return `/outputs/${pdfName}/${language}/${pdfName}_vn_script_${language}.json`;
    }
  }

  /**
   * Get audio directory based on current configuration
   */
  getAudioPath() {
    const pdfName = this.get('pdf_name');
    const language = this.get('language');
    return `/outputs/${pdfName}/${language}/audio/`;
  }

  /**
   * Get audio mapping file path
   */
  getAudioMappingPath() {
    const pdfName = this.get('pdf_name');
    const language = this.get('language');
    return `/outputs/${pdfName}/${language}/${language}_audio_mapping.json`;
  }

  /**
   * Update configuration and save (for future enhancement)
   */
  updateConfig(updates) {
    this.config = { ...this.config, ...updates };
    
    if (this.config.debug_mode) {
      console.log('🎮 Config updated:', updates);
    }
  }

  /**
   * Get available languages for current PDF
   */
  async getAvailableLanguages() {
    const pdfName = this.get('pdf_name');
    const availableLanguages = [];
    
    // Check which language folders exist
    const languages = ['en', 'hi', 'te'];
    
    for (const lang of languages) {
      try {
        const scriptPath = lang === 'en' 
          ? `/outputs/${pdfName}/en/${pdfName}_vn_script.json`
          : `/outputs/${pdfName}/${lang}/${pdfName}_vn_script_${lang}.json`;
          
        const response = await fetch(scriptPath, { method: 'HEAD' });
        if (response.ok) {
          availableLanguages.push(lang);
        }
      } catch (error) {
        // Language not available
      }
    }
    
    return availableLanguages;
  }

  /**
   * Get available PDFs
   */
  async getAvailablePDFs() {
    try {
      // Try to fetch a list of available outputs
      // For now, return the current PDF
      return [this.get('pdf_name')];
    } catch (error) {
      return [this.get('pdf_name')];
    }
  }
}

// Create singleton instance
export const gameConfig = new GameConfig();