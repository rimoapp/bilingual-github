import os
from src.utils.translation import translate_text

def translate_markdown(file_path, target_languages):
    with open(file_path, "r") as file:
        content = file.read()

    for language in target_languages:
        translated_text = translate_text(content, language)
        if translated_text:
            translated_file = f"{file_path.split('.')[0]}.{language}.md"
            with open(translated_file, "w") as file:
                file.write(translated_text)
            print(f"Translated {file_path} to {language}: {translated_file}")

def main():
    target_languages = ["ja", "fr"]
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".md"):
                translate_markdown(os.path.join(root, file), target_languages)

if __name__ == "__main__":
    main()
