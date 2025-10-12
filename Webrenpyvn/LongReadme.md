# WebRenPy VN - PDF to Visual Novel Converter

Transform academic research papers into interactive Visual Novel experiences with multi-language support and high-quality audio generation.

## 🚀 Quick Setup

### Prerequisites

1. **Node.js & npm** (for React frontend)
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install nodejs npm
   
   # Verify installation
   node --version
   npm --version
   ```

2. **Python 3.8+** (for AI processing)
   ```bash
   # Ubuntu/Debian
   sudo apt install python3 python3-pip
   
   # Verify installation
   python3 --version
   pip3 --version
   ```

3. **Git** (to download the project)
   ```bash
   sudo apt install git
   ```

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Webrenpyvn
   ```

2. **Install Python dependencies**
   ```bash
   pip3 install PyPDF2 requests pathlib google-generativeai
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Verify setup**
   ```bash
   cd Assest_generation_pipeline
   python3 test_pipeline.py
   ```

## 🎮 Usage Instructions

### 1. Converting a New PDF to Visual Novel

1. **Place your PDF in the research_paper folder**
   ```bash
   cp your_research_paper.pdf research_paper/
   ```

2. **Run the conversion pipeline**
   ```bash
   cd Assest_generation_pipeline
   ./run_pipeline.sh your_research_paper.pdf
   ```
   
   This will:
   - Extract and summarize the PDF content
   - Generate an interactive VN script
   - Translate to Hindi and Telugu
   - Create high-quality TTS audio for all languages
   - Output everything to `outputs/[pdf_name]/`

3. **Update public directory** (after first run)
   ```bash
   cd ..
   cp -r outputs public/
   ```

### 2. Setting Game Configuration

#### Option A: Using the update script (Recommended)
```bash
# Switch to English
./update_config.sh your_pdf_name en

# Switch to Hindi
./update_config.sh your_pdf_name hi

# Switch to Telugu
./update_config.sh your_pdf_name te

# Example:
./update_config.sh 2509.21175v1 en
```

#### Option B: Manual configuration
Edit `game.conf` and `public/game.conf`:
```properties
# Change these values
pdf_name=your_pdf_name
language=en  # or hi, te
audio_enabled=true
```

### 3. Playing the Visual Novel

1. **Start the development server**
   ```bash
   npm start
   ```

2. **Open your browser**
   - Navigate to `http://localhost:3000`
   - The VN will automatically load based on your configuration

3. **Game Controls**
   - **Space/Enter**: Advance dialogue
   - **Mouse Click**: Select choices
   - **M**: Toggle mute
   - **T**: Toggle TTS
   - **Esc**: Cancel choice selection

4. **Language Switcher**
   - Use the language switcher in the top-right corner
   - Changes take effect after page reload

## 📁 Project Structure

```
Webrenpyvn/
├── Assest_generation_pipeline/     # PDF conversion tools
│   ├── run_pipeline.sh            # Main conversion script
│   ├── pdf_to_vn_pipeline.py     # Core pipeline
│   └── ...
├── research_paper/                # Place PDFs here
├── outputs/                       # Generated VN content
│   └── [pdf_name]/
│       ├── en/                    # English version
│       ├── hi/                    # Hindi version
│       └── te/                    # Telugu version
├── public/                        # Web-served files
│   ├── game.conf                  # Game configuration
│   └── outputs/                   # Copy of outputs
├── src/                           # React VN engine
├── game.conf                      # Main configuration
└── update_config.sh               # Configuration helper
```

## 🔧 Configuration Options

Edit `game.conf` to customize:

```properties
# Core settings
pdf_name=2509.21175v1              # PDF to play
language=en                        # en, hi, or te

# Audio settings
audio_enabled=true                 # Enable/disable TTS
auto_play=false                    # Auto-advance dialogue
auto_play_delay=3000              # Auto-play delay (ms)

# Development
debug_mode=false                   # Show debug information
```

## 🎵 Audio Features

- **High-quality TTS**: Generated using Bhashini API
- **Multi-language support**: English, Hindi, Telugu
- **Character voices**: Different voices for each character
- **Pre-generated audio**: Instant playback, no delays
- **48kHz quality**: Professional audio format

## 🌍 Language Support

