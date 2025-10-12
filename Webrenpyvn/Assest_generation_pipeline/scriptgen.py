import os
import json
import google.generativeai as genai

# --- 1. Configuration ---
# ⚠ IMPORTANT: Replace the placeholder values below with your actual API key and file paths.

# Add your Gemini API Key here.
# For security, it's better to load this from an environment variable.
GEMINI_API_KEY = "AIzaSyDMEZcOnWp2ke4Op_b_n6A0MMAgT7sPvPY"

# The full path to the text file you want to process.
INPUT_TEXT_FILE = "/home/jatin/Code/Year3/Megathon/Webrenpyvn/Resaerchpdftoscript/detailed_summary_output.txt"

# The name of the file where the JSON output will be saved.
OUTPUT_JSON_FILE = "/home/jatin/Code/Year3/Megathon/Webrenpyvn/Resaerchpdftoscript/computational_humour_vn_script.json"


# --- 2. File Reading Function ---

def read_text_file(file_path):
    """Reads the content of a local text file and handles potential errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Successfully read file: {file_path}")
        return content
    except FileNotFoundError:
        print(f"❌ Error: The file was not found at {file_path}")
        return None
    except Exception as e:
        print(f"❌ An error occurred while reading the file: {e}")
        return None


# --- 3. Prompt and Instruction Setup ---
SYSTEM_INSTRUCTION = """ 
# Academic Paper to Visual Novel Conversion Prompt

## Task
Convert the provided academic paper summary into an interactive visual novel script format that makes complex concepts accessible through dialogue, character interactions, and meaningful choices.

## JSON Structure Required
json
{
  "script": [
    {
      "scene_name": "Chapter 1: Introduction",
      "scene_music": "ChillLofiR.mp3",
      "interactions": [
        {
          "character_name": "Kurisu",
          "dialogue": "Text content here",
          "character_expression": "happy",
          "image_displayed": "image.png"
        },
        {
          "character_name": "Player",
          "dialogue": {
            "type": "conversational",
            "prompt": "Choice prompt here",
            "choices": [
              {
                "text": "Choice option",
                "outcome": "next"
              }
            ]
          },
          "character_expression": "neutral",
          "image_displayed": "image.png"
        }
      ]
    }
  ]
}


## Restrictions
- *Expressions*: Only use "happy", "sad", "angry", "neutral"
- *Music*: Only use "ChillLofiR.mp3" 
- *Image*: Always use "image.png" 
- *Choice Types*: "conversational", "re-explanation", "question"
- *Outcomes*: "next", "replay", "correct", "wrong"

## Few-Shot Examples

### Example 1: Choice System Demo (Complete Scene)
json
{
  "scene_name": "Chapter 1: Testing the Choice System",
  "scene_music": "ChillLofiR.mp3",
  "interactions": [
    {
      "character_name": "Kurisu",
      "dialogue": "Welcome to the enhanced choice system! I'll demonstrate the three types of choices we now support.",
      "character_expression": "happy",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Kurisu",
      "dialogue": "Now let me explain quantum mechanics briefly. Quantum mechanics is the branch of physics that deals with the behavior of matter and energy at the molecular, atomic, nuclear, and even smaller microscopic levels.",
      "character_expression": "neutral",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Player",
      "dialogue": {
        "type": "re-explanation",
        "prompt": "Would you like me to explain quantum mechanics again?",
        "choices": [
          {
            "text": "Yes, please explain it again",
            "outcome": "replay"
          },
          {
            "text": "No, I understood it",
            "outcome": "next"
          }
        ]
      },
      "character_expression": "neutral",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Player",
      "dialogue": {
        "type": "question",
        "prompt": "What is the fundamental principle that quantum mechanics deals with?",
        "choices": [
          {
            "text": "The behavior of matter and energy at microscopic levels",
            "outcome": "correct"
          },
          {
            "text": "The movement of planets and stars",
            "outcome": "wrong"
          },
          {
            "text": "The chemistry of large molecules only",
            "outcome": "wrong"
          }
        ]
      },
      "character_expression": "neutral",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Player",
      "dialogue": {
        "type": "conversational",
        "prompt": "How do you feel about testing this new system?",
        "choices": [
          {
            "text": "I'm excited to see how it works!",
            "outcome": "next"
          },
          {
            "text": "I'm a bit nervous but curious.",
            "outcome": "next"
          },
          {
            "text": "Let's see what this can do!",
            "outcome": "next"
          }
        ]
      },
      "character_expression": "neutral",
      "image_displayed": "image.png"
    }
  ]
}


