import google.generativeai as genai
import re
import unicodedata
from typing import Dict, List
import os

# --- EXISTING CODE FUNCTIONS (Metadata, Extraction, Cleaning) ---

def extract_paper_metadata(file_path):
    """Extract paper metadata from LaTeX or PDF text file."""
    metadata = {
        "title": "Research Paper",
        "authors": "Author", 
        "date": "2024"
    }
    
    # Try to extract basic info from filename
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Clean up filename for title
    title = name_without_ext.replace('_', ' ').replace('-', ' ').title()
    metadata["title"] = title
    
    return metadata

def extract_text_from_file(file_path):
    """Extract clean text from LaTeX or text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def clean_text(text):
    """Clean unicode characters from text."""
    # Remove unicode artifacts and normalize
    text = unicodedata.normalize('NFKD', text)
    
    # Clean up common extraction issues
    import re
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)  # Non-ASCII chars
    
    return text.strip()

# --- NEW/MODIFIED SUMMARY FUNCTION WITH YOUR PROMPT ---

def generate_detailed_summary_with_gemini(api_key, input_text):
    """Generate a detailed, structured summary using the new prompt."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # NEW PROMPT START
    prompt = f"""
*Role:* You are an expert academic summarizer and technical writer. Your goal is to create a comprehensive, highly accurate, and accessible summary of the provided research paper text.

*Instructions:*

1.  *Coverage:* Summarize the entire paper, focusing on the core content: Introduction, Background, Methods, Results/Findings, Discussion, and Conclusion. *Explicitly exclude* the "References," "Bibliography," or "Resource" section.
2.  *Structure:* Preserve the paper's original major section headings (e.g., "1. Introduction," "2. Methodology," "3. Experimental Results") in your summary, making them bold. If a section is very long, use relevant subheadings to break up the text for readability.
3.  *Accuracy and Tone:* Maintain high factual accuracy. Do not introduce external information or speculation. The tone must be academic but accessible, ensuring complex concepts are explained clearly for a general but informed audience.
4.  *Content Detail:*
    * *Introduction/Background:* State the research problem, its significance, and the paper's main contribution/hypothesis.
    * *Methods:* Briefly describe the experimental setup, data used, and key techniques/algorithms employed.
    * *Results/Findings:* State the main quantitative and qualitative findings clearly. Highlight the most significant results.
    * *Discussion/Conclusion:* Summarize the implications of the findings, their limitations, and suggested future work.
5.  *Output Format:* Present the summary in a clear, well-structured text format, using markdown for headings.

*Paper Text to Summarize:* [INSERT THE FULL TEXT OF THE RESEARCH PAPER HERE]
{input_text}
"""
    # NEW PROMPT END

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating summary with Gemini: {e}")
        # Return a fallback message instead of raising, to allow main to save error text
        return f"ERROR: Failed to generate summary. Details: {e}" 

# --- REMOVED/UNUSED PPT-STYLE/JSON FUNCTIONS ---
# The functions generate_full_script_with_gemini, split_script_into_sections, 
# generate_all_bullet_points_with_gemini, generate_title_introduction, 
# generate_web_novel_json (and their helpers) are removed from this file's purpose 
# but are left as placeholders below for dependency management if required elsewhere.
# However, for a clean saral1.py dedicated to summary:
# The main function in main.py will now import generate_detailed_summary_with_gemini directly.
# The generate_title_introduction is not strictly needed as metadata is written in main.py.

def generate_title_introduction(title, authors, date):
    """Placeholder for the old function - not used for detailed summary output."""
    return f"Title: {title}, Authors: {authors}, Date: {date}"