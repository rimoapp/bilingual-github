import os
import sys
from pathlib import Path
from difflib import unified_diff

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

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

def is_original_markdown(file_path):
    path = Path(file_path)
    return (path.suffix == '.md' and 
            not any(path.name.endswith(f'.{lang}.md') for lang in TARGET_LANGUAGES))

def sync_translations(original_file, target_languages):
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

def main():
    markdown_files = [f for f in os.listdir('.') if f.endswith('.md') and is_original_markdown(f)]
    
    for file in markdown_files:
        sync_translations(file, TARGET_LANGUAGES)

if __name__ == "__main__":
    main()