import React, { useEffect, useRef, useState } from 'react';

const AudioManager = ({ currentMusic, volume = 0.7, onError }) => {
  const audioRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [currentTrack, setCurrentTrack] = useState(null);

  const log = (message, data = null, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `🎵 [${timestamp}] AudioManager:`;
    
    switch (level) {
      case 'error':
        console.error(`❌ ${prefix}`, message, data);
        break;
      case 'warn':
        console.warn(`⚠️ ${prefix}`, message, data);
        break;
      default:
        console.log(`ℹ️ ${prefix}`, message, data);
    }
  };

  useEffect(() => {
    if (!currentMusic) {
      log('No music specified');
      return;
    }

    // Don't reload the same track
    if (currentTrack === currentMusic && isLoaded) {
      log('Same track already playing', currentMusic);
      return;
    }

    const audio = audioRef.current;
    if (!audio) return;

    const loadMusic = async () => {
      try {
        log('Loading music', currentMusic);
        
        // Stop current music if playing
        audio.pause();
        audio.currentTime = 0;
        
        // Set new source
        audio.src = `/Music/${currentMusic}`;
        audio.volume = volume;
        audio.loop = true;
        
        // Load and play
        await audio.load();
        
        const playPromise = audio.play();
        if (playPromise !== undefined) {
          await playPromise;
          log('Music started playing', currentMusic);
          setIsLoaded(true);
          setCurrentTrack(currentMusic);
        }
        
      } catch (error) {
        log('Failed to load/play music', { music: currentMusic, error }, 'error');
        if (onError) onError(error);
        setIsLoaded(false);
      }
    };

    loadMusic();
  }, [currentMusic, onError, currentTrack, isLoaded, volume]);

  // Update volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = Math.max(0, Math.min(1, volume));
      log('Volume updated', volume);
    }
  }, [volume]);

  // Cleanup
  useEffect(() => {
    const audio = audioRef.current;
    return () => {
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
        log('Audio cleanup performed');
      }
    };
  }, []);

  return (
    <audio
      ref={audioRef}
      onError={(e) => {
        log('Audio element error', e.target.error, 'error');
        if (onError) onError(e.target.error);
      }}
      onLoadStart={() => log('Started loading audio')}
      onCanPlayThrough={() => log('Audio ready to play')}
      onEnded={() => log('Audio playback ended')}
      style={{ display: 'none' }}
    />
  );
};

export default AudioManager;