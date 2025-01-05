import os
import sys
import subprocess
from difflib import unified_diff

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

TARGET_LANGUAGES = ["ja", "fr"]

def read_file(file_path):
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    for encoding in encodings:
        with open(file_path, "r", encoding=encoding) as file:
            return file.read()

def save_translated_file(file_path, content, language):
    translated_file = f"{file_path.split('.')[0]}.{language}.md"
    with open(translated_file, "w", encoding="utf-8") as file:
        file.write(content)

def get_changed_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"], 
        capture_output=True, 
        text=True
    )
    return [f.strip() for f in result.stdout.split("\n") if f.strip()]

def is_original_markdown(file_path):
    return file_path.endswith(".md") and not any(file_path.endswith(f".{lang}.md") for lang in TARGET_LANGUAGES)

def sync_translations(original_file, target_languages):
    content = read_file(original_file)
    for language in target_languages:
        translated_file = f"{original_file.split('.')[0]}.{language}.md"

        if os.path.exists(translated_file):
            existing_translation = read_file(translated_file)
            diff = unified_diff(existing_translation.splitlines(), content.splitlines(), lineterm="")
            if list(diff):
                translated_content = translate_text(content, language)
                save_translated_file(original_file, translated_content, language)
        else:
            translated_content = translate_text(content, language)
            save_translated_file(original_file, translated_content, language)

def main():
    changed_files = get_changed_files()
    for file in changed_files:
        if is_original_markdown(file):
            sync_translations(file, TARGET_LANGUAGES)

if __name__ == "__main__":
    main()
