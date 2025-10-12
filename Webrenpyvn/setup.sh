#!/bin/bash
# Asset Generation Pipeline Setup Script
# =====================================
# This script sets up the Python environment for the PDF to VN pipeline

echo "🚀 Setting up Asset Generation Pipeline Environment"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | grep -oP '3\.\d+')
echo "✅ Found Python $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ Found pip3"

# Create virtual environment (optional but recommended)
read -p "🤔 Do you want to create a virtual environment? (y/N): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip3 install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📋 Next Steps:"
echo "1. Set up your API keys:"
echo "   - Add your Gemini API key to the pipeline scripts"
echo "   - Bhashini API key is already configured"
echo ""
echo "2. Test the installation:"
echo "   cd Assest_generation_pipeline"
echo "   python3 test_pipeline.py"
echo ""
echo "3. Run the pipeline:"
echo "   ./run_pipeline.sh <your_pdf_file.pdf>"
echo ""
echo "💡 Make sure your PDF files are in the research_paper/ folder"

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔧 To activate the virtual environment in future sessions:"
    echo "   source venv/bin/activate"
fi