import os
import sys
import subprocess
from pathlib import Path
from difflib import unified_diff

# Add the script's src directory to the path
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

# Define target languages for translation
TARGET_LANGUAGES = ["ja", "fr"]

def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return file.read()

def save_translated_file(file_path, content, language):
    translated_file = Path(file_path).with_suffix(f'.{language}.md')
    translated_file.write_text(content, encoding='utf-8')
    print(f"Generated translated file: {translated_file}")

def get_changed_files():
    try:
        # Check for changed and staged files
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        staged_files = [f for f in result.stdout.splitlines() if f.strip()]

        # Check for untracked files
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True
        )
        untracked_files = [f for f in result.stdout.splitlines() if f.strip()]

        # Combine and return both staged and untracked files
        return list(set(staged_files + untracked_files))

    except subprocess.CalledProcessError as e:
        print(f"Error detecting changed files: {str(e)}")
        return []

def is_original_markdown(file_path):
    path = Path(file_path)
    return (path.suffix == '.md' and 
            not any(path.name.endswith(f'.{lang}.md') for lang in TARGET_LANGUAGES))

def sync_translations(original_file, target_languages):
    try:
        content = read_file(original_file)
        original_path = Path(original_file)

        for language in target_languages:
            translated_file = original_path.with_suffix(f'.{language}.md')
            
            needs_translation = True
            if translated_file.exists():
                existing_translation = read_file(translated_file)
                diff = list(unified_diff(
                    existing_translation.splitlines(),
                    content.splitlines(),
                    lineterm=""
                ))
                needs_translation = bool(diff)

            if needs_translation:
                translated_content = translate_text(content, language)
                if translated_content:
                    save_translated_file(original_file, translated_content, language)
                    print(f"Updated translation for {translated_file}")
            else:
                print(f"No changes detected for {translated_file}. Skipping.")

    except Exception as e:
        print(f"Error processing {original_file}: {str(e)}")

def main():
    # Get changed files in the repository
    changed_files = get_changed_files()
    for file in changed_files:
        if os.path.exists(file) and is_original_markdown(file):
            sync_translations(file, TARGET_LANGUAGES)

if __name__ == "__main__":
    main()
