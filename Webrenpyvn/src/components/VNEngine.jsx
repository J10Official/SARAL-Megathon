import React, { useState, useEffect, useCallback } from 'react';
import { FaVolumeUp, FaVolumeMute, FaCog, FaMicrophone, FaMicrophoneSlash } from 'react-icons/fa';
import AudioManager from './AudioManager';
import CharacterDisplay from './CharacterDisplay';
import TextBox from './TextBox';
import ChoiceMenu from './ChoiceMenu';
import Background from './Background';
import LanguageSwitcher from './LanguageSwitcher';
import TTSService from '../services/TTSService';
import { gameConfig } from '../utils/GameConfig';

const VNEngine = () => {
  const [gameState, setGameState] = useState({
    currentSceneIndex: 0,
    currentInteractionIndex: 0,
    isLoading: true,
    script: null,
    choices: null,
    showChoices: false,
    isTextComplete: false,
    isGameComplete: false,
    tempInteraction: null,
    tempInteractionSequence: null,
    tempInteractionIndex: 0,
  });

  const [settings, setSettings] = useState({
    autoPlay: false,
    textSpeed: 50,
    musicVolume: 0.7,
    soundEffectsVolume: 0.8,
    isMuted: false,
    ttsEnabled: true,
  });

  const [debugMode, setDebugMode] = useState(true);

  // Enhanced logging function
  const log = useCallback((message, data = null, level = 'info') => {
    if (!debugMode) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `🎮 [${timestamp}] VNEngine:`;
    
    switch (level) {
      case 'error':
        console.error(`❌ ${prefix}`, message, data);
        break;
      case 'warn':
        console.warn(`⚠️ ${prefix}`, message, data);
        break;
      case 'debug':
        console.debug(`🔍 ${prefix}`, message, data);
        break;
      default:
        console.log(`ℹ️ ${prefix}`, message, data);
    }
  }, [debugMode]);

  // Load script data
  useEffect(() => {
    const loadScript = async () => {
      try {
        log('Loading game configuration...');
        
        // Load game configuration first
        const config = await gameConfig.loadConfig();
        log('Game configuration loaded', config);
        
        // Get script path from configuration
        const scriptPath = gameConfig.getScriptPath();
        log(`Loading script from: ${scriptPath}`);
        
        const response = await fetch(scriptPath);
        
        if (!response.ok) {
          throw new Error(`Failed to load script: ${response.status} ${response.statusText}`);
        }
        
        const scriptData = await response.json();
        log('Script loaded successfully', {
          language: config.language,
          pdfName: config.pdf_name,
          totalScenes: scriptData.script?.length || 0
        });
        
        setGameState(prev => ({
          ...prev,
          script: scriptData,
          isLoading: false,
        }));
        
        // Update settings from config
        setSettings(prev => ({
          ...prev,
          autoPlay: config.auto_play,
          isMuted: !config.audio_enabled,
          ttsEnabled: config.audio_enabled,
        }));
        
        // Initialize TTS service with the correct language
        try {
          await TTSService.setLanguage(config.language);
          log(`TTS service initialized for language: ${config.language}`);
        } catch (ttsError) {
          log('Failed to initialize TTS service', ttsError, 'warn');
        }
        
        log('Game state initialized', {
          totalScenes: scriptData.script?.length || 0,
          firstScene: scriptData.script?.[0]?.scene_name,
          language: config.language,
          audioPath: gameConfig.getAudioPath(),
        });
        
      } catch (error) {
        log('Failed to load script', error, 'error');
        setGameState(prev => ({ ...prev, isLoading: false }));
        
        // Fallback to default script.json if config-based loading fails
        try {
          log('Attempting fallback to /script.json...');
          const fallbackResponse = await fetch('/script.json');
          if (fallbackResponse.ok) {
            const fallbackData = await fallbackResponse.json();
            setGameState(prev => ({
              ...prev,
              script: fallbackData,
              isLoading: false,
            }));
            log('Fallback script loaded successfully');
          }
        } catch (fallbackError) {
          log('Fallback loading also failed', fallbackError, 'error');
        }
      }
    };

    loadScript();
  }, [log]);

  const getCurrentScene = useCallback(() => {
    if (!gameState.script?.script) return null;
    return gameState.script.script[gameState.currentSceneIndex];
  }, [gameState.script, gameState.currentSceneIndex]);

  const getCurrentInteraction = useCallback(() => {
    // Handle temporary interaction sequence (for wrong answers)
    if (gameState.tempInteractionSequence && gameState.tempInteractionIndex < gameState.tempInteractionSequence.length) {
      return gameState.tempInteractionSequence[gameState.tempInteractionIndex];
    }
    
    // Handle single temporary interaction (for correct answers)
    if (gameState.tempInteraction) {
      return gameState.tempInteraction;
    }
    
    // Regular interaction
    const scene = getCurrentScene();
    if (!scene?.interactions) return null;
    return scene.interactions[gameState.currentInteractionIndex];
  }, [getCurrentScene, gameState.currentInteractionIndex, gameState.tempInteraction, gameState.tempInteractionSequence, gameState.tempInteractionIndex]);

  const advanceInteraction = useCallback(() => {
    const scene = getCurrentScene();
    if (!scene) {
      log('Cannot advance: No current scene', null, 'warn');
      return;
    }

    const currentInteraction = getCurrentInteraction();
    if (!currentInteraction) {
      log('Cannot advance: No current interaction', null, 'warn');
      return;
    }

    log('Advancing interaction', {
      currentScene: gameState.currentSceneIndex,
      currentInteraction: gameState.currentInteractionIndex,
      character: currentInteraction.character_name,
      isTemporary: currentInteraction.isTemporary
    });

    // Handle temporary interactions
    if (currentInteraction.isTemporary) {
      if (gameState.tempInteractionSequence) {
        // Advance through temporary sequence
        if (gameState.tempInteractionIndex < gameState.tempInteractionSequence.length - 1) {
          setGameState(prev => ({
            ...prev,
            tempInteractionIndex: prev.tempInteractionIndex + 1,
            isTextComplete: false,
          }));
          return;
        } else {
          // End of temporary sequence, clear and advance normally
          setGameState(prev => ({
            ...prev,
            tempInteractionSequence: null,
            tempInteractionIndex: 0,
          }));
        }
      } else if (gameState.tempInteraction) {
        // Clear single temporary interaction
        setGameState(prev => ({
          ...prev,
          tempInteraction: null,
        }));
      }
      
      // After clearing temporary, advance normally
      setTimeout(() => {
        advanceToNext();
      }, 100);
      return;
    }

    // Check if current interaction has choices (Player character with dialogue choices)
    const hasChoices = currentInteraction.character_name === 'Player' && (
      Array.isArray(currentInteraction.dialogue) || 
      (typeof currentInteraction.dialogue === 'object' && currentInteraction.dialogue.choices)
    );
    
    if (hasChoices) {
      log('Player choices detected', currentInteraction.dialogue);
      
      // Handle new format vs legacy format
      let choicesData;
      if (Array.isArray(currentInteraction.dialogue)) {
        // Legacy format - convert to new format
        choicesData = {
          type: 'conversational',
          prompt: 'Choose your response:',
          choices: currentInteraction.dialogue.map(text => ({
            text: text,
            outcome: 'next'
          }))
        };
      } else {
        // New format
        choicesData = currentInteraction.dialogue;
      }
      
      setGameState(prev => ({
        ...prev,
        choices: choicesData,
        showChoices: true,
        isTextComplete: true,
      }));
      return;
    }

    log('Regular interaction advancement (not player choice)', {
      character: currentInteraction.character_name,
      isArray: Array.isArray(currentInteraction.dialogue),
    });

    // Regular advancement
    advanceToNext();
  }, [gameState, getCurrentScene, getCurrentInteraction, log]);

  const handleChoice = useCallback((choiceIndex) => {
    const choices = gameState.choices;
    if (!choices) {
      log('No choices available', null, 'error');
      return;
    }

    // Handle both legacy (array) and new (object) formats
    const selectedChoice = Array.isArray(choices) 
      ? { text: choices[choiceIndex], outcome: 'next' }
      : choices.choices[choiceIndex];
    
    if (!selectedChoice) {
      log('Invalid choice selection', { choiceIndex, availableChoices: choices }, 'error');
      return;
    }

    log('Player chose option', {
      choiceIndex,
      choice: selectedChoice.text,
      outcome: selectedChoice.outcome,
    });

    const scene = getCurrentScene();
    if (!scene) {
      log('Cannot advance after choice: No current scene', null, 'warn');
      return;
    }

    // Hide choices first
    setGameState(prev => ({
      ...prev,
      showChoices: false,
      choices: null,
    }));

    // Handle different outcomes
    setTimeout(() => {
      switch (selectedChoice.outcome) {
        case 'replay':
          log('Replaying previous dialogue', {
            currentIndex: gameState.currentInteractionIndex,
            willGoTo: gameState.currentInteractionIndex > 0 ? gameState.currentInteractionIndex - 1 : gameState.currentInteractionIndex
          });
          // Go back to previous interaction and replay it
          if (gameState.currentInteractionIndex > 0) {
            setGameState(prev => ({
              ...prev,
              currentInteractionIndex: prev.currentInteractionIndex - 1,
              isTextComplete: false,
            }));
          } else {
            // If we're at the beginning of scene, just replay current
            log('At beginning of scene, replaying current interaction');
            setGameState(prev => ({
              ...prev,
              isTextComplete: false,
            }));
          }
          break;
          
        case 'correct':
          log('Correct answer - showing encouragement');
          handleCorrectAnswer();
          break;
          
        case 'wrong':
          log('Wrong answer - showing correction sequence');
          handleWrongAnswer();
          break;
          
        case 'next':
        default:
          log('Normal advancement after choice');
          advanceToNext();
          break;
      }
    }, 300);
  }, [gameState.choices, gameState.currentInteractionIndex, getCurrentScene, log]);

  const handleCorrectAnswer = useCallback(() => {
    // Insert a temporary interaction for correct response
    const encouragementMessages = [
      "Excellent! You understand the concept perfectly.",
      "That's absolutely right! Well done.", 
      "Perfect! You've grasped the key principle.",
      "Outstanding! Your understanding is impressive."
    ];
    
    const randomMessage = encouragementMessages[Math.floor(Math.random() * encouragementMessages.length)];
    
    setGameState(prev => ({
      ...prev,
      tempInteraction: {
        character_name: 'Kurisu',
        dialogue: randomMessage,
        character_expression: 'happy',
        isTemporary: true
      },
      isTextComplete: false,
    }));
  }, []);

  const handleWrongAnswer = useCallback(() => {
    // Insert temporary interactions for wrong answer sequence
    const correctionMessages = [
      "That's not quite right, but don't worry!",
      "Not exactly, but that's okay!",
      "That's not correct, but learning is a process!"
    ];
    
    const encouragementMessages = [
      "Every mistake is a learning opportunity. Let's continue!",
      "Understanding comes with practice. You're doing great!",
      "Don't worry, even scientists make mistakes. That's how we learn!"
    ];
    
    const correctionMessage = correctionMessages[Math.floor(Math.random() * correctionMessages.length)];
    const encouragementMessage = encouragementMessages[Math.floor(Math.random() * encouragementMessages.length)];
    
    setGameState(prev => ({
      ...prev,
      tempInteractionSequence: [
        {
          character_name: 'Kurisu',
          dialogue: correctionMessage,
          character_expression: 'sad',
          isTemporary: true
        },
        {
          character_name: 'Kurisu', 
          dialogue: encouragementMessage,
          character_expression: 'happy',
          isTemporary: true
        }
      ],
      tempInteractionIndex: 0,
      isTextComplete: false,
    }));
  }, []);

  const advanceToNext = useCallback(() => {
    const scene = getCurrentScene();
    
    // Check if we're at the end of current scene
    if (gameState.currentInteractionIndex >= scene.interactions.length - 1) {
      // Move to next scene
      if (gameState.currentSceneIndex < gameState.script.script.length - 1) {
        log('Moving to next scene after choice', {
          from: scene.scene_name,
          to: gameState.script.script[gameState.currentSceneIndex + 1]?.scene_name,
        });
        
        setGameState(prev => ({
          ...prev,
          currentSceneIndex: prev.currentSceneIndex + 1,
          currentInteractionIndex: 0,
          isTextComplete: false,
        }));
      } else {
        log('Reached end of script after choice');
        setGameState(prev => ({
          ...prev,
          isGameComplete: true,
        }));
      }
    } else {
      // Move to next interaction in current scene
      log('Moving to next interaction after choice');
      setGameState(prev => ({
        ...prev,
        currentInteractionIndex: prev.currentInteractionIndex + 1,
        isTextComplete: false,
      }));
    }
  }, [gameState.currentInteractionIndex, gameState.currentSceneIndex, gameState.script, getCurrentScene, log]);

  const handleTextComplete = useCallback(() => {
    log('Text display completed');
    setGameState(prev => ({
      ...prev,
      isTextComplete: true,
    }));
  }, [log]);

  // Handle TTS for dialogue
  const playDialogueTTS = useCallback(async (dialogue, language, characterName) => {
    if (!settings.ttsEnabled || !dialogue || typeof dialogue !== 'string') {
      return;
    }

    try {
      await TTSService.playDialogueAudio(
        dialogue,
        language || 'en',
        gameState.currentSceneIndex,
        gameState.currentInteractionIndex,
        characterName
      );
    } catch (error) {
      log('Failed to play TTS audio', error, 'error');
    }
  }, [settings.ttsEnabled, gameState.currentSceneIndex, gameState.currentInteractionIndex, log]);

  // Handle TTS for choice prompts (accessibility feature)
  const playChoicePromptTTS = useCallback(async (prompt, language) => {
    if (!settings.ttsEnabled || !prompt) {
      return;
    }

    try {
      await TTSService.playChoicePromptAudio(
        prompt,
        language || 'en',
        gameState.currentSceneIndex,
        gameState.currentInteractionIndex
      );
    } catch (error) {
      log('Failed to play choice prompt TTS', error, 'error');
    }
  }, [settings.ttsEnabled, gameState.currentSceneIndex, gameState.currentInteractionIndex, log]);

  // Effect to handle dialogue TTS when interaction changes
  useEffect(() => {
    const currentInteraction = getCurrentInteraction();
    if (!currentInteraction) {
      return;
    }

    const scriptLanguage = gameState.script?.language || 'en';
    
    // Handle regular dialogue
    if (typeof currentInteraction.dialogue === 'string') {
      playDialogueTTS(currentInteraction.dialogue, scriptLanguage, currentInteraction.character_name);
    }
    // Handle choice prompts (for accessibility)
    else if (currentInteraction.dialogue && currentInteraction.dialogue.prompt) {
      playChoicePromptTTS(currentInteraction.dialogue.prompt, scriptLanguage);
    }
  }, [getCurrentInteraction, gameState.script?.language, playDialogueTTS, playChoicePromptTTS]);

  const toggleTTS = useCallback(() => {
    setSettings(prev => {
      const newTTSEnabled = !prev.ttsEnabled;
      TTSService.toggleTTS();
      log(`TTS ${newTTSEnabled ? 'enabled' : 'disabled'}`);
      return {
        ...prev,
        ttsEnabled: newTTSEnabled,
      };
    });
  }, [log]);

  const toggleMute = useCallback(() => {
    setSettings(prev => {
      const newMuted = !prev.isMuted;
      log(`Audio ${newMuted ? 'muted' : 'unmuted'}`);
      return { ...prev, isMuted: newMuted };
    });
  }, [log]);

  const restartGame = useCallback(() => {
    log('Restarting game');
    setGameState(prev => ({
      ...prev,
      currentSceneIndex: 0,
      currentInteractionIndex: 0,
      isGameComplete: false,
      showChoices: false,
      choices: null,
      isTextComplete: false,
    }));
  }, [log]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event) => {
      switch (event.key) {
        case ' ':
        case 'Enter':
          event.preventDefault();
          if (gameState.isGameComplete) {
            restartGame();
          } else if (gameState.showChoices) {
            log('Cannot advance with spacebar: choices are shown');
          } else if (gameState.isTextComplete) {
            advanceInteraction();
          }
          break;
        case 'Escape':
          if (gameState.isGameComplete) {
            restartGame();
          } else {
            setGameState(prev => ({ ...prev, showChoices: false, choices: null }));
          }
          break;
        case 'm':
        case 'M':
          toggleMute();
          break;
        case 't':
        case 'T':
          toggleTTS();
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [gameState.showChoices, gameState.isTextComplete, gameState.isGameComplete, advanceInteraction, toggleMute, toggleTTS, restartGame, log]);

  // Cleanup TTS on unmount
  useEffect(() => {
    return () => {
      TTSService.cleanup();
    };
  }, []);

  // Loading screen
  if (gameState.isLoading) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center">
        <div className="text-white text-xl animate-pulse">
          Loading Visual Novel...
        </div>
      </div>
    );
  }

  // Error state
  if (!gameState.script) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center">
        <div className="text-red-500 text-xl">
          Failed to load script. Check console for details.
        </div>
      </div>
    );
  }

  // Game completion screen
  if (gameState.isGameComplete) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center">
        <Background />
        <div className="relative z-20 text-center animate-fade-in">
          <div className="vn-textbox mx-4 p-8 max-w-2xl">
            <h1 className="text-4xl font-bold text-white mb-6 animate-slide-up">
              🎉 Story Complete!
            </h1>
            <p className="text-xl text-gray-300 mb-8 animate-slide-up" style={{ animationDelay: '0.2s' }}>
              Thank you for experiencing this visual novel!
            </p>
            <div className="flex flex-col gap-4 items-center animate-slide-up" style={{ animationDelay: '0.4s' }}>
              <button
                onClick={restartGame}
                className="vn-choice-button px-8 py-4 rounded-lg text-white text-xl font-semibold transition-all duration-300 hover:scale-105"
              >
                🔄 Play Again
              </button>
              <div className="text-gray-400 text-sm mt-4">
                Press Space or click the button to restart
              </div>
            </div>
          </div>
        </div>
        
        {/* UI Controls still available */}
        <div className="absolute top-4 right-4 flex gap-2">
          <button
            onClick={toggleMute}
            className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
            title={settings.isMuted ? 'Unmute' : 'Mute'}
          >
            {settings.isMuted ? <FaVolumeMute /> : <FaVolumeUp />}
          </button>
        </div>
      </div>
    );
  }

  const currentScene = getCurrentScene();
  const currentInteraction = getCurrentInteraction();

  if (!currentScene || !currentInteraction) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center">
        <div className="text-white text-xl">
          Game Complete or Error Loading Scene
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      {/* Audio Manager */}
      <AudioManager
        currentMusic={currentScene.scene_music}
        volume={settings.isMuted ? 0 : settings.musicVolume}
        onError={(error) => log('Audio error', error, 'error')}
      />

      {/* Background */}
      <Background />

      {/* Character Display */}
      <CharacterDisplay
        character={currentInteraction.character_name}
        expression={currentInteraction.character_expression}
        onError={(error) => log('Character display error', error, 'error')}
      />

      {/* Text Box */}
      <TextBox
        character={currentInteraction.character_name}
        dialogue={
          // Handle different dialogue formats
          Array.isArray(currentInteraction.dialogue) 
            ? 'Choose your response...'
            : typeof currentInteraction.dialogue === 'object' && currentInteraction.dialogue.prompt
            ? currentInteraction.dialogue.prompt
            : typeof currentInteraction.dialogue === 'string'
            ? currentInteraction.dialogue
            : 'Choose your response...'
        }
        onTextComplete={handleTextComplete}
        onAdvance={advanceInteraction}
        canAdvance={gameState.isTextComplete && !gameState.showChoices}
        textSpeed={settings.textSpeed}
      />

      {/* Choice Menu */}
      {gameState.showChoices && gameState.choices && (
        <ChoiceMenu
          choices={gameState.choices}
          onChoice={handleChoice}
        />
      )}

      {/* UI Controls */}
      <div className="absolute top-4 right-4 flex gap-2">
        <button
          onClick={toggleMute}
          className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
          title={settings.isMuted ? 'Unmute' : 'Mute'}
        >
          {settings.isMuted ? <FaVolumeMute /> : <FaVolumeUp />}
        </button>
        
        <button
          onClick={toggleTTS}
          className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
          title={settings.ttsEnabled ? 'Disable TTS' : 'Enable TTS'}
        >
          {settings.ttsEnabled ? <FaMicrophone /> : <FaMicrophoneSlash />}
        </button>
        
        <button
          onClick={() => setDebugMode(!debugMode)}
          className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-all"
          title="Toggle Debug Mode"
        >
          <FaCog />
        </button>
      </div>

      {/* Debug Info */}
      {debugMode && (
        <div className="absolute top-4 left-4 bg-black bg-opacity-70 text-white p-3 rounded text-sm font-mono">
          <div>Scene: {gameState.currentSceneIndex + 1}/{gameState.script.script.length}</div>
          <div>Interaction: {gameState.currentInteractionIndex + 1}/{currentScene.interactions.length}</div>
          <div>Character: {currentInteraction.character_name}</div>
          <div>Expression: {currentInteraction.character_expression}</div>
          <div>Music: {currentScene.scene_music}</div>
          <div>Language: {gameState.script.language || 'en'}</div>
          <div>TTS: {settings.ttsEnabled ? 'On' : 'Off'}</div>
          <div>Text Complete: {gameState.isTextComplete ? 'Yes' : 'No'}</div>
          <div>Show Choices: {gameState.showChoices ? 'Yes' : 'No'}</div>
          <div>Game Complete: {gameState.isGameComplete ? 'Yes' : 'No'}</div>
          <div className="mt-2 text-xs">
            Controls: Space/Enter = Advance, M = Mute, T = TTS, Esc = Cancel Choices
          </div>
        </div>
      )}

      {/* Language Switcher */}
      <LanguageSwitcher 
        onLanguageChange={(newLanguage) => {
          log(`Language changed to: ${newLanguage}`);
          // Reload the page to switch to new language content
          window.location.reload();
        }}
      />
    </div>
  );
};

export default VNEngine;