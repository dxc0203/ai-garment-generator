# File: run_maintenance.py

import sys
import os
import time

# Add the root directory to the Python path to find our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.database import crud
from app.translator import ai_translate # We import the AI function directly

# --- Configuration ---
# This list defines all languages the script should check and ensure are translated.
# It should match the list in your language_selector.
LANGUAGES_TO_CHECK = ["zh_CN", "es", "fr"]
# How old a translation must be (in days) before it's deleted.
DAYS_TO_KEEP = 90
# --- End of Configuration ---

def main():
    """Main function to run all maintenance tasks."""
    print("="*50)
    print("  Starting Application Maintenance Workflow")
    print("="*50)
    print("IMPORTANT: Make sure your LM Studio server is running with a text model loaded on port 1235.")
    input("Press Enter to continue...")

    # --- Task 1: Purge Old Translations ---
    print(f"\n--- Step 1: Purging translations not used in the last {DAYS_TO_KEEP} days ---")
    crud.purge_old_translations(days_old=DAYS_TO_KEEP)

    # --- Task 2: Proactively Translate Missing Entries ---
    print("\n--- Step 2: Checking for and generating missing translations ---")
    
    # 2a: Get the master list of all English phrases
    source_texts = crud.get_all_unique_source_texts()
    if not source_texts:
        print("No source texts found in the database. Nothing to translate.")
        print("\nMaintenance complete.")
        return
    
    print(f"Found {len(source_texts)} unique English phrases to check against {len(LANGUAGES_TO_CHECK)} languages.")
    
    new_translations_added = 0
    
    # 2b: Loop through each language and each phrase
    for lang_code in LANGUAGES_TO_CHECK:
        print(f"\nChecking language: {lang_code.upper()}")
        for text in source_texts:
            # Check if a translation already exists
            existing_translation = crud.get_translation(lang_code, text)
            
            if existing_translation is None:
                # If it doesn't exist, generate a new one
                print(f"  -> Missing translation for: \"{text}\". Calling AI...")
                
                new_translation = ai_translate(text, lang_code)
                
                if new_translation:
                    crud.add_translation(lang_code, text, new_translation)
                    print(f"  -> AI Response: \"{new_translation}\". Saved to cache.")
                    new_translations_added += 1
                else:
                    print(f"  -> FAILED to get translation from AI.")
                
                time.sleep(1) # Be nice to the AI server
    
    print("\n" + "="*50)
    print("  Maintenance workflow complete!")
    print(f"  Summary: {new_translations_added} new translations were generated and saved.")
    print("="*50)

if __name__ == "__main__":
    main()
