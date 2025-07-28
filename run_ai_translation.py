# File: run_ai_translation.py

import subprocess
import os
import sys
import polib
import requests
import json
import time
from datetime import datetime

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, '.venv')
PYBABEL_PATH = os.path.join(VENV_DIR, 'Scripts', 'pybabel.exe')
BABEL_CFG_PATH = os.path.join(BASE_DIR, 'babel.cfg')
LOCALE_DIR = os.path.join(BASE_DIR, 'data', 'locales')
POT_FILE_PATH = os.path.join(LOCALE_DIR, 'base.pot')
LANGUAGE_CODE = "zh_CN"
PO_FILE_PATH = os.path.join(LOCALE_DIR, LANGUAGE_CODE, 'LC_MESSAGES', 'base.po')
LM_STUDIO_URL = "http://localhost:1235/v1/chat/completions"
# --- End of Configuration ---

def run_command(command, step_name):
    """A helper function to run shell commands that we know are reliable."""
    print(f"--- Step {step_name} ---")
    command_str = ' '.join(f'"{part}"' for part in command)
    print(f"> {command_str}")
    try:
        result = subprocess.run(command_str, check=True, capture_output=True, text=True, encoding='utf-8', shell=True)
        print("Success.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed.\n--- Stderr ---\n{e.stderr}\n--- Stdout ---\n{e.stdout}")
        return False

def create_or_update_po_file():
    """
    This is the new, robust function that replaces 'pybabel init' and 'pybabel update'.
    It uses the 'polib' library to create or merge translation files.
    """
    print("--- Step 2: Creating/Updating language file ---")
    try:
        # Load the master template file
        pot = polib.pofile(POT_FILE_PATH, encoding='utf-8')
        
        # If the language file already exists, merge it (update)
        if os.path.exists(PO_FILE_PATH):
            print(f"Found existing file at '{PO_FILE_PATH}'. Merging new strings...")
            po = polib.pofile(PO_FILE_PATH, encoding='utf-8')
            po.merge(pot)
            po.save()
            print("Merge complete.")
        # If it doesn't exist, create it from the template (init)
        else:
            print(f"No file found at '{PO_FILE_PATH}'. Creating new file...")
            po = polib.POFile()
            po.metadata = pot.metadata
            po.header = pot.header
            po.metadata['Language'] = LANGUAGE_CODE
            po.metadata['PO-Revision-Date'] = datetime.now().strftime('%Y-%m-%d %H:%M%z')
            
            for entry in pot:
                po.append(entry)
            
            po.save(PO_FILE_PATH)
            print("New file created successfully.")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create or update .po file. Details: {e}")
        return False

def translate_text(text_to_translate: str):
    """Sends text to the local LLM and returns the translation."""
    prompt = f"Please translate the following English text to Simplified Chinese. Provide only the translated text, without any explanations or quotation marks. The text to translate is: \"{text_to_translate}\""
    headers = {"Content-Type": "application/json"}
    data = {"model": "local-model", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
    try:
        response = requests.post(LM_STUDIO_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        translated_text = response.json()['choices'][0]['message']['content'].strip().strip('"')
        return translated_text
    except Exception as e:
        print(f"  ERROR: AI translation failed. Details: {e}")
        return None

def ai_translate_po_file():
    """Finds untranslated entries and uses an AI to translate them."""
    print("--- Step 3: Translating new entries with local AI ---")
    po = polib.pofile(PO_FILE_PATH, encoding='utf-8')
    untranslated = [e for e in po if not e.msgstr and e.msgid]
    if not untranslated:
        print("All entries are already translated. Nothing to do.")
        return True

    print(f"Found {len(untranslated)} untranslated entries. Beginning translation...")
    for i, entry in enumerate(untranslated):
        print(f"[{i+1}/{len(untranslated)}] Translating: \"{entry.msgid}\"")
        translation = translate_text(entry.msgid)
        if translation:
            print(f"  -> AI Response: \"{translation}\"")
            entry.msgstr = translation
        time.sleep(1)
    
    po.save()
    print("\nFile saved successfully.")
    return True

def main():
    print("="*50)
    print("  Starting Automated AI Translation Workflow")
    print("="*50)
    print("IMPORTANT: Make sure your LM Studio server is running with a text model loaded on port 1235.")
    input("Press Enter to continue...")

    # Step 1: Extract text (This command is reliable)
    extract_command = [PYBABEL_PATH, 'extract', '-F', BABEL_CFG_PATH, '-o', POT_FILE_PATH, '.']
    if not run_command(extract_command, "1: Extracting text from source code"):
        return

    # Step 2: Create or Update .po file using our new Python function
    if not create_or_update_po_file():
        return

    # Step 3: AI Translate
    if not ai_translate_po_file():
        return

    # Step 4: Compile (This command is reliable)
    compile_command = [PYBABEL_PATH, 'compile', '-d', LOCALE_DIR]
    if not run_command(compile_command, "4: Compiling translations"):
        return

    print("\n" + "="*50)
    print("  AI Translation workflow complete!")
    print("="*50)

if __name__ == "__main__":
    main()
