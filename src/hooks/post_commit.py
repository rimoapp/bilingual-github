import os
import sys
import subprocess
from difflib import unified_diff

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

# List of target languages for translation
TARGET_LANGUAGES = ["ja", "fr"]

def read_file(file_path):
    """Read a file with multiple encoding fallbacks."""
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Failed to read {file_path} with any of the tried encodings.")

def save_translated_file(file_path, content, language):
    """Save the translated content to a new file."""
    translated_file = f"{file_path.split('.')[0]}.{language}.md"
    print(f"Saving translated file: {translated_file}")
    with open(translated_file, "w", encoding="utf-8") as file:
        file.write(content)

def get_changed_files():
    """Get a list of files changed in the last commit."""
    print("Fetching changed files...")
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"], 
        capture_output=True, 
        text=True
    )
    changed_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
    print(f"Changed files detected: {changed_files}")
    return changed_files


def is_original_markdown(file_path):
    """Check if a file is an original markdown file (not a translation)."""
    return file_path.endswith(".md") and not any(file_path.endswith(f".{lang}.md") for lang in TARGET_LANGUAGES)

def sync_translations(original_file, target_languages):
    """Translate and synchronize markdown files."""
    content = read_file(original_file)
    for language in target_languages:
        translated_file = f"{original_file.split('.')[0]}.{language}.md"

        if os.path.exists(translated_file):
            # Read existing translation
            existing_translation = read_file(translated_file)

            # Check differences and re-translate changed parts
            diff = unified_diff(existing_translation.splitlines(), content.splitlines(), lineterm="")
            diff_lines = list(diff)

            if diff_lines:
                print(f"Changes detected in {original_file}. Updating {translated_file}...")
                translated_content = translate_text(content, language)
                save_translated_file(original_file, translated_content, language)
        else:
            # Translate the whole file if translation doesn't exist
            print(f"Translating {original_file} to {language}...")
            translated_content = translate_text(content, language)
            save_translated_file(original_file, translated_content, language)

def main():
    """Main function to handle post-commit translation."""
    changed_files = get_changed_files()

    for file in changed_files:
        if is_original_markdown(file):
            print(f"Processing file: {file}")
            sync_translations(file, TARGET_LANGUAGES)

if __name__ == "__main__":
    main()
