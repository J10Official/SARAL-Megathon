import React from 'react';

const Background = () => {
  const log = (message, data = null, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `🖼️ [${timestamp}] Background:`;
    
    switch (level) {
      case 'error':
        console.error(`❌ ${prefix}`, message, data);
        break;
      default:
        console.log(`ℹ️ ${prefix}`, message, data);
    }
  };

  React.useEffect(() => {
    log('Background component mounted - using static lab.jpg');
  }, []);

  return (
    <div className="absolute inset-0 w-full h-full">
      <img
        src="/backgrounds/lab.jpg"
        alt="Visual Novel Background"
        className="w-full h-full object-cover"
        onLoad={() => log('Background image loaded successfully')}
        onError={(e) => {
          log('Failed to load background image', e, 'error');
          // Fallback to gradient background
          e.target.style.display = 'none';
          e.target.parentElement.style.background = 'linear-gradient(135deg, #1e3a8a 0%, #312e81 50%, #1e1b4b 100%)';
        }}
      />
      
      {/* Optional overlay for better text readability */}
      <div className="absolute inset-0 bg-black bg-opacity-20"></div>
    </div>
  );
};

export default Background;