- **English (en)**: Original content
- **Hindi (hi)**: Full translation with native TTS
- **Telugu (te)**: Full translation with native TTS

## 🚨 Troubleshooting

### Common Issues

1. **Pipeline fails to run**
   - Check Python dependencies: `pip3 list | grep -E "(PyPDF2|requests|google-generativeai)"`
   - Verify PDF is in `research_paper/` folder

2. **No audio in VN**
   - Ensure `audio_enabled=true` in both `game.conf` files
   - Check that `public/outputs/` contains the audio files
   - Refresh browser after configuration changes

3. **Wrong language loading**
   - Update both `game.conf` and `public/game.conf`
   - Use `./update_config.sh` script for automatic sync
   - Clear browser cache if needed

4. **Development server won't start**
   - Run `npm install` to ensure dependencies
   - Check that port 3000 is available
   - Try `npm start -- --port 3001` for alternative port

### Getting Help

1. **Check pipeline status**
   ```bash
   cd Assest_generation_pipeline
   python3 test_pipeline.py
   ```

2. **View current configuration**
   ```bash
   ./update_config.sh  # Shows current settings
   ```

3. **Check available content**
   ```bash
   ls outputs/          # List available PDFs
   ls outputs/[pdf]/    # List available languages
   ```

## 🎯 Quick Start Example

```bash
# 1. Setup (one time)
npm install
pip3 install PyPDF2 requests pathlib google-generativeai

# 2. Convert a PDF
cp my_paper.pdf research_paper/
cd Assest_generation_pipeline
./run_pipeline.sh my_paper.pdf
cd ..

# 3. Configure and play
./update_config.sh my_paper en
cp -r outputs public/
npm start
```

Open `http://localhost:3000` and enjoy your research paper as an interactive Visual Novel!

## 🔄 Updating Content

To update with new outputs after running the pipeline:
```bash
cp -r outputs public/
```

The VN will automatically use the updated content on next page load.

---

**Note**: Keep the `outputs/` folder and `public/game.conf` as provided for immediate testing with the included sample content.


# Quick Reference - WebRenPy VN

## 🚀 Essential Commands

### First Time Setup
```bash
npm install
pip3 install PyPDF2 requests pathlib google-generativeai
```

### Convert New PDF
```bash
# 1. Add PDF to research folder
cp your_paper.pdf research_paper/

# 2. Run conversion
cd Assest_generation_pipeline
./run_pipeline.sh your_paper.pdf
cd ..

# 3. Update public files
cp -r outputs public/
```

### Switch Language/PDF
```bash
# Quick config update
./update_config.sh [pdf_name] [language]

# Examples:
./update_config.sh 2509.21175v1 en    # English
./update_config.sh 2509.21175v1 hi    # Hindi  
./update_config.sh 2509.21175v1 te    # Telugu
```

### Run Visual Novel
```bash
npm start
# Open http://localhost:3000
```

## 📋 File Locations

| What | Where |
|------|-------|
| Input PDFs | `research_paper/` |
| Generated content | `outputs/[pdf_name]/` |
| Game config | `game.conf` & `public/game.conf` |
| Web files | `public/` |
| Conversion tools | `Assest_generation_pipeline/` |

## 🎮 Game Controls

| Key | Action |
|-----|--------|
| Space/Enter | Advance dialogue |
| Mouse click | Select choices |
| M | Toggle mute |
| T | Toggle TTS |
| Esc | Cancel choices |

## 🔧 Configuration

Edit `game.conf`:
```properties
pdf_name=your_pdf_name     # Which PDF to play
language=en                # en/hi/te
audio_enabled=true         # Enable audio
debug_mode=false           # Show debug info
```

## 🚨 Quick Fixes

| Problem | Solution |
|---------|----------|
| No audio | Check `audio_enabled=true` in both config files |
| Wrong language | Run `./update_config.sh pdf_name language` |
| Pipeline fails | Check PDF in `research_paper/` folder |
| Server won't start | Run `npm install`, check port 3000 |

## 📊 Check Status

```bash
# Test pipeline
cd Assest_generation_pipeline && python3 test_pipeline.py

# View config
./update_config.sh

# List available content
ls outputs/
ls outputs/[pdf_name]/
```