#!/usr/bin/env python3
"""
TTS Server for Visual Novel Engine
Generates and serves audio files for dialogue using multi-language TTS
"""

import os
import sys
import hashlib
import requests
import urllib3
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# Configuration
LANG_MAP_TTS = {
    "hi": {
        "tts_endpoint": "https://canvas.iiit.ac.in/sandboxbeprod/generate_tts/67bca89ae0b95a6a1ea34a92",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTY3ZDZiOTNlM2JlYzkwMWZkOTc3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.D_lwUftpnNSFbBs0_9uG4P86Z2p6kMZ9PC1GkqZd8mg"
    },
    "en": {
        "tts_endpoint": "https://canvas.iiit.ac.in/sandboxbeprod/generate_tts/67bca8b3e0b95a6a1ea34a93",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTY3ZDZiOTNlM2JlYzkwMWZkOTc3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.D_lwUftpnNSFbBs0_9uG4P86Z2p6kMZ9PC1GkqZd8mg"
    },
    "te": {
        "tts_endpoint": "https://canvas.iiit.ac.in/sandboxbeprod/generate_tts/68d2468f08531bc3c5ccf47d",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTY3ZDZiOTNlM2JlYzkwMWZkOTc3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.D_lwUftpnNSFbBs0_9uG4P86Z2p6kMZ9PC1GkqZd8mg"
    }
}

# Audio storage directory
AUDIO_DIR = Path("public/audio")

def ensure_directories():
    """Create audio directories for each language"""
    for lang in LANG_MAP_TTS.keys():
        lang_dir = AUDIO_DIR / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {lang_dir}")

def generate_filename(text, language, scene_index, interaction_index):
    """Generate consistent filename for audio"""
    # Create hash of text content
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
    return f"scene{scene_index}_int{interaction_index}_{text_hash}.wav"

def text_to_speech(text, language, gender="female"):
    """Generate speech from text using TTS API"""
    if language not in LANG_MAP_TTS:
        raise ValueError(f"Unsupported language: {language}")

    config = LANG_MAP_TTS[language]
    headers = {"access-token": config["token"], "Content-Type": "application/json"}
    payload = {"text": text, "gender": gender}

    try:
        print(f"🎤 Generating TTS for [{language}]: {text[:50]}...")
        
        response = requests.post(
            config["tts_endpoint"], 
            headers=headers, 
            json=payload, 
            verify=False, 
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            raise RuntimeError(f"TTS API failed: {data}")

        s3_url = data["data"]["s3_url"]
        
        # Download audio
        audio_response = requests.get(s3_url, verify=False, timeout=30)
        audio_response.raise_for_status()
        
        print(f"✅ TTS generated successfully")
        return audio_response.content
        
    except Exception as e:
        print(f"❌ TTS generation failed: {e}")
        raise

@app.route('/api/tts/generate', methods=['POST'])
def generate_tts():
    """Generate TTS audio for dialogue"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        scene_index = data.get('scene_index', 0)
        interaction_index = data.get('interaction_index', 0)
        gender = data.get('gender', 'female')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        if language not in LANG_MAP_TTS:
            return jsonify({"error": f"Unsupported language: {language}"}), 400
        
        # Generate filename
        filename = generate_filename(text, language, scene_index, interaction_index)
        filepath = AUDIO_DIR / language / filename
        
        # Check if file already exists
        if filepath.exists():
            print(f"📁 Audio file already exists: {filename}")
            return jsonify({
                "status": "success",
                "filename": filename,
                "url": f"/audio/{language}/{filename}",
                "cached": True
            })
        
        # Generate TTS
        audio_content = text_to_speech(text, language, gender)
        
        # Save to file
        with open(filepath, 'wb') as f:
            f.write(audio_content)
        
        print(f"💾 Audio saved: {filepath}")
        
        return jsonify({
            "status": "success", 
            "filename": filename,
            "url": f"/audio/{language}/{filename}",
            "cached": False
        })
        
    except Exception as e:
        print(f"❌ TTS endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<language>/<filename>')
def serve_audio(language, filename):
    """Serve audio files"""
    try:
        filepath = AUDIO_DIR / language / filename
        if not filepath.exists():
            return jsonify({"error": "Audio file not found"}), 404
            
        return send_file(filepath, mimetype='audio/wav')
        
    except Exception as e:
        print(f"❌ Error serving audio: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tts/languages')
def get_supported_languages():
    """Get list of supported TTS languages"""
    return jsonify({
        "languages": list(LANG_MAP_TTS.keys()),
        "default": "en"
    })

@app.route('/api/tts/status')
def tts_status():
    """Check TTS service status"""
    stats = {}
    for lang in LANG_MAP_TTS.keys():
        lang_dir = AUDIO_DIR / lang
        if lang_dir.exists():
            audio_files = list(lang_dir.glob("*.wav"))
            stats[lang] = {
                "directory": str(lang_dir),
                "files": len(audio_files),
                "total_size_mb": round(sum(f.stat().st_size for f in audio_files) / (1024*1024), 2)
            }
        else:
            stats[lang] = {"directory": str(lang_dir), "files": 0, "total_size_mb": 0}
    
    return jsonify({
        "status": "running",
        "supported_languages": list(LANG_MAP_TTS.keys()),
        "audio_stats": stats
    })

if __name__ == '__main__':
    print("🎤 Starting TTS Server for Visual Novel Engine")
    print("=" * 50)
    
    # Create directories
    ensure_directories()
    
    print(f"📁 Audio directory: {AUDIO_DIR.absolute()}")
    print(f"🌐 Supported languages: {list(LANG_MAP_TTS.keys())}")
    print("🚀 Starting server...")
    
    app.run(host='0.0.0.0', port=5001, debug=True)