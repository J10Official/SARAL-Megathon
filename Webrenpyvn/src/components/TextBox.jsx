import React, { useState, useEffect, useCallback } from 'react';
import { FaForward } from 'react-icons/fa';

const TextBox = ({ 
  character, 
  dialogue, 
  onTextComplete, 
  onAdvance, 
  canAdvance = false,
  textSpeed = 50 
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const log = (message, data = null, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `💬 [${timestamp}] TextBox:`;
    
    switch (level) {
      case 'error':
        console.error(`❌ ${prefix}`, message, data);
        break;
      default:
        console.log(`ℹ️ ${prefix}`, message, data);
    }
  };

  const startTyping = useCallback(() => {
    if (!dialogue) return;
    
    log('Starting text animation', { character, dialogue: dialogue.substring(0, 50) + '...' });
    
    setDisplayedText('');
    setCurrentIndex(0);
    setIsTyping(true);
  }, [dialogue, character]);

  // Typing animation effect
  useEffect(() => {
    if (!isTyping || !dialogue) return;

    if (currentIndex < dialogue.length) {
      const timer = setTimeout(() => {
        setDisplayedText(dialogue.substring(0, currentIndex + 1));
        setCurrentIndex(currentIndex + 1);
      }, textSpeed);

      return () => clearTimeout(timer);
    } else {
      // Typing complete
      log('Text animation completed');
      setIsTyping(false);
      if (onTextComplete) {
        onTextComplete();
      }
    }
  }, [currentIndex, dialogue, isTyping, textSpeed, onTextComplete]);

  // Start typing when dialogue changes
  useEffect(() => {
    startTyping();
  }, [startTyping]);

  const handleClick = () => {
    if (isTyping) {
      // Skip typing animation
      log('Skipping text animation');
      setDisplayedText(dialogue);
      setIsTyping(false);
      setCurrentIndex(dialogue.length);
      if (onTextComplete) {
        onTextComplete();
      }
    } else if (canAdvance && onAdvance) {
      // Advance to next interaction
      log('Advancing to next interaction');
      onAdvance();
    }
  };

  if (!dialogue) {
    return null;
  }

  return (
    <div 
      className="absolute bottom-0 left-0 right-0 z-20"
      onClick={handleClick}
    >
      <div className="vn-textbox mx-4 mb-4 p-6 rounded-lg cursor-pointer select-none">
        {/* Character Name */}
        {character && character !== 'Player' && (
          <div className="text-blue-300 font-semibold text-lg mb-2 animate-slide-up">
            {character}
          </div>
        )}
        
        {/* Dialogue Text */}
        <div className="text-white text-lg leading-relaxed font-visual-novel min-h-[3rem] flex items-center">
          <span className="block">
            {displayedText}
            {isTyping && (
              <span className="inline-block w-2 h-6 bg-white ml-1 animate-pulse" />
            )}
          </span>
        </div>
        
        {/* Continue Indicator */}
        {canAdvance && !isTyping && (
          <div className="flex justify-end mt-3">
            <div className="flex items-center text-gray-300 text-sm animate-pulse">
              <span className="mr-2">Continue</span>
              <FaForward className="text-xs" />
            </div>
          </div>
        )}
        
        {/* Skip Indicator */}
        {isTyping && (
          <div className="flex justify-end mt-3">
            <div className="text-gray-400 text-xs animate-pulse">
              Click to skip
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TextBox;