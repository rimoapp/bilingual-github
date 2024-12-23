import os
import sys

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)
from utils.translation import translate_text


def read_file(file_path):
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Failed to read {file_path} with any of the tried encodings.")


def save_translated_file(file_path, content, language):
    translated_file = f"{file_path.split('.')[0]}.{language}.md"
    with open(translated_file, "w", encoding="utf-8") as file:
        file.write(content)


def translate_markdown_file(file_path, target_languages):
    content = read_file(file_path)
    for language in target_languages:
        translated_content = translate_text(content, language)
        if translated_content:
            save_translated_file(file_path, translated_content, language)
            print(f"Translated {file_path} to {language}")
        else:
            print(f"Translation failed for {file_path} to {language}")


def translate_markdown_files(target_languages):
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".md"):
                translate_markdown_file(os.path.join(root, file), target_languages)


def main():
    target_languages = ["ja", "fr"]
    translate_markdown_files(target_languages)


if __name__ == "__main__":
    main()
