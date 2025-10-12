#!/usr/bin/env python3
"""
PDF to VN Pipeline - Complete Automated System
==============================================
Takes a research PDF and generates:
1. VN script in English 
2. Translated scripts (Hindi, Telugu)
3. Audio files for all languages

Usage: python pdf_to_vn_pipeline.py <pdf_path>
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from PyPDF2 import PdfReader
import google.generativeai as genai
import re
import unicodedata
from typing import Dict, List
import time

class PDFToVNPipeline:
    def __init__(self, pdf_path):
        # Handle relative path from research_paper folder
        if not os.path.isabs(pdf_path):
            # Get parent directory (Webrenpyvn)
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            research_paper_dir = os.path.join(parent_dir, "research_paper")
            self.pdf_path = os.path.join(research_paper_dir, pdf_path)
        else:
            self.pdf_path = pdf_path
            
        self.pdf_name = Path(self.pdf_path).stem
        
        # API Configuration
        self.gemini_api_key = "AIzaSyDMEZcOnWp2ke4Op_b_n6A0MMAgT7sPvPY"
        
        # Create output directory structure in parent Webrenpyvn folder
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_output_dir = os.path.join(parent_dir, "outputs")
        self.paper_output_dir = os.path.join(self.base_output_dir, self.pdf_name)
        
        # Language subdirectories
        self.lang_dirs = {
            "en": os.path.join(self.paper_output_dir, "en"),
            "hi": os.path.join(self.paper_output_dir, "hi"), 
            "te": os.path.join(self.paper_output_dir, "te")
        }
        
        # Audio subdirectories
        self.audio_dirs = {
            "en": os.path.join(self.lang_dirs["en"], "audio"),
            "hi": os.path.join(self.lang_dirs["hi"], "audio"),
            "te": os.path.join(self.lang_dirs["te"], "audio")
        }
        
        # Create all directories
        self.create_directory_structure()
        
        # File paths
        self.summary_file = os.path.join(self.paper_output_dir, "detailed_summary.txt")
        self.script_files = {
            "en": os.path.join(self.lang_dirs["en"], f"{self.pdf_name}_vn_script.json"),
            "hi": os.path.join(self.lang_dirs["hi"], f"{self.pdf_name}_vn_script_hi.json"),
            "te": os.path.join(self.lang_dirs["te"], f"{self.pdf_name}_vn_script_te.json")
        }
        
    def create_directory_structure(self):
        """Create all necessary directories"""
        print("📁 Creating directory structure...")
        
        # Create base directories
        for lang_dir in self.lang_dirs.values():
            Path(lang_dir).mkdir(parents=True, exist_ok=True)
            
        # Create audio directories
        for audio_dir in self.audio_dirs.values():
            Path(audio_dir).mkdir(parents=True, exist_ok=True)
            
        print(f"✅ Created output structure in: {self.paper_output_dir}")
        
    def extract_text_from_pdf(self):
        """Extract text from PDF"""
        print(f"📄 Extracting text from: {self.pdf_path}")
        
        try:
            reader = PdfReader(self.pdf_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("No text extracted from PDF")
                
            print(f"✅ Extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            print(f"❌ Error extracting PDF text: {e}")
            return None
            
    def clean_text(self, text):
        """Clean extracted text"""
        print("🧹 Cleaning extracted text...")
        
        # Remove unicode artifacts and normalize
        text = unicodedata.normalize('NFKD', text)
        
        # Clean up common PDF extraction issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines
        
        print("✅ Text cleaned")
        return text.strip()
        
    def extract_paper_metadata(self):
        """Extract basic metadata from PDF"""
        print("📋 Extracting paper metadata...")
        
        metadata = {
            "title": self.pdf_name.replace('_', ' ').title(),
            "authors": "Authors",
            "date": "2024"
        }
        
        # Try to extract title from first few lines of text if available
        try:
            with open(self.summary_file, 'r') as f:
                first_lines = f.read()[:500]
                # Simple heuristic for title extraction
                lines = first_lines.split('\n')
                for line in lines:
                    if len(line) > 10 and len(line) < 200:
                        if not line.startswith('Abstract') and not line.startswith('Introduction'):
                            metadata["title"] = line.strip()
                            break
        except:
            pass
            
        print(f"✅ Metadata: {metadata['title']}")
        return metadata
        
    def generate_summary(self, pdf_text):
        """Generate detailed summary using Gemini"""
        print("🤖 Generating detailed summary with Gemini AI...")
        
        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
*Role:* You are an expert academic summarizer and technical writer. Your goal is to create a comprehensive, highly accurate, and accessible summary of the provided research paper text.

*Instructions:*

1. *Coverage:* Summarize the entire paper, focusing on the core content: Introduction, Background, Methods, Results/Findings, Discussion, and Conclusion. *Explicitly exclude* the "References," "Bibliography," or "Resource" section.
2. *Structure:* Preserve the paper's original major section headings (e.g., "1. Introduction," "2. Methodology," "3. Experimental Results") in your summary, making them bold. If a section is very long, use relevant subheadings to break up the text for readability.
3. *Accuracy and Tone:* Maintain high factual accuracy. Do not introduce external information or speculation. The tone must be academic but accessible, ensuring complex concepts are explained clearly for a general but informed audience.
4. *Content Detail:*
   * *Introduction/Background:* State the research problem, its significance, and the paper's main contribution/hypothesis.
   * *Methods:* Briefly describe the experimental setup, data used, and key techniques/algorithms employed.
   * *Results/Findings:* State the main quantitative and qualitative findings clearly. Highlight the most significant results.
   * *Discussion/Conclusion:* Summarize the implications of the findings, their limitations, and suggested future work.
5. *Output Format:* Present the summary in a clear, well-structured text format, using markdown for headings.

*Paper Text to Summarize:*
{pdf_text}
"""

        try:
            response = model.generate_content(prompt)
            summary = response.text
            
            # Save summary
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                metadata = self.extract_paper_metadata()
                f.write(f"--- DETAILED ACADEMIC SUMMARY ---\n")
                f.write(f"Title: {metadata['title']}\n")
                f.write(f"Authors: {metadata['authors']}\n") 
                f.write(f"Date: {metadata['date']}\n")
                f.write("-" * 40 + "\n\n")
                f.write(summary)
                
            print(f"✅ Summary generated and saved to: {self.summary_file}")
            return summary
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return None
            
    def generate_vn_script(self):
        """Generate VN script from summary"""
        print("🎮 Generating VN script with Gemini AI...")
        
        # Read summary
        try:
            with open(self.summary_file, 'r', encoding='utf-8') as f:
                summary_content = f.read()
        except Exception as e:
            print(f"❌ Error reading summary: {e}")
            return False
            
        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=self.get_vn_generation_prompt()
        )
        
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        main_prompt = f"""
        --- ACADEMIC SUMMARY TEXT START ---
        {summary_content}
        --- ACADEMIC SUMMARY TEXT END ---
        """
        
        try:
            response = model.generate_content(
                contents=[main_prompt],
                generation_config=generation_config
            )
            
            json_output = response.text
            script_data = json.loads(json_output)
            
            # Add language metadata
            script_data["language"] = "en"
            
            # Save English script
            with open(self.script_files["en"], 'w', encoding='utf-8') as f:
                json.dump(script_data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ VN script generated and saved to: {self.script_files['en']}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating VN script: {e}")
            return False
            
    def translate_script(self, target_lang):
        """Translate script to target language"""
        print(f"🌍 Translating script to {target_lang.upper()}...")
        
        try:
            # Get absolute paths within the Asset generation pipeline
            script_path = os.path.abspath(self.script_files["en"])
            current_dir = os.path.dirname(os.path.abspath(__file__))
            translate_script_path = os.path.join(current_dir, "translate_vn_script.py")
            
            # Run translation script from current directory
            cmd = [
                "python3", 
                translate_script_path,
                script_path,
                target_lang
            ]
            
            print(f"🔧 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=current_dir)
            
            if result.returncode == 0:
                # Look for translated file in translated_scripts directory within current folder
                script_basename = os.path.basename(self.script_files["en"]).replace('.json', '')
                translated_scripts_dir = os.path.join(current_dir, "translated_scripts")
                translated_file = os.path.join(translated_scripts_dir, f"{script_basename}_{target_lang}.json")
                
                print(f"🔍 Looking for translated file: {translated_file}")
                
                if os.path.exists(translated_file):
                    # Copy to proper location
                    shutil.copy2(translated_file, self.script_files[target_lang])
                    print(f"✅ Translation to {target_lang.upper()} completed")
                    return True
                else:
                    print(f"❌ Translation file not found: {translated_file}")
                    # List what files exist in translated_scripts
                    if os.path.exists(translated_scripts_dir):
                        files = os.listdir(translated_scripts_dir)
                        print(f"📂 Files in translated_scripts: {files}")
                    return False
            else:
                print(f"❌ Translation failed: {result.stderr}")
                print(f"📤 Translation stdout: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"❌ Error translating to {target_lang}: {e}")
            return False
            
    def generate_audio(self, lang):
        """Generate audio for a language"""
        print(f"🎵 Generating {lang.upper()} audio files...")
        
        try:
            # Get absolute paths within the Asset generation pipeline
            script_path = os.path.abspath(self.script_files[lang])
            current_dir = os.path.dirname(os.path.abspath(__file__))
            audio_script_path = os.path.join(current_dir, "generate_bhashini_tts_audio.py")
            
            # Run audio generation script from current directory
            cmd = [
                "python3",
                audio_script_path, 
                script_path,
                lang
            ]
            
            print(f"🔧 Running: {' '.join(cmd)}")
            
            # Run with input to auto-confirm
            process = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=current_dir
            )
            
            # Send 'y' to confirm audio generation
            stdout, stderr = process.communicate(input='y\n')
            
            print(f"📤 Audio generation stdout: {stdout[-500:]}")  # Last 500 chars
            if stderr:
                print(f"📤 Audio generation stderr: {stderr[-500:]}")
            
            if process.returncode == 0:
                # Move audio files to proper location
                source_audio_dir = os.path.join(current_dir, "public", "audio", lang)
                target_audio_dir = self.audio_dirs[lang]
                
                print(f"🔍 Looking for audio files in: {source_audio_dir}")
                
                if os.path.exists(source_audio_dir):
                    # Copy audio files
                    audio_files = [f for f in os.listdir(source_audio_dir) if f.endswith('.wav')]
                    print(f"📂 Found {len(audio_files)} audio files")
                    
                    for file in audio_files:
                        shutil.copy2(
                            os.path.join(source_audio_dir, file),
                            os.path.join(target_audio_dir, file)
                        )
                    
                    # Copy audio mapping
                    mapping_file = os.path.join(current_dir, "public", "audio", f"{lang}_audio_mapping.json")
                    if os.path.exists(mapping_file):
                        shutil.copy2(mapping_file, os.path.join(self.lang_dirs[lang], f"{lang}_audio_mapping.json"))
                        
                    print(f"✅ Audio generation for {lang.upper()} completed - {len(audio_files)} files")
                    return True
                else:
                    print(f"❌ Audio directory not found: {source_audio_dir}")
                    return False
            else:
                print(f"❌ Audio generation failed with return code: {process.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating audio for {lang}: {e}")
            return False
            
    def get_vn_generation_prompt(self):
        """Get the VN generation system prompt"""
        return """
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

    def copy_to_public_directory(self):
        """Copy generated outputs to public directory for React server access"""
        print("📋 Copying outputs to public directory for web access...")
        
        try:
            # Get parent directory (Webrenpyvn)
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            public_outputs_dir = os.path.join(parent_dir, "public", "outputs")
            
            # Create public/outputs directory if it doesn't exist
            Path(public_outputs_dir).mkdir(parents=True, exist_ok=True)
            
            # Copy the entire paper output directory to public/outputs
            target_dir = os.path.join(public_outputs_dir, self.pdf_name)
            
            # Remove existing directory if it exists
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            
            # Copy the entire directory
            shutil.copytree(self.paper_output_dir, target_dir)
            
            print(f"✅ Outputs copied to: {target_dir}")
            print(f"🌐 Files now accessible via React dev server at: /outputs/{self.pdf_name}/")
            
            return True
            
        except Exception as e:
            print(f"❌ Error copying to public directory: {e}")
            return False

    def run_pipeline(self):
        """Run the complete pipeline"""
        print("🚀 Starting PDF to VN Pipeline")
        print("=" * 50)
        print(f"📄 Input PDF: {self.pdf_path}")
        print(f"📁 Output Directory: {self.paper_output_dir}")
        print("=" * 50)
        
        # Step 1: Extract and clean PDF text
        pdf_text = self.extract_text_from_pdf()
        if not pdf_text:
            print("❌ Pipeline failed at PDF extraction")
            return False
            
        pdf_text = self.clean_text(pdf_text)
        
        # Step 2: Generate summary
        summary = self.generate_summary(pdf_text)
        if not summary:
            print("❌ Pipeline failed at summary generation")
            return False
            
        # Step 3: Generate English VN script
        if not self.generate_vn_script():
            print("❌ Pipeline failed at VN script generation")
            return False
            
        # Step 4: Translate to Hindi and Telugu
        for lang in ["hi", "te"]:
            if not self.translate_script(lang):
                print(f"❌ Pipeline failed at {lang.upper()} translation")
                return False
                
        # Step 5: Generate audio for all languages
        for lang in ["en", "hi", "te"]:
            if not self.generate_audio(lang):
                print(f"❌ Pipeline failed at {lang.upper()} audio generation")
                return False
                
        # Step 6: Generate summary report
        self.generate_summary_report()
        
        # Step 7: Copy outputs to public directory for React server access
        if not self.copy_to_public_directory():
            print("❌ Pipeline failed at copying to public directory")
            return False
        
        print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"📁 All outputs saved in: {self.paper_output_dir}")
        print("\n📋 Generated files:")
        for lang in ["en", "hi", "te"]:
            print(f"  {lang.upper()}:")
            print(f"    📄 Script: {os.path.relpath(self.script_files[lang])}")
            print(f"    🎵 Audio:  {os.path.relpath(self.audio_dirs[lang])}")
        print("\n✅ Ready for VN integration!")
        print("🌐 Files accessible via React dev server!")
        
        return True
        
    def generate_summary_report(self):
        """Generate a summary report of the pipeline results"""
        report_file = os.path.join(self.paper_output_dir, "pipeline_report.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"PDF to VN Pipeline Report\n")
            f.write(f"========================\n\n")
            f.write(f"Source PDF: {self.pdf_path}\n")
            f.write(f"Paper Name: {self.pdf_name}\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Generated Files:\n")
            f.write(f"---------------\n")
            
            for lang in ["en", "hi", "te"]:
                f.write(f"\n{lang.upper()} Language:\n")
                f.write(f"  Script: {os.path.basename(self.script_files[lang])}\n")
                
                # Count audio files
                audio_dir = self.audio_dirs[lang]
                if os.path.exists(audio_dir):
                    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
                    f.write(f"  Audio Files: {len(audio_files)} WAV files\n")
                    
                    # Calculate total size
                    total_size = sum(os.path.getsize(os.path.join(audio_dir, f)) for f in audio_files)
                    f.write(f"  Audio Size: {total_size / (1024*1024):.1f} MB\n")
                else:
                    f.write(f"  Audio Files: 0\n")
                    
        print(f"📊 Pipeline report saved to: {report_file}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_vn_pipeline.py <pdf_filename>")
        print("\nExample:")
        print("  python pdf_to_vn_pipeline.py 2509.21175v1.pdf")
        print("\nNote: PDF files should be placed in ../research_paper/ folder")
        print("      Outputs will be generated in ../outputs/ folder")
        sys.exit(1)
        
    pdf_filename = sys.argv[1]
    
    # Create pipeline instance (handles path resolution)
    pipeline = PDFToVNPipeline(pdf_filename)
    
    # Check if the resolved PDF path exists
    if not os.path.exists(pipeline.pdf_path):
        print(f"❌ PDF file not found: {pipeline.pdf_path}")
        print(f"💡 Place your PDF file in the research_paper folder as: ../research_paper/{pdf_filename}")
        sys.exit(1)
        
    print(f"📖 Processing PDF: {pipeline.pdf_path}")
    print(f"📁 Output directory: {pipeline.paper_output_dir}")
    
    success = pipeline.run_pipeline()
    
    if success:
        print("\n🎯 Pipeline completed successfully!")
        print(f"📂 Check outputs in: {pipeline.paper_output_dir}")
        sys.exit(0)
    else:
        print("\n💥 Pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()