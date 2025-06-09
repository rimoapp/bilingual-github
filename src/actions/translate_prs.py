import sys
import os
from github import Github
import re

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from utils.translation import translate_text

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = os.getenv("GITHUB_REPOSITORY", "").strip()
TRANSLATED_LABEL = "translated"
NEEDS_TRANSLATION_LABEL = "need translation"
PR_NUMBER = os.getenv("PR_NUMBER", "").strip()
COMMENT_ID = os.getenv("COMMENT_ID", "").strip()
ORIGINAL_CONTENT_MARKER = "Original Content:"
EVENT_NAME = os.getenv("GITHUB_EVENT_NAME", "").strip()

LANGUAGE_NAMES = {
    "ja": "日本語",
    "en": "English"
}

def get_original_content(content):
    if ORIGINAL_CONTENT_MARKER in content:
        parts = content.split(ORIGINAL_CONTENT_MARKER, 1)
        original = parts[1].lstrip()
        original = re.sub(r'^(<br>\s*)+', '', original)
        return original.strip()
    return content.strip()

def detect_language(text):
    # Unicode ranges for Japanese characters
    HIRAGANA = '\u3040-\u309F'
    KATAKANA = '\u30A0-\u30FF'
    KANJI = '\u4E00-\u9FFF'
    HALF_WIDTH_KATAKANA = '\uFF60-\uFF9F'
    
    # Check if text contains any Japanese character
    jp_pattern = f'[{HIRAGANA}{KATAKANA}{KANJI}{HALF_WIDTH_KATAKANA}]'
    has_japanese = bool(re.search(jp_pattern, text))
    
    # If any Japanese character is found, original is Japanese, translate to English
    # Otherwise, original is English, translate to Japanese
    return "ja" if has_japanese else "en"

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
            formatted_parts.append(f"## {translation}")

    for language, translation in body_translations.items():
        if translation and language != original_language:
            language_name = LANGUAGE_NAMES.get(language, language.capitalize())
            formatted_parts.append(
                f"<details>\n<summary><b>{language_name}</b></summary>\n\n{translation}\n</details><br>"
            )

    original_lang_name = LANGUAGE_NAMES.get(original_language, original_language.capitalize())
    formatted_parts.append(f"<b>{ORIGINAL_CONTENT_MARKER}</b>\n\n{original_content}")

    return "\n\n".join(formatted_parts).strip()

def translate_content(content, original_language):
    translations = {original_language: content}
    target_languages = get_target_languages(original_language)
    
    for language in target_languages:
        translation = translate_text(content, language)
        if translation:
            translations[language] = translation
    
    return translations

def translate_pr(pr, original_content, original_language, pr_title, pr_body):
    title_translations = translate_content(pr_title, original_language)
    body_translations = translate_content(pr_body, original_language)
    updated_body = format_translations(title_translations, body_translations, original_content, original_language)
    
    if updated_body != pr.body:
        pr.edit(body=updated_body)
        return True
    
    return False

def translate_pr_comment(comment):
    if not comment.body:
        return False
        
    current_content = comment.body.strip()
    original_content = get_original_content(current_content)
    original_language = detect_language(original_content)
    translations = translate_content(original_content, original_language)
    
    if translations:
        updated_body = format_translations({}, translations, original_content, original_language)
        if updated_body != comment.body:
            comment.edit(body=updated_body)
            return True
    
    return False

def should_translate(pr):
    labels = [label.name.lower() for label in pr.labels]
    
    if NEEDS_TRANSLATION_LABEL.lower() in labels:
        return True
    
    if TRANSLATED_LABEL.lower() in labels and NEEDS_TRANSLATION_LABEL.lower() in labels:
        return True
        
    return False

def main():
    if not all([GITHUB_TOKEN, REPO_NAME, PR_NUMBER]):
        print("Missing required environment variables")
        return
    
    try:
        pr_number = int(PR_NUMBER)
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        pr = repo.get_pull(number=pr_number)
        
        if not should_translate(pr):
            print(f"PR #{pr_number} does not require translation at this time.")
            return
        
        if COMMENT_ID:
            comment_id = int(COMMENT_ID)
            # Check if it's a review comment or an issue comment
            if EVENT_NAME == 'pull_request_review_comment':
                comment = pr.get_review_comment(comment_id)
            else:
                comment = pr.get_issue_comment(comment_id)
            if translate_pr_comment(comment):
                labels = [label.name.lower() for label in pr.labels]
                if TRANSLATED_LABEL.lower() not in labels:
                    pr.add_to_labels(TRANSLATED_LABEL)
            return
        
        # Otherwise translate the PR body
        original_content = get_original_content(pr.body)
        original_language = detect_language(original_content)
        pr_title = pr.title
        pr_body = get_original_content(pr.body)
        
        pr_translated = translate_pr(pr, original_content, original_language, pr_title, pr_body)

        # Translate all comments on the PR
        comments = pr.get_issue_comments()
        comments_translated = False
        for comment in comments:
            if translate_pr_comment(comment):
                comments_translated = True

        # Translate all review comments on the PR
        review_comments = pr.get_review_comments()
        for comment in review_comments:
            if translate_pr_comment(comment):
                comments_translated = True

        if pr_translated or comments_translated:
            labels = [label.name.lower() for label in pr.labels]
            if TRANSLATED_LABEL.lower() not in labels:
                pr.add_to_labels(TRANSLATED_LABEL)
    
    except ValueError as ve:
        print(f"Invalid number format: {ve}")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main() 