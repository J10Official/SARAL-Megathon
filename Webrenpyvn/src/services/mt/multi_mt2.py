import requests
import os
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------- CONFIG ----------------
LANG_MAP = {
    "hi-en": {"mt_endpoint": "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316384a", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTY3ZDZiOTNlM2JlYzkwMWZkOTc3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.D_lwUftpnNSFbBs0_9uG4P86Z2p6kMZ9PC1GkqZd8mg"},
    "en-hi": {"mt_endpoint": "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316383c", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTY3ZDZiOTNlM2JlYzkwMWZkOTc3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.D_lwUftpnNSFbBs0_9uG4P86Z2p6kMZ9PC1GkqZd8mg"},
    "en-te": {"mt_endpoint": "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316389a", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTY3ZDZiOTNlM2JlYzkwMWZkOTc3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.D_lwUftpnNSFbBs0_9uG4P86Z2p6kMZ9PC1GkqZd8mg"},
    "te-en": {"mt_endpoint": "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb923163869", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTY3ZDZiOTNlM2JlYzkwMWZkOTc3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.D_lwUftpnNSFbBs0_9uG4P86Z2p6kMZ9PC1GkqZd8mg"},
}
# ----------------------------------------

def windows_to_wsl_path(windows_path):
    """Convert Windows path to WSL path"""
    if windows_path.startswith('C:'):
        return '/mnt/c' + windows_path[2:].replace('\\', '/')
    elif windows_path.startswith('D:'):
        return '/mnt/d' + windows_path[2:].replace('\\', '/')
    else:
        return windows_path.replace('\\', '/')

def translate_text(text: str, direction: str):
    if direction not in LANG_MAP:
        raise ValueError(f"Unsupported direction: {direction}")

    endpoint = LANG_MAP[direction]["mt_endpoint"]
    token = LANG_MAP[direction]["token"]
    headers = {"access-token": token, "Content-Type": "application/json"}
    payload = {"input_text": text}

    response = requests.post(endpoint, headers=headers, json=payload, verify=False, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError(f"Translation failed: {data}")

    return data["data"]["output_text"]

def translate_file(input_file: str, output_file: str, direction: str):
    """
    Translate text from input file and write to output file
    
    Args:
        input_file: Path to input text file
        output_file: Path to output text file
        direction: Translation direction (hi-en, en-hi, en-te, te-en)
    """
    # Convert Windows paths to WSL paths if needed
    input_file = windows_to_wsl_path(input_file)
    output_file = windows_to_wsl_path(output_file)
    
    print(f"Looking for input file at: {input_file}")
    print(f"Will write output to: {output_file}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        print("Warning: Input file is empty")
        return
    
    print(f"Translating {len(lines)} lines...")
    
    translated_lines = []
    
    # Translate line by line to preserve formatting
    for i, line in enumerate(lines, 1):
        original_line = line.rstrip('\n\r')  # Remove trailing newlines but keep content
        if not original_line.strip():  # Empty line
            translated_lines.append('')
            continue
            
        print(f"Translating line {i}/{len(lines)}: {original_line[:50]}{'...' if len(original_line) > 50 else ''}")
        
        try:
            translated_line = translate_text(original_line, direction)
            translated_lines.append(translated_line)
            print(f"  → {translated_line[:50]}{'...' if len(translated_line) > 50 else ''}")
        except Exception as e:
            print(f"Error translating line {i}: {e}")
            translated_lines.append(f"[Translation failed: {original_line}]")
    
    # Write to output file with original line structure
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, translated_line in enumerate(translated_lines):
            # Write the translated line
            f.write(translated_line)
            
            # Add newline if it's not the last line or if original had newline
            if i < len(lines) - 1:
                f.write('\n')
            elif lines and lines[-1].endswith(('\n', '\r')):
                f.write('\n')
    
    print(f"✅ Translation completed!")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Direction: {direction}")
    print(f"Translated {len([l for l in translated_lines if l.strip()])} non-empty lines")

def translate_file_paragraphs(input_file: str, output_file: str, direction: str):
    """
    Alternative method: Translate by paragraphs (groups of lines)
    """
    # Convert Windows paths to WSL paths if needed
    input_file = windows_to_wsl_path(input_file)
    output_file = windows_to_wsl_path(output_file)
    
    print(f"Looking for input file at: {input_file}")
    print(f"Will write output to: {output_file}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content:
        print("Warning: Input file is empty")
        return
    
    # Split into paragraphs (groups of lines separated by empty lines)
    paragraphs = []
    current_paragraph = []
    
    for line in content.split('\n'):
        if line.strip():  # Non-empty line
            current_paragraph.append(line)
        else:  # Empty line - paragraph separator
            if current_paragraph:
                paragraphs.append('\n'.join(current_paragraph))
                current_paragraph = []
            paragraphs.append('')  # Preserve empty lines
    
    # Don't forget the last paragraph
    if current_paragraph:
        paragraphs.append('\n'.join(current_paragraph))
    
    print(f"Translating {len([p for p in paragraphs if p])} paragraphs...")
    
    translated_paragraphs = []
    
    # Translate paragraph by paragraph
    for i, paragraph in enumerate(paragraphs, 1):
        if not paragraph:  # Empty paragraph (preserved empty lines)
            translated_paragraphs.append('')
            continue
            
        print(f"Translating paragraph {i}/{len(paragraphs)}: {paragraph[:50]}{'...' if len(paragraph) > 50 else ''}")
        
        try:
            translated_paragraph = translate_text(paragraph, direction)
            translated_paragraphs.append(translated_paragraph)
            print(f"  → {translated_paragraph[:50]}{'...' if len(translated_paragraph) > 50 else ''}")
        except Exception as e:
            print(f"Error translating paragraph {i}: {e}")
            translated_paragraphs.append(f"[Translation failed: {paragraph}]")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, translated_paragraph in enumerate(translated_paragraphs):
            if translated_paragraph:  # Non-empty paragraph
                f.write(translated_paragraph)
            if i < len(translated_paragraphs) - 1:
                f.write('\n\n' if translated_paragraphs[i+1] else '\n')
            elif content.endswith('\n'):
                f.write('\n')
    
    print(f"✅ Translation completed!")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Direction: {direction}")

def interactive_mode():
    """Interactive mode for manual text input"""
    while True:
        print("\n" + "="*50)
        print("Choose MT direction:")
        print("1. Hindi → English")
        print("2. English → Hindi") 
        print("3. English → Telugu")
        print("4. Telugu → English")
        print("5. File Translation Mode")
        print("6. Exit")
        choice = input("Enter choice [1-6]: ")

        if choice == "6":
            break
        elif choice == "5":
            file_translation_mode()
        elif choice == "1":
            direction = "hi-en"
        elif choice == "2":
            direction = "en-hi"
        elif choice == "3":
            direction = "en-te"
        elif choice == "4":
            direction = "te-en"
        else:
            print("Invalid choice!")
            continue

        text = input("Enter text to translate: ")
        try:
            translated = translate_text(text, direction)
            print(f"✅ Translated ({direction}): {translated}")
        except Exception as e:
            print(f"❌ Translation failed: {e}")

def file_translation_mode():
    """Mode for file-based translation"""
    print("\n" + "="*50)
    print("FILE TRANSLATION MODE")
    print("="*50)
    
    # Get translation direction
    print("\nChoose translation direction:")
    print("1. Hindi → English")
    print("2. English → Hindi") 
    print("3. English → Telugu")
    print("4. Telugu → English")
    direction_choice = input("Enter choice [1-4]: ")
    
    direction_map = {
        "1": "hi-en",
        "2": "en-hi", 
        "3": "en-te",
        "4": "te-en"
    }
    
    if direction_choice not in direction_map:
        print("Invalid choice!")
        return
    
    direction = direction_map[direction_choice]
    
    # Get translation method
    print("\nChoose translation method:")
    print("1. Line by line (preserves line structure)")
    print("2. By paragraphs (better for context)")
    method_choice = input("Enter choice [1-2]: ")
    
    # Get file paths
    print("\nEnter file paths:")
    input_file = input("Input file path: ").strip()
    output_file = input("Output file path: ").strip()
    
    if not input_file or not output_file:
        print("Both input and output file paths are required!")
        return
    
    try:
        if method_choice == "2":
            translate_file_paragraphs(input_file, output_file, direction)
        else:
            translate_file(input_file, output_file, direction)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("           TEXT TRANSLATION TOOL")
    print("="*60)
    print("Supported translations:")
    print("  • Hindi → English")
    print("  • English → Hindi") 
    print("  • English → Telugu")
    print("  • Telugu → English")
    print("="*60)
    
    print("\nChoose mode:")
    print("1. Interactive mode (type text)")
    print("2. File mode (process files)")
    
    mode_choice = input("Enter mode choice [1-2]: ")
    
    if mode_choice == "1":
        interactive_mode()
    elif mode_choice == "2":
        file_translation_mode()
    else:
        print("Invalid choice! Starting interactive mode...")
        interactive_mode()