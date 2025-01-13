# Import required libraries
from difflib import unified_diff
import os
import sys
from pathlib import Path

# Add the script's src directory to the path
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

# Define target languages for translation
TARGET_LANGUAGES = ["ja", "fr"]

# Get target repository directory from environment variables
TARGET_REPO_DIR = os.getenv("GITHUB_REPOSITORY", "").strip()

print(f"TARGET_REPO_DIR: {TARGET_REPO_DIR}")
if not TARGET_REPO_DIR or not os.path.isdir(TARGET_REPO_DIR):
    raise ValueError("Target repository directory is not set or doesn't exist")
else:
    print(f"Directory exists: {TARGET_REPO_DIR}")

# Function to recursively find Markdown files in the target directory
def find_markdown_files(directory):
    return [str(path) for path in Path(directory).rglob("*.md")]

def read_file(file_path):
    # Function to read a file with UTF-8 or UTF-8 BOM encoding
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return file.read()

def save_translated_file(file_path, content, language):
    # Function to save the translated content
    translated_file = Path(file_path).with_suffix(f'.{language}.md')
    translated_file.write_text(content, encoding='utf-8')
    print(f"Generated translated file: {translated_file}")

def is_original_markdown(file_path):
    # Function to check if a file is an original Markdown file (not a translation)
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
    # Find all Markdown files in the target repository directory
    markdown_files = find_markdown_files(TARGET_REPO_DIR)
    for file in markdown_files:
        if is_original_markdown(file):
            sync_translations(file, TARGET_LANGUAGES)

if __name__ == "__main__":
    main()
