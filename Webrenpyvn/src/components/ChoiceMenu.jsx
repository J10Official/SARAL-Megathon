import React from 'react';

const ChoiceMenu = ({ choices, onChoice }) => {
  const log = (message, data = null, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `🎯 [${timestamp}] ChoiceMenu:`;
    
    switch (level) {
      case 'error':
        console.error(`❌ ${prefix}`, message, data);
        break;
      default:
        console.log(`ℹ️ ${prefix}`, message, data);
    }
  };

  // Normalize choices data to handle both formats
  const normalizedChoices = React.useMemo(() => {
    if (!choices) return null;
    
    if (Array.isArray(choices)) {
      // Legacy format
      return {
        type: 'conversational',
        prompt: 'Choose your response:',
        choices: choices.map(text => ({ text, outcome: 'next' }))
      };
    } else if (choices.choices) {
      // New format
      return choices;
    }
    
    return null;
  }, [choices]);

  React.useEffect(() => {
    log('Choice menu displayed', { 
      choiceCount: normalizedChoices?.choices?.length || 0, 
      choices: normalizedChoices,
      type: normalizedChoices?.type 
    });
  }, [normalizedChoices]);

  const handleChoice = (index) => {
    const choice = normalizedChoices?.choices[index];
    log('Choice selected', { 
      index, 
      choice: choice?.text,
      outcome: choice?.outcome,
      type: normalizedChoices?.type
    });
    if (onChoice) {
      onChoice(index);
    }
  };

  if (!normalizedChoices?.choices || normalizedChoices.choices.length === 0) {
    log('No choices to display', choices, 'warn');
    return null;
  }

  return (
    <div className="absolute inset-0 flex items-center justify-center z-30 bg-black bg-opacity-40">
      <div className="bg-black bg-opacity-80 backdrop-filter backdrop-blur-lg rounded-lg p-6 mx-4 max-w-2xl w-full animate-slide-up">
        <div className="text-white text-xl font-semibold mb-4 text-center">
          {normalizedChoices.prompt || 'Choose your response:'}
        </div>
        
        {/* Choice type indicator */}
        {normalizedChoices.type && (
          <div className="text-gray-400 text-sm text-center mb-4">
            {normalizedChoices.type === 'question' && '🤔 Quiz Question'}
            {normalizedChoices.type === 're-explanation' && '🔄 Re-explanation'}
            {normalizedChoices.type === 'conversational' && '💬 Conversation'}
          </div>
        )}
        
        <div className="space-y-3">
          {normalizedChoices.choices.map((choice, index) => (
            <button
              key={index}
              onClick={() => handleChoice(index)}
              className="vn-choice-button w-full p-4 rounded-lg text-white text-left transition-all duration-300 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-400"
              style={{
                animationDelay: `${index * 0.1}s`,
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-blue-300 font-bold mr-3 text-lg">
                    {index + 1}.
                  </span>
                  <span className="text-lg">
                    {choice.text}
                  </span>
                </div>
                {choice.outcome && choice.outcome !== 'next' && (
                  <span className="text-xs text-gray-400 ml-2">
                    {choice.outcome === 'correct' && '✓'}
                    {choice.outcome === 'wrong' && '✗'}
                    {choice.outcome === 'replay' && '🔄'}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
        
        <div className="text-gray-400 text-sm text-center mt-4">
          Click a choice or press the number key
        </div>
      </div>
    </div>
  );
};

export default ChoiceMenu;