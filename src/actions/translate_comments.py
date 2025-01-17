import sys
import os
from github import Github

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from utils.translation import translate_text

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = os.getenv("GITHUB_REPOSITORY", "").strip()
TRANSLATED_LABEL = "translated"
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "").strip()
COMMENT_ID = os.getenv("COMMENT_ID", "").strip()
COMMENT_ORIGINAL_MARKER = "**Original Comment:**"

LANGUAGE_NAMES = {
    "ja": "日本語",  # Japanese
    "fr": "Français",  # French
    "en": "English"  
}

def get_original_content(content):
    if COMMENT_ORIGINAL_MARKER in content:
        parts = content.split(COMMENT_ORIGINAL_MARKER)
        return parts[1].strip()
    return content.strip()

def detect_language(text):
    # Basic language detection (English vs Japanese for simplicity)
    if any(ord(char) > 128 for char in text):  # Checks for non-ASCII characters (mostly Japanese)
        return "ja"
    return "en"  # Default to English if it's not detected as Japanese

def format_translations(translations, original_content):
    formatted_translations = []
    for language, translation in translations.items():
        language_name = LANGUAGE_NAMES.get(language, language.capitalize())
        formatted_translations.append(
            f"<details>\n<summary>{language_name}</summary>\n\n{translation}\n</details>"
        )
    
    return "\n\n".join(formatted_translations) + f"\n\n{COMMENT_ORIGINAL_MARKER}\n\n{original_content}"

def translate_content(content, original_language):
    translations = {}
    target_languages = ["ja", "fr"] if original_language == "en" else ["en"]
    
    for language in target_languages:
        translation = translate_text(content, language)
        if translation:
            translations[language] = translation
    
    return translations

def translate_comment(comment):
    if not comment.body or COMMENT_ORIGINAL_MARKER in comment.body:
        return False

    original_content = comment.body.strip()
    original_language = detect_language(original_content)
    translations = translate_content(original_content, original_language)
    
    if translations:
        updated_body = format_translations(translations, original_content)
        comment.edit(body=updated_body)
        return True
    
    return False

def main():
    if not all([GITHUB_TOKEN, REPO_NAME, ISSUE_NUMBER, COMMENT_ID]):
        print("Missing required environment variables")
        return

    try:
        issue_number = int(ISSUE_NUMBER)
        comment_id = int(COMMENT_ID)
        
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        issue = repo.get_issue(number=issue_number)
        comment = issue.get_comment(comment_id)

        if translate_comment(comment):
            # Only add the translated label if it's not already present
            labels = [label.name for label in issue.labels]
            if TRANSLATED_LABEL not in labels:
                issue.add_to_labels(TRANSLATED_LABEL)

    except ValueError as ve:
        print(f"Invalid number format: {ve}")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()