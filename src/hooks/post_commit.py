import os
import sys
from pathlib import Path
from difflib import unified_diff

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

TARGET_LANGUAGE = "en"

def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return file.read()

def get_translated_path(original_path):
    # Replace 'docs' with 'en.docs' in the path
    parts = Path(original_path).parts
    try:
        idx = parts.index('docs')
        new_parts = list(parts)
        new_parts[idx] = 'en.docs'
        return Path(*new_parts)
    except ValueError:
        # If 'docs' not in path, just prepend 'en.docs'
        return Path('en.docs') / Path(original_path)

def sync_translations(original_file):
    content = read_file(original_file)
    translated_file = get_translated_path(original_file)
    translated_file.parent.mkdir(parents=True, exist_ok=True)
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
        translated_content = translate_text(content, TARGET_LANGUAGE)
        if translated_content:
            translated_file.write_text(translated_content, encoding='utf-8')

def find_markdown_files(directory='docs'):
    markdown_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    return markdown_files

def main():
    markdown_files = find_markdown_files('docs')
    for file in markdown_files:
        sync_translations(file)

if __name__ == "__main__":
    main()