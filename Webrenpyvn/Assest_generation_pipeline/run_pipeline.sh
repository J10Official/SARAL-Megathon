#!/bin/bash

# Asset Generation Pipeline Runner
# This script runs the PDF to VN pipeline from the Asset_generation_pipeline directory

echo "🚀 Asset Generation Pipeline"
echo "=============================="

if [ $# -eq 0 ]; then
    echo "Usage: $0 <pdf_filename>"
    echo ""
    echo "Example: $0 2509.21175v1.pdf"
    echo ""
    echo "📁 Available PDFs in research_paper folder:"
    if [ -d "../research_paper" ]; then
        ls -1 ../research_paper/*.pdf 2>/dev/null | sed 's|../research_paper/||' || echo "  No PDF files found"
    else
        echo "  research_paper folder not found"
    fi
    echo ""
    echo "💡 Place your PDF files in ../research_paper/ folder"
    echo "📂 Outputs will be generated in ../outputs/ folder"
    exit 1
fi

PDF_FILE="$1"

echo "📖 Processing: $PDF_FILE"
echo "⏳ Starting pipeline..."
echo ""

# Run the pipeline
python3 pdf_to_vn_pipeline.py "$PDF_FILE"

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "🎉 Pipeline completed successfully!"
    echo "📂 Check your outputs in ../outputs/ folder"
else
    echo ""
    echo "❌ Pipeline failed with exit code: $RESULT"
fi

exit $RESULT