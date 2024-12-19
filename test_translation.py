from src.utils.translation import translate_text

# Test case: Translate text to French
text = "Hello, how are you?"
target_language = "ja"

translated_text = translate_text(text, target_language)
if translated_text:
    print(f"Original: {text}")
    print(f"Translated ({target_language}): {translated_text}")
else:
    print("Translation failed")
