import os
import sys
import subprocess
from pathlib import Path
from difflib import unified_diff

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

TARGET_LANGUAGES = ["ja", "fr"]

def read_file(file_path):
    print(f"Reading file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            print(f"Successfully read {len(content)} characters from {file_path}")
            return content
    except UnicodeDecodeError:
        print(f"UTF-8 decode failed, trying UTF-8-SIG for {file_path}")
        with open(file_path, "r", encoding="utf-8-sig") as file:
            content = file.read()
            print(f"Successfully read {len(content)} characters from {file_path} with UTF-8-SIG")
            return content

def save_translated_file(file_path, content, language):
    translated_file = Path(file_path).with_suffix(f'.{language}.md')
    print(f"Saving translation to: {translated_file}")
    translated_file.write_text(content, encoding='utf-8')
    print(f"Successfully saved {len(content)} characters to {translated_file}")

def get_changed_files():
    print("Checking for changed files...")
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        files = [f for f in result.stdout.splitlines() if f.strip()]
        print(f"Found {len(files)} changed files using git diff: {files}")
        return files
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e}")
        print("Falling back to git status...")
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        files = [line[3:] for line in result.stdout.splitlines() if line.strip()]
        print(f"Found {len(files)} changed files using git status: {files}")
        return files

def is_original_markdown(file_path):
    path = Path(file_path)
    result = (path.suffix == '.md' and 
            not any(path.name.endswith(f'.{lang}.md') for lang in TARGET_LANGUAGES))
    print(f"Checking if {file_path} is original markdown: {result}")
    return result

def sync_translations(original_file, target_languages):
    print(f"\nProcessing translations for: {original_file}")
    try:
        content = read_file(original_file)
        original_path = Path(original_file)

        for language in target_languages:
            print(f"\nProcessing {language} translation...")
            translated_file = original_path.with_suffix(f'.{language}.md')
            
            needs_translation = True
            if translated_file.exists():
                print(f"Found existing translation: {translated_file}")
                existing_translation = read_file(translated_file)
                diff = list(unified_diff(
                    existing_translation.splitlines(),
                    content.splitlines(),
                    lineterm=""
                ))
                needs_translation = bool(diff)
                print(f"Translation needs update: {needs_translation}")
                if diff:
                    print(f"Found {len(diff)} lines different")

            if needs_translation:
                print(f"Translating content to {language}...")
                translated_content = translate_text(content, language)
                if translated_content:
                    save_translated_file(original_file, translated_content, language)
                    print(f"Successfully updated translation for {translated_file}")
                else:
                    print(f"Warning: No content returned from translation to {language}")

    except Exception as e:
        print(f"Error processing {original_file}: {str(e)}")
        import traceback
        print(traceback.format_exc())

def main():
    print("Starting markdown translation process...")
    changed_files = get_changed_files()
    print(f"\nFound {len(changed_files)} changed files")
    
    for file in changed_files:
        print(f"\nProcessing file: {file}")
        if os.path.exists(file):
            print(f"File exists: {file}")
            if is_original_markdown(file):
                sync_translations(file, TARGET_LANGUAGES)
            else:
                print(f"Skipping non-original markdown file: {file}")
        else:
            print(f"File does not exist: {file}")

if __name__ == "__main__":
    main()