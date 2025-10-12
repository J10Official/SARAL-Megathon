# Asset Generation Pipeline

A comprehensive system for converting academic research papers into interactive Visual Novel experiences with multi-language support and high-quality text-to-speech audio generation.

## 🚀 Overview

This pipeline transforms PDF research papers into engaging Visual Novel scripts with:
- Automatic content extraction and summarization
- Interactive dialogue and choice systems
- Multi-language translation (English, Hindi, Telugu, and more)
- High-quality TTS audio generation using Bhashini API
- Complete asset management for VN engines

## 📋 Pipeline Components

### Core Scripts

1. **`pdf_to_vn_pipeline.py`** - Main orchestration script
   - Manages the complete PDF → VN conversion workflow
   - Handles directory structure creation
   - Coordinates all sub-processes
   - Generates summary reports

2. **`outlinegen.py`** - PDF processing and summarization
   - Extracts text from PDF documents
   - Generates structured summaries using Gemini AI
   - Prepares content for VN script generation

3. **`scriptgen.py`** - VN script creation
   - Converts summaries into interactive VN scripts
   - Creates character dialogues and choice systems
   - Formats output as JSON for VN engines

4. **`translate_vn_script.py`** - Multi-language translation
   - Translates VN scripts using Bhashini MT API
   - Supports 20+ languages across language families
   - Preserves script structure and formatting

5. **`generate_bhashini_tts_audio.py`** - Audio generation
   - Creates high-quality TTS audio using Bhashini API
   - Supports character-specific voice assignments
   - Generates 48kHz mono WAV files for optimal quality

### Support Files

- **`test_pipeline.py`** - Pipeline testing and validation
- **`README.md`** - This documentation

## 🛠️ Setup Requirements

### Dependencies
```bash
pip install PyPDF2 requests pathlib google-generativeai
```

### API Configuration
- **Gemini AI API Key**: Required for content generation
- **Bhashini API Key**: Required for translation and TTS
  - Authorization: `DveTyi8IJRxMNJdbUI0EhiE1X0yQYmoIiNLafiNLYbr4K0JCmDxFasFbOQQgkz7w`

## 📖 Usage

### Basic Usage
```bash
# Run complete pipeline on a PDF
python3 pdf_to_vn_pipeline.py path/to/research_paper.pdf

# Test pipeline integrity
python3 test_pipeline.py
```

### Individual Components
```bash
# Generate outline from PDF
python3 outlinegen.py path/to/paper.pdf

# Create VN script from outline
python3 scriptgen.py path/to/outline.txt

# Translate script to Hindi
python3 translate_vn_script.py path/to/script.json hi

# Generate audio for script
python3 generate_bhashini_tts_audio.py path/to/script.json en
```

## 📁 Output Structure

The pipeline creates organized output directories:

```
outputs/
└── [paper_name]/
    ├── summary.txt              # AI-generated summary
    ├── summary_report.txt       # Pipeline execution report
    ├── en/                      # English version
    │   ├── script.json         # VN script
    │   ├── audio/              # Audio files
    │   └── en_audio_mapping.json
    ├── hi/                      # Hindi version
    │   ├── script.json
    │   ├── audio/
    │   └── hi_audio_mapping.json
    └── te/                      # Telugu version
        ├── script.json
        ├── audio/
        └── te_audio_mapping.json
```

## 🌍 Language Support

### Translation Languages
- **Indo-Aryan**: Hindi (hi), Bengali (bn), Gujarati (gu), Marathi (mr), Punjabi (pa), Urdu (ur)
- **Dravidian**: Telugu (te), Tamil (ta), Kannada (kn), Malayalam (ml)
- **Others**: English (en), Assamese (as), Odia (or), Manipuri (mni), Bodo (brx), Santali (sat), Kashmiri (ks), Nepali (ne), Sindhi (sd), Dogri (doi), Konkani (gom), Maithili (mai)

### TTS Languages
All translation languages support high-quality TTS with appropriate voice models.

## 🎯 Features

### Content Processing
- Intelligent PDF text extraction
- Academic paper structure recognition
- AI-powered summarization and script generation
- Interactive choice system creation

### Multi-Language Support
- Automatic translation to multiple languages
- Language family-aware processing
- Cultural adaptation of content

### Audio Generation
- High-quality 48kHz audio output
- Character-specific voice assignments
- Rate-limited API calls for reliability
- Automatic audio file management

### Quality Assurance
- Comprehensive error handling
- Progress tracking and reporting
- Validation testing
- Modular architecture for easy maintenance

## 🔧 Configuration

### API Endpoints
- **Bhashini Translation**: `https://dhruva-api.bhashini.gov.in/services/inference/pipeline`
- **Bhashini TTS**: `https://dhruva-api.bhashini.gov.in/services/inference/pipeline`
- **Gemini AI**: Configured through `google-generativeai` library

### Service IDs
The pipeline uses optimized service IDs for different language families:
- Indo-Aryan languages: Service group 1
- Misc languages: Service group 2  
- Dravidian languages: Service group 3

## 🚨 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **API Failures**: Check internet connection and API key validity
3. **File Not Found**: Verify PDF path is correct and accessible
4. **Memory Issues**: Large PDFs may require splitting

### Testing
Run `python3 test_pipeline.py` to verify installation and configuration.

## 📊 Performance

- **Processing Time**: ~5-10 minutes per paper (depending on length)
- **Audio Generation**: ~1-2 seconds per dialogue line
- **Translation**: ~30 seconds per language
- **Output Quality**: Professional-grade TTS audio and accurate translations

## 🤝 Contributing

This pipeline is designed for modularity. Each component can be enhanced independently:
- Add new language support
- Integrate additional TTS providers
- Enhance script generation prompts
- Improve PDF processing accuracy

## 📄 License

This project uses various APIs and services. Ensure compliance with:
- Bhashini API terms of service
- Google Gemini AI usage policies
- Individual research paper licensing