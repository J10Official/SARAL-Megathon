import React, { useState, useEffect } from 'react';

const CharacterDisplay = ({ character, expression, onError }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageSrc, setImageSrc] = useState('');

  const log = (message, data = null, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `👤 [${timestamp}] CharacterDisplay:`;
    
    switch (level) {
      case 'error':
        console.error(`❌ ${prefix}`, message, data);
        break;
      default:
        console.log(`ℹ️ ${prefix}`, message, data);
    }
  };

  useEffect(() => {
    if (!character || character === 'Player') {
      log('No character image needed', { character });
      setImageLoaded(false);
      setImageSrc('');
      return;
    }

    const newImageSrc = `/${character}/${expression}.png`;
    log('Loading character image', { character, expression, src: newImageSrc });
    
    setImageSrc(newImageSrc);
    setImageLoaded(false);
  }, [character, expression]);

  const handleImageLoad = () => {
    log('Character image loaded successfully', { character, expression });
    setImageLoaded(true);
  };

  const handleImageError = (e) => {
    const errorMsg = `Failed to load character image: ${imageSrc}`;
    log(errorMsg, { character, expression }, 'error');
    
    if (onError) onError(new Error(errorMsg));
    setImageLoaded(false);
  };

  // Don't render anything for Player character
  if (!character || character === 'Player') {
    return null;
  }

  return (
    <div className="absolute inset-0 flex items-end justify-center pointer-events-none z-10">
      <div className="relative">
        {imageSrc && (
          <img
            src={imageSrc}
            alt={`${character} - ${expression}`}
            className={`character-image max-h-screen transition-all duration-500 ${
              imageLoaded 
                ? 'opacity-100 animate-fade-in' 
                : 'opacity-0'
            }`}
            onLoad={handleImageLoad}
            onError={handleImageError}
            style={{
              maxHeight: '80vh',
              width: 'auto',
              objectFit: 'contain',
            }}
          />
        )}
        
        {!imageLoaded && imageSrc && (
          <div className="flex items-center justify-center h-64 w-64 bg-gray-800 rounded-lg animate-pulse">
            <div className="text-gray-400 text-sm">
              Loading {character}...
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CharacterDisplay;