#!/usr/bin/env python3
"""
Bhashini TTS Audio Pre-generation Script for WebRenPy VN Engine
Uses Bhashini API to generate high-quality TTS audio files
"""

import json
import os
import requests
import re
import base64
from pathlib import Path
import time

class BhashiniTTSAudioGenerator:
    def __init__(self, script_path, output_dir="public/audio"):
        self.script_path = script_path
        self.output_dir = output_dir
        self.audio_counter = 1
        self.audio_mapping = {}
        
        # Bhashini Configuration
        self.api_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
        self.auth_key = "DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w"
        
        # Service IDs for different language groups
        self.service_ids = {
            "indo_aryan": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4",
            "misc": "ai4bharat/indic-tts-coqui-misc-gpu--t4",
            "dravidian": "ai4bharat/indic-tts-coqui-dravidian-gpu--t4"
        }
        
        # Language to service mapping
        self.language_service_map = {
            "as": "indo_aryan", "bn": "indo_aryan", "gu": "indo_aryan", 
            "hi": "indo_aryan", "mr": "indo_aryan", "or": "indo_aryan", "pa": "indo_aryan",
            "brx": "misc", "en": "misc", "mni": "misc",
            "te": "dravidian", "ta": "dravidian", "ml": "dravidian", "kn": "dravidian"
        }
        
    def get_service_id(self, language):
        """Get the correct service ID for a language"""
        service_group = self.language_service_map.get(language)
        if not service_group:
            raise ValueError(f"Language '{language}' not supported")
        return self.service_ids[service_group]
        
    def sanitize_filename(self, text):
        """Extract first three words and sanitize for filename"""
        # Remove punctuation and extra spaces
        cleaned = re.sub(r'[^\w\s]', '', text)
        words = cleaned.split()[:3]
        return "_".join(words).lower()
    
    def get_voice_gender(self, character_name):
        """Return voice gender based on character"""
        if character_name.lower() == "player":
            return "male"
        else:
            return "female"
    
    def generate_tts_audio(self, text, language, voice_gender, output_path):
        """Generate TTS audio using Bhashini API"""
        try:
            # Get correct service ID
            service_id = self.get_service_id(language)
            
            # Prepare request
            headers = {
                "Authorization": self.auth_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {
                                "sourceLanguage": language
                            },
                            "serviceId": service_id,
                            "gender": voice_gender,
                            "speed": 1.0,
                            "samplingRate": 48000
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
            
            print(f"🎤 Generating TTS [{voice_gender}] for: \"{text[:50]}...\"")
            
            # Make API request
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract audio content
            if "pipelineResponse" in data:
                pipeline_response = data["pipelineResponse"][0]
                if pipeline_response.get("taskType") == "tts" and "audio" in pipeline_response:
                    audio_data = pipeline_response["audio"][0]
                    base64_content = audio_data.get("audioContent")
                    
                    if base64_content:
                        # Decode base64 audio
                        audio_bytes = base64.b64decode(base64_content)
                        
                        # Create directory if needed
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        
                        # Save audio file
                        with open(output_path, "wb") as f:
                            f.write(audio_bytes)
                        
                        print(f"✅ Generated: {output_path} ({len(audio_bytes)} bytes)")
                        return True
                    else:
                        print("❌ No audio content in response")
                        return False
                else:
                    print("❌ Invalid response structure")
                    return False
            else:
                print("❌ No pipelineResponse in response")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error generating TTS: {e}")
            return False
    
    def process_dialogue(self, dialogue, character_name, language):
        """Process a single dialogue and generate TTS audio"""
        if isinstance(dialogue, str):
            # Regular dialogue
            first_three = self.sanitize_filename(dialogue)
            voice_gender = self.get_voice_gender(character_name)
            filename = f"{language}_{first_three}_{self.audio_counter}.wav"
            output_path = os.path.join(self.output_dir, language, filename)
            
            if self.generate_tts_audio(dialogue, language, voice_gender, output_path):
                dialogue_key = f"{character_name}:{dialogue}"
                self.audio_mapping[dialogue_key] = filename
                self.audio_counter += 1
                # Add delay to avoid rate limiting
                time.sleep(0.5)
                return True
            return False
                
        elif isinstance(dialogue, dict) and dialogue.get("type"):
            # Choice dialogue
            prompt = dialogue.get("prompt", "")
            if prompt:
                first_three = self.sanitize_filename(prompt)
                voice_gender = self.get_voice_gender(character_name)
                filename = f"{language}_{first_three}_{self.audio_counter}.wav"
                output_path = os.path.join(self.output_dir, language, filename)
                
                if self.generate_tts_audio(prompt, language, voice_gender, output_path):
                    dialogue_key = f"{character_name}:{prompt}"
                    self.audio_mapping[dialogue_key] = filename
                    self.audio_counter += 1
                    # Add delay to avoid rate limiting
                    time.sleep(0.5)
                    return True
                return False
        
        return False
    
    def test_bhashini_connection(self, language):
        """Test if Bhashini API is accessible for the language"""
        try:
            service_id = self.get_service_id(language)
            
            headers = {
                "Authorization": self.auth_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {
                                "sourceLanguage": language
                            },
                            "serviceId": service_id,
                            "gender": "female",
                            "speed": 1.0,
                            "samplingRate": 48000
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": "Test connection"
                        }
                    ],
                    "audio": [
                        {
                            "audioContent": None
                        }
                    ]
                }
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "pipelineResponse" in data:
                    print(f"✅ Bhashini TTS connection successful for {language}")
                    return True
                else:
                    print(f"❌ Bhashini TTS returned invalid response for {language}")
                    return False
            else:
                print(f"❌ Bhashini TTS HTTP error for {language}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Bhashini TTS connection failed for {language}: {e}")
            return False
    
    def generate_all_audio(self):
        """Generate TTS audio for entire script using Bhashini"""
        # Load script
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading script: {e}")
            return False
        
        language = script_data.get("language", "en")
        
        # Check if language is supported
        if language not in self.language_service_map:
            print(f"❌ Language '{language}' not supported by Bhashini TTS")
            print(f"Available languages: {list(self.language_service_map.keys())}")
            return False
        
        # Test Bhashini connection first
        print(f"🔍 Testing Bhashini TTS API connection for {language}...")
        if not self.test_bhashini_connection(language):
            print(f"❌ Cannot connect to Bhashini TTS API for {language}")
            return False
        
        # Create output directory
        lang_dir = os.path.join(self.output_dir, language)
        Path(lang_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"\n🎵 Generating TTS audio using Bhashini for language: {language}")
        print(f"📁 Output directory: {lang_dir}")
        print(f"🌐 Using service: {self.get_service_id(language)}")
        print()
        
        # Count total dialogues
        total_dialogues = 0
        for scene in script_data.get("script", []):
            for interaction in scene.get("interactions", []):
                dialogue = interaction.get("dialogue")
                if dialogue:
                    total_dialogues += 1
        
        print(f"📊 Total dialogues to process: {total_dialogues}")
        print("⏳ Generating audio files with Bhashini...")
        print()
        
        # Process all scenes and interactions
        current_dialogue = 0
        successful_generations = 0
        
        for scene in script_data.get("script", []):
            scene_name = scene.get("scene_name", "Unknown Scene")
            print(f"\n🎬 Processing scene: {scene_name}")
            
            for interaction in scene.get("interactions", []):
                character_name = interaction.get("character_name", "Unknown")
                dialogue = interaction.get("dialogue")
                
                if dialogue:
                    current_dialogue += 1
                    print(f"[{current_dialogue}/{total_dialogues}] Processing {character_name}...")
                    
                    if self.process_dialogue(dialogue, character_name, language):
                        successful_generations += 1
        
        # Save audio mapping
        mapping_path = os.path.join(self.output_dir, f"{language}_audio_mapping.json")
        try:
            with open(mapping_path, 'w', encoding='utf-8') as f:
                json.dump(self.audio_mapping, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Audio mapping saved to: {mapping_path}")
        except Exception as e:
            print(f"❌ Error saving mapping: {e}")
        
        print(f"\n🎉 Bhashini TTS audio generation complete!")
        print(f"📈 Successfully generated {successful_generations}/{total_dialogues} audio files")
        
        if successful_generations == total_dialogues:
            print(f"🎵 All audio files generated successfully using Bhashini!")
        elif successful_generations > 0:
            print(f"⚠️ Some audio files failed to generate. Check errors above.")
        else:
            print(f"❌ No audio files were generated. Check Bhashini API connection.")
        
        return successful_generations > 0

def main():
    import sys
    
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
    else:
        script_path = "public/script.json"
    
    if not os.path.exists(script_path):
        print(f"❌ Script file not found: {script_path}")
        return
    
    print("🎵 WebRenPy Bhashini TTS Audio Pre-Generator")
    print("=" * 55)
    print("🌟 Uses Bhashini API for high-quality TTS")
    print("🎤 Supports multiple Indian languages + English")
    print("⚡ Generates audio files for instant playback")
    print("🛡️ Reliable base64 audio handling")
    print()
    
    generator = BhashiniTTSAudioGenerator(script_path)
    
    # Show configuration
    with open(script_path, 'r') as f:
        script_data = json.load(f)
    language = script_data.get("language", "en")
    
    if language in generator.language_service_map:
        service_id = generator.get_service_id(language)
        print(f"✅ Bhashini TTS configuration found for '{language}'")
        print(f"🌐 Service: {service_id}")
        print()
        
        # Confirm before proceeding
        response = input("🚀 Start generating TTS audio with Bhashini? This may take several minutes. (y/N): ")
        if response.lower() in ['y', 'yes']:
            success = generator.generate_all_audio()
            if success:
                print("\n🎯 Audio generation completed successfully!")
                print("🎮 Your VN is now ready for instant audio playback!")
                print("🎧 Audio files are in high-quality WAV format")
            else:
                print("\n❌ Audio generation failed. Please check the errors above.")
        else:
            print("⏹️ Generation cancelled.")
    else:
        print(f"❌ Language '{language}' not supported by Bhashini TTS")
        print(f"Available languages: {list(generator.language_service_map.keys())}")

if __name__ == "__main__":
    main()