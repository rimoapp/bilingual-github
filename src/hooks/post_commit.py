import os
from src.utils.translation import translate_text

def read_file_with_fallback(file_path):
    encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]  # Multiple encodings to try
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as file:
                return file.read()
        except UnicodeDecodeError:
            continue  # Try the next encoding if this one fails
    raise ValueError(f"Failed to read {file_path} with any of the tried encodings.")  # Raise error if all fail

def translate_markdown(file_path, target_languages):
    print(f"Processing file: {file_path}")
    
    content = read_file_with_fallback(file_path)  # Read with fallback encodings

    for language in target_languages:
        print(f"Translating to {language}...")  # Log the current language
        translated_text = translate_text(content, language)
        
        if translated_text:
            translated_file = f"{file_path.split('.')[0]}.{language}.md"
            with open(translated_file, "w", encoding="utf-8") as file:  # Use utf-8 encoding to write the file
                file.write(translated_text)
            print(f"Translated {file_path} to {language}: {translated_file}")
        else:
            print(f"Translation failed for {file_path} to {language}")

def main():
    target_languages = ["ja", "fr"]
    print("Starting translation process...")
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".md"):
                translate_markdown(os.path.join(root, file), target_languages)

if __name__ == "__main__":
    main()
