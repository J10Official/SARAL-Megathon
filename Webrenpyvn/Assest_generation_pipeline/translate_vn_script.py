#!/usr/bin/env python3
"""
VN Script Translator
Translates dialogue content in visual novel scripts to target languages using Bhashini API.

Usage:
    python translate_vn_script.py <script_file> <target_language>
    
Examples:
    python translate_vn_script.py script.json hi
    python translate_vn_script.py generated.json te
    python translate_vn_script.py generated.json ta
    
Supported languages: en, as, bn, brx, doi, gom, gu, hi, kn, ks, mai, ml, mni, mr, ne, or, pa, sa, sat, sd, ta, te, ur
"""

import json
import sys
import os
import requests
from pathlib import Path

# Bhashini API Configuration
BHASHINI_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
BHASHINI_AUTH_KEY = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"

# Supported language codes for Bhashini MT
SUPPORTED_LANGUAGES = [
    "en", "as", "bn", "brx", "doi", "gom", "gu", "hi", "kn", "ks", 
    "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat", "sd", 
    "ta", "te", "ur"
]

def translate_text(text: str, target_lang: str):
    """Translate text using Bhashini API"""
    if target_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {target_lang}. Supported: {SUPPORTED_LANGUAGES}")
    
    headers = {
        "Authorization": BHASHINI_AUTH_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": "en",
                        "targetLanguage": target_lang
                    },
                    "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
                    "numTranslation": "True"
                }
            }
        ],
        "inputData": {
            "input": [
                {
                    "source": text
                }
            ],
            "audio": [
                {
                    "audioContent": None
                }
            ]
        }
    }
    
    try:
        response = requests.post(BHASHINI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract translated text from Bhashini response
        if "pipelineResponse" in data and len(data["pipelineResponse"]) > 0:
            pipeline_response = data["pipelineResponse"][0]
            if "output" in pipeline_response and len(pipeline_response["output"]) > 0:
                return pipeline_response["output"][0]["target"]
        
        print(f"Translation API error: {data}")
        return text  # Return original text if translation fails
            
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        return text  # Return original text if translation fails

def translate_dialogue_recursive(obj, target_lang: str, translated_count: list):
    """Recursively find and translate dialogue content"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "dialogue" and isinstance(value, str):
                # Translate string dialogue
                original = value
                translated = translate_text(original, target_lang)
                obj[key] = translated
                translated_count[0] += 1
                print(f"Translated {translated_count[0]}: '{original[:50]}...' -> '{translated[:50]}...'")
            elif key == "dialogue" and isinstance(value, dict):
                # Handle choice dialogue objects
                if "prompt" in value:
                    original_prompt = value["prompt"]
                    translated_prompt = translate_text(original_prompt, target_lang)
                    value["prompt"] = translated_prompt
                    translated_count[0] += 1
                    print(f"Translated prompt {translated_count[0]}: '{original_prompt[:50]}...'")
                
                # Translate choice text
                if "choices" in value and isinstance(value["choices"], list):
                    for choice in value["choices"]:
                        if "text" in choice:
                            original_text = choice["text"]
                            translated_text = translate_text(original_text, target_lang)
                            choice["text"] = translated_text
                            translated_count[0] += 1
                            print(f"Translated choice {translated_count[0]}: '{original_text}'")
            else:
                # Recursively process nested objects
                translate_dialogue_recursive(value, target_lang, translated_count)
    elif isinstance(obj, list):
        for item in obj:
            translate_dialogue_recursive(item, target_lang, translated_count)

def translate_vn_script(input_file: str, target_lang: str):
    """Translate VN script to target language"""
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return
    
    if target_lang not in SUPPORTED_LANGUAGES:
        print(f"Error: Unsupported language '{target_lang}'. Supported: {SUPPORTED_LANGUAGES}")
        return
    
    print(f"Loading script: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        script_data = json.load(f)
    
    # Add language metadata to output
    script_data['language'] = target_lang
    
    print(f"Translating dialogue to {target_lang}...")
    translated_count = [0]  # Use list to allow modification in nested function
    translate_dialogue_recursive(script_data, target_lang, translated_count)
    
    # Create output directory if it doesn't exist
    output_dir = "translated_scripts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output filename
    input_path = Path(input_file)
    output_filename = f"{input_path.stem}_{target_lang}.json"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save translated script
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Translation complete!")
    print(f"📊 Translated {translated_count[0]} dialogue entries")
    print(f"💾 Saved to: {output_path}")
    print(f"\nTo use: Copy {output_path} to public/script.json or use the script switcher")

def main():
    if len(sys.argv) != 3:
        print("Usage: python translate_vn_script.py <script_file> <target_language>")
        print("\nExamples:")
        print("  python translate_vn_script.py script.json hi")
        print("  python translate_vn_script.py generated.json te")
        print("  python translate_vn_script.py generated.json ta")
        print(f"\nSupported languages: {', '.join(SUPPORTED_LANGUAGES)}")
        sys.exit(1)
    
    script_file = sys.argv[1]
    target_lang = sys.argv[2].lower()
    
    translate_vn_script(script_file, target_lang)

if __name__ == "__main__":
    main()