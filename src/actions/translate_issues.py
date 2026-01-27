import sys
import os
from github import Github

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from utils.translation import translate_text, detect_language

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = os.getenv("GITHUB_REPOSITORY", "").strip()
TRANSLATED_LABEL = "translated"
NEEDS_TRANSLATION_LABEL = "need translation"
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "").strip()
ORIGINAL_CONTENT_MARKER = "Original Content:"

LANGUAGE_NAMES = {
    "ja": "日本語",
    "en": "English"
}

def get_original_content(content):
    if ORIGINAL_CONTENT_MARKER in content:
        parts = content.split(ORIGINAL_CONTENT_MARKER)
        return parts[1].strip()
    return content.strip()

def get_target_languages(original_language):
    if original_language == "en":
        return ["ja"]
    elif original_language == "ja":
        return ["en"]
    return ["en"]

def format_translations(title_translations, body_translations, original_content, original_language):
    formatted_parts = []
    
    for language, translation in title_translations.items():
        if translation and language != original_language:
            language_name = LANGUAGE_NAMES.get(language, language.capitalize())
            formatted_parts.append(f"<h2>{translation}</h2>")
    
    for language, translation in body_translations.items():
        if translation and language != original_language:
            language_name = LANGUAGE_NAMES.get(language, language.capitalize())
            formatted_parts.append(f"\n\n<details>\n<summary><b>{language_name}</b></summary>\n\n{translation}\n</details><br>")
    
    original_lang_name = LANGUAGE_NAMES.get(original_language, original_language.capitalize())
    formatted_parts.append(f"<b>{ORIGINAL_CONTENT_MARKER}</b>\n{original_content}")
    
    return "\n\n".join(formatted_parts)

def translate_content(content, original_language):
    translations = {original_language: content}
    target_languages = get_target_languages(original_language)
    
    for language in target_languages:
        translation = translate_text(content, language)
        if translation:
            translations[language] = translation
    
    return translations

def translate_issue(issue, original_content, original_language, issue_title, issue_body):
    title_translations = translate_content(issue_title, original_language)
    body_translations = translate_content(issue_body, original_language)
    updated_body = format_translations(title_translations, body_translations, original_content, original_language)

    if updated_body != issue.body:
        issue.edit(body=updated_body)
        return True

    return False


def format_comment_translations(translations, original_content, original_language):
    """Format translations for a comment (without title)."""
    formatted_parts = []

    for language, translation in translations.items():
        if translation and language != original_language:
            language_name = LANGUAGE_NAMES.get(language, language.capitalize())
            formatted_parts.append(
                f"<details>\n<summary><b>{language_name}</b></summary>\n\n{translation}\n</details><br>"
            )

    formatted_parts.append(f"<b>{ORIGINAL_CONTENT_MARKER}</b>\n{original_content}")

    return "\n\n".join(formatted_parts)


def translate_comment(comment):
    """Translate a single comment. Returns True if translation was performed."""
    if not comment.body:
        return False

    current_content = comment.body.strip()
    original_content = get_original_content(current_content)

    original_language = detect_language(original_content)
    translations = translate_content(original_content, original_language)

    if translations:
        updated_body = format_comment_translations(translations, original_content, original_language)
        if updated_body != comment.body:
            comment.edit(body=updated_body)
            return True

    return False

def should_translate(issue):
    labels = [label.name.lower() for label in issue.labels]
    
    if NEEDS_TRANSLATION_LABEL.lower() in labels:
        return True
    
    if TRANSLATED_LABEL.lower() in labels and NEEDS_TRANSLATION_LABEL.lower() in labels:
        return True
        
    return False

def main():
    if not all([GITHUB_TOKEN, REPO_NAME, ISSUE_NUMBER]):
        print("Missing required environment variables")
        return

    try:
        issue_number = int(ISSUE_NUMBER)
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        issue = repo.get_issue(number=issue_number)

        if not should_translate(issue):
            print(f"Issue #{issue_number} does not require translation at this time.")
            return

        # Translate the issue body
        print(f"Translating issue #{issue_number}...")
        original_content = get_original_content(issue.body)
        original_language = detect_language(original_content)
        issue_title = issue.title
        issue_body = get_original_content(issue.body)

        issue_translated = translate_issue(issue, original_content, original_language, issue_title, issue_body)
        if issue_translated:
            print(f"Successfully translated issue #{issue_number}")
        else:
            print(f"Issue #{issue_number} was already translated or unchanged")

        # Translate all comments on the issue
        print(f"Translating comments on issue #{issue_number}...")
        comments = issue.get_comments()
        comments_translated = False
        comment_count = 0

        for comment in comments:
            comment_count += 1
            print(f"Processing comment #{comment.id} ({comment_count})...")
            if translate_comment(comment):
                comments_translated = True
                print(f"Successfully translated comment #{comment.id}")
            else:
                print(f"Comment #{comment.id} was already translated or empty")

        print(f"Processed {comment_count} comments on issue #{issue_number}")

        # Add translated label if any translation was performed
        if issue_translated or comments_translated:
            labels = [label.name.lower() for label in issue.labels]
            if TRANSLATED_LABEL.lower() not in labels:
                issue.add_to_labels(TRANSLATED_LABEL)
                print(f"Added '{TRANSLATED_LABEL}' label to issue #{issue_number}")

    except ValueError as ve:
        print(f"Invalid number format: {ve}")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()