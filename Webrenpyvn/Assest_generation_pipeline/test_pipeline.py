#!/usr/bin/env python3
"""
Test script to verify the reorganized Asset Generation Pipeline works correctly
"""

import os
import sys

def test_pipeline_structure():
    """Test that all required files are present"""
    print("🔍 Testing Asset Generation Pipeline Structure...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        "pdf_to_vn_pipeline.py",
        "outlinegen.py", 
        "scriptgen.py",
        "translate_vn_script.py",
        "generate_bhashini_tts_audio.py"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n🚨 Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All pipeline files present!")
        return True

def test_pipeline_imports():
    """Test that the main pipeline can import without errors"""
    print("\n🔍 Testing Pipeline Imports...")
    
    try:
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Test main pipeline import
        from pdf_to_vn_pipeline import PDFToVNPipeline
        print("✅ Main pipeline imports successfully")
        
        # Test if we can instantiate with dummy path
        pipeline = PDFToVNPipeline("test.pdf")
        print("✅ Pipeline instantiation successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Reorganized Asset Generation Pipeline\n")
    
    # Test 1: File structure
    structure_ok = test_pipeline_structure()
    
    # Test 2: Imports
    imports_ok = test_pipeline_imports()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    if structure_ok and imports_ok:
        print("🎉 All tests PASSED! Pipeline is ready to use.")
        print("💡 To run the pipeline, use:")
        print("   python3 pdf_to_vn_pipeline.py <path_to_pdf>")
        return 0
    else:
        print("🚨 Some tests FAILED. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)