// TTS Service for Visual Novel Engine - Pre-generated Audio Version

class TTSService {
  constructor() {
    this.audioCache = new Map();
    this.currentAudio = null;
    this.isEnabled = true;
    this.audioMapping = null;
    this.currentLanguage = 'en';
    this.audioBasePath = '/audio/';
    this.gameConfig = null;
    this.initializeConfig();
  }

  // Initialize configuration
  async initializeConfig() {
    try {
      // Import gameConfig dynamically
      const { gameConfig } = await import('../utils/GameConfig.js');
      this.gameConfig = gameConfig;
      await this.loadAudioMapping();
    } catch (error) {
      console.warn('⚠️ Could not load game config, using fallback paths');
      await this.loadAudioMapping();
    }
  }

  // Load audio mapping for current language
  async loadAudioMapping() {
    try {
      let mappingPath;
      let audioBasePath;
      
      // Try to use game config first
      if (this.gameConfig) {
        await this.gameConfig.loadConfig();
        mappingPath = this.gameConfig.getAudioMappingPath();
        audioBasePath = this.gameConfig.getAudioPath();
        this.currentLanguage = this.gameConfig.get('language');
        
        console.log(`🔍 Loading audio mapping from config: ${mappingPath}`);
        console.log(`🎵 Audio base path from config: ${audioBasePath}`);
      } else {
        // Fallback to default paths
        mappingPath = `/audio/${this.currentLanguage}_audio_mapping.json`;
        audioBasePath = `/audio/`;
        console.log(`🔍 Loading audio mapping (fallback): ${mappingPath}`);
      }
      
      const response = await fetch(mappingPath);
      if (response.ok) {
        this.audioMapping = await response.json();
        this.audioBasePath = audioBasePath;
        
        console.log(`✅ Loaded audio mapping for ${this.currentLanguage}`);
        console.log(`🎵 Audio base path set to: ${this.audioBasePath}`);
        console.log(`📊 Audio mapping entries: ${Object.keys(this.audioMapping).length}`);
      } else {
        console.warn(`⚠️ No audio mapping found at ${mappingPath} (${response.status})`);
        
        // Try fallback path if config path failed
        if (this.gameConfig && mappingPath !== `/audio/${this.currentLanguage}_audio_mapping.json`) {
          console.log('🔄 Trying fallback audio mapping path...');
          const fallbackResponse = await fetch(`/audio/${this.currentLanguage}_audio_mapping.json`);
          if (fallbackResponse.ok) {
            this.audioMapping = await fallbackResponse.json();
            this.audioBasePath = `/audio/`;
            console.log(`✅ Loaded fallback audio mapping for ${this.currentLanguage}`);
          } else {
            this.audioMapping = {};
          }
        } else {
          this.audioMapping = {};
        }
      }
    } catch (error) {
      console.warn(`⚠️ Failed to load audio mapping: ${error.message}`);
      this.audioMapping = {};
    }
  }

  // Set current language and reload mapping
  async setLanguage(language) {
    if (this.currentLanguage !== language) {
      this.currentLanguage = language;
      
      // Update config if available
      if (this.gameConfig) {
        this.gameConfig.updateConfig({ language: language });
      }
      
      await this.loadAudioMapping();
      // Clear cache when language changes
      this.audioCache.clear();
    }
  }

  // Get audio filename for dialogue
  getAudioFilename(text, characterName) {
    const dialogueKey = `${characterName}:${text}`;
    const filename = this.audioMapping[dialogueKey] || null;
    
    if (!filename) {
      console.warn(`🔍 Audio mapping lookup failed for key: "${dialogueKey.substring(0, 100)}..."`);
      console.warn(`📊 Available mapping keys (first 3):`, Object.keys(this.audioMapping).slice(0, 3));
    } else {
      console.log(`✅ Audio mapping found: "${dialogueKey.substring(0, 50)}..." -> ${filename}`);
    }
    
    return filename;
  }

  // Load pre-generated audio file
  async loadAudioFile(text, characterName) {
    const filename = this.getAudioFilename(text, characterName);
    
    if (!filename) {
      console.warn(`⚠️ No pre-generated audio found for: "${text.substring(0, 50)}..."`);
      return null;
    }

    // Use dynamic audio path from config
    const audioPath = `${this.audioBasePath}${filename}`;
    const currentLang = this.gameConfig ? this.gameConfig.get('language') : this.currentLanguage;
    const cacheKey = `${currentLang}_${filename}`;

    // Check cache first
    if (this.audioCache.has(cacheKey)) {
      console.log(`🔄 Using cached audio: ${filename}`);
      return this.audioCache.get(cacheKey);
    }

    try {
      console.log(`🎵 Loading pre-generated audio: ${filename}`);
      
      const response = await fetch(audioPath);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const arrayBuffer = await response.arrayBuffer();
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

      // Cache the audio buffer
      this.audioCache.set(cacheKey, audioBuffer);
      console.log(`✅ Loaded and cached audio: ${filename}`);

      return audioBuffer;
    } catch (error) {
      console.error(`❌ Failed to load audio file ${filename}:`, error);
      return null;
    }
  }

  // Determine voice gender based on character
  getVoiceGender(characterName) {
    // Player gets male voice for accessibility
    if (characterName === 'Player') {
      return 'male';
    }
    // Default female voice for other characters (like Kurisu)
    return 'female';
  }

  // Get audio for dialogue
  async getAudio(text, language, sceneIndex, interactionIndex, characterName = null) {
    if (!this.isEnabled || !text || text.trim() === '') {
      return null;
    }

    // Set language if different
    await this.setLanguage(language);

    // Load pre-generated audio
    const audioBuffer = await this.loadAudioFile(text, characterName);
    
    if (audioBuffer) {
      console.log(`🎵 Audio ready for: "${text.substring(0, 30)}..."`);
      return audioBuffer;
    }

    console.warn(`⚠️ No audio available for: "${text.substring(0, 30)}..."`);
    return null;
  }

  // Play audio from buffer
  async playAudioBuffer(audioBuffer) {
    if (!audioBuffer) {
      return false;
    }

    try {
      // Stop any currently playing audio
      this.stopCurrentAudio();

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);
      
      this.currentAudio = source;
      
      source.start(0);
      console.log('🔊 Playing pre-generated audio');
      
      return true;
    } catch (error) {
      console.error('❌ Failed to play audio:', error);
      return false;
    }
  }

  // Play dialogue audio with character voice
  async playDialogueAudio(text, language, sceneIndex, interactionIndex, characterName = null) {
    if (!this.isEnabled) {
      console.log('🔇 TTS is disabled');
      return false;
    }

    try {
      console.log(`🎤 Playing dialogue [${characterName || 'Unknown'}]: "${text.substring(0, 50)}..."`);
      
      const audioBuffer = await this.getAudio(text, language, sceneIndex, interactionIndex, characterName);
      
      if (audioBuffer) {
        const success = await this.playAudioBuffer(audioBuffer);
        if (success) {
          console.log(`✅ Audio playback started for ${characterName || 'character'}`);
          return true;
        }
      }
      
      console.warn(`⚠️ Could not play audio for dialogue`);
      return false;
    } catch (error) {
      console.error('❌ Error in playDialogueAudio:', error);
      return false;
    }
  }

  // Play choice prompt audio (always uses Player voice for accessibility)
  async playChoicePromptAudio(prompt, language, sceneIndex, interactionIndex) {
    if (!this.isEnabled) {
      return false;
    }

    console.log(`🎯 Playing choice prompt: "${prompt.substring(0, 30)}..."`);
    
    // Choice prompts always use Player voice for accessibility
    return await this.playDialogueAudio(prompt, language, sceneIndex, interactionIndex, 'Player');
  }

  // Stop currently playing audio
  stopCurrentAudio() {
    if (this.currentAudio) {
      try {
        this.currentAudio.stop();
        console.log('⏹️ Stopped current audio');
      } catch (error) {
        // Audio might already be stopped
      }
      this.currentAudio = null;
    }
  }

  // Toggle TTS on/off
  toggleTTS() {
    this.isEnabled = !this.isEnabled;
    if (!this.isEnabled) {
      this.stopCurrentAudio();
    }
    console.log(`🎵 TTS ${this.isEnabled ? 'enabled' : 'disabled'}`);
    return this.isEnabled;
  }

  // Get current status
  getStatus() {
    return {
      enabled: this.isEnabled,
      hasCurrentAudio: !!this.currentAudio,
      cacheSize: this.audioCache.size,
      currentLanguage: this.currentLanguage,
      hasMappingLoaded: !!this.audioMapping
    };
  }

  // Cleanup resources
  cleanup() {
    this.stopCurrentAudio();
    this.audioCache.clear();
    this.audioMapping = null;
    console.log('🧹 TTS Service cleaned up');
  }
}

// Create singleton instance
const ttsServiceInstance = new TTSService();

// Export as global
window.TTSService = ttsServiceInstance;

// Export as default for ES6 modules
export default ttsServiceInstance;

// Export for CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ttsServiceInstance;
}