### Example 2: Simple Paper Explanation Scene
json
{
  "scene_name": "Chapter 1: Understanding Neural Networks",
  "scene_music": "ChillLofiR.mp3", 
  "interactions": [
    {
      "character_name": "Kurisu",
      "dialogue": "Hey there! Today we're going to explore a fascinating paper about neural networks. Think of neural networks like a simplified version of how your brain processes information!",
      "character_expression": "happy",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Kurisu",
      "dialogue": "The paper introduces a new type of neural network called a 'Transformer'. Unlike traditional networks that process information sequentially, transformers can look at all parts of the input simultaneously using something called 'attention'.",
      "character_expression": "neutral",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Player",
      "dialogue": {
        "type": "re-explanation",
        "prompt": "That sounds complex. Should I explain it with a simpler analogy?",
        "choices": [
          {
            "text": "Yes, please use a simpler explanation",
            "outcome": "replay"
          },
          {
            "text": "No, I think I understand the basics",
            "outcome": "next"
          }
        ]
      },
      "character_expression": "neutral",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Kurisu",
      "dialogue": "Imagine you're reading a book and trying to understand a sentence. Traditional neural networks would read word by word, left to right. But transformers are like having super-vision - they can focus on ALL words at once and understand how each word relates to every other word!",
      "character_expression": "happy",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Player",
      "dialogue": {
        "type": "question",
        "prompt": "What's the key advantage of transformers over traditional neural networks?",
        "choices": [
          {
            "text": "They can process all parts of input simultaneously",
            "outcome": "correct"
          },
          {
            "text": "They use less computer memory",
            "outcome": "wrong"
          },
          {
            "text": "They are simpler to understand",
            "outcome": "wrong"
          }
        ]
      },
      "character_expression": "neutral",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Player",
      "dialogue": {
        "type": "conversational",
        "prompt": "What would you like to explore next about transformers?",
        "choices": [
          {
            "text": "How do they apply to language translation?",
            "outcome": "next"
          },
          {
            "text": "What about their use in chatbots like me?",
            "outcome": "next"
          },
          {
            "text": "Tell me about the technical details",
            "outcome": "next"
          }
        ]
      },
      "character_expression": "neutral",
      "image_displayed": "image.png"
    },
    {
      "character_name": "Kurisu",
      "dialogue": "Excellent questions! This attention mechanism is what made modern AI possible - from language models to image recognition. The paper 'Attention Is All You Need' literally changed the entire field!",
      "character_expression": "happy",
      "image_displayed": "image.png"
    }
  ]
}


## Character Setup
- *Main Character*: Kurisu Makise (genius scientist from Steins;Gate)
- *Role*: Educational guide who explains concepts with enthusiasm and clarity
- *Personality*: Brilliant, slightly tsundere, passionate about science, uses analogies
- *Expressions*: Only use "neutral", "happy", "sad", "angry"

## Scene Structure Guidelines
Create 4-6 scenes that progressively build understanding:
1. *Introduction Scene*: Hook the reader, introduce the problem/motivation
2. *Foundation Scenes*: Core concepts broken into digestible parts  
3. *Deep Dive Scenes*: Complex details with interactive explanations
4. *Conclusion Scene*: Applications, implications, and future directions

## Choice Integration
Implement all three choice types strategically:

### Re-explanation Choices (type: "re-explanation")
- Trigger when introducing complex concepts
- Allow users to request simpler explanations
- Use analogies and real-world examples
- Always use outcome: "replay" or "next"

### Quiz Choices (type: "question") 
- Test understanding of key concepts
- Use outcome: "correct" for right answers, "wrong" for incorrect ones
- Provide clear, specific questions about the content

### Conversational Choices (type: "conversational")
- Explore different aspects of the topic
- Allow personalized learning paths
- Show practical applications
- Always use outcome: "next"

## Dialogue Style Guide
- *Kurisu's Voice*: Confident, scientific, but approachable
- *Explanations*: Start simple, build complexity gradually
- *Analogies*: Use everyday objects/situations to explain abstract concepts
- *Pacing*: Allow pauses for reflection, don't overwhelm
- *Engagement*: Ask rhetorical questions, show excitement about discoveries

## Technical Requirements
- Each scene should have 3-7 dialogue interactions
- Use scene_music: "ChillLofiR.mp3" for all scenes
- Use image_displayed: "image.png" for all interactions
- Character expressions: only "neutral", "happy", "sad", "angry"
- Choice outcomes: only "next", "replay", "correct", "wrong"
- Choice types: only "conversational", "re-explanation", "question"
- All interactions must have character_name, dialogue, character_expression, image_displayed
- Player choices must use the nested dialogue object format
- End with a satisfying conclusion that ties everything together
- All JSON must be valid and properly formatted

## Quality Checklist
- [ ] Complete JSON structure with "script" array containing scenes
- [ ] Complex concepts broken into understandable chunks
- [ ] All three choice types used appropriately  
- [ ] Character personality consistent throughout
- [ ] Scientific accuracy maintained while simplifying
- [ ] Engaging narrative that doesn't feel like a textbook
- [ ] Clear learning progression from basic to advanced concepts
- [ ] Only allowed expressions: neutral, happy, sad, angry
- [ ] Only allowed music: ChillLofiR.mp3
- [ ] Only allowed image: image.png
- [ ] Valid JSON syntax throughout
- [ ] Proper choice outcomes: next, replay, correct, wrong

---

*Input*: [Academic paper summary]
*Output*: Complete JSON script ready for the visual novel engine


"""
def main():
    file_content = read_text_file(INPUT_TEXT_FILE)
    if file_content is None:
        print("Script terminated due to file reading error.")
        return

    # FIX IS HERE: Create the prompt after reading the file
    main_prompt = f"""
    --- ACADEMIC SUMMARY TEXT START ---
    {file_content}
    --- ACADEMIC SUMMARY TEXT END ---
    """

    try:
        # Configure the Gemini API key
        genai.configure(api_key=GEMINI_API_KEY)

        # Create the generative model with the system instruction
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=SYSTEM_INSTRUCTION
        )

        # Set the generation configuration to enforce JSON output
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )

        # Call the API to generate the content
        print("Calling the Gemini API... 🤖")
        response = model.generate_content(
            contents=[main_prompt],
            generation_config=generation_config
        )

        # The response.text will be a valid JSON string
        json_output_str = response.text

        # Convert the JSON string to a Python dictionary for verification
        output_data = json.loads(json_output_str)

        # Save the dictionary to the output JSON file
        with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4)

        print("\n🎉 Success! Successfully processed the text and saved the JSON output.")
        print(f"Output saved to: {os.path.abspath(OUTPUT_JSON_FILE)}")

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check your API key, internet connection, and input file.")



# Run the main function when the script is executed
if __name__ == "__main__":
    main()
