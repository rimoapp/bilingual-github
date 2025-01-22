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
ORIGINAL_MARKER = "Original Content:"

LANGUAGE_NAMES = {
    "ja": "日本語",
    "en": "English"
}

def get_original_content(issue_body):
    if ORIGINAL_MARKER in issue_body:
        parts = issue_body.split(ORIGINAL_MARKER)
        return parts[1].strip()
    return issue_body.strip()

def detect_language(text):
    if any(ord(char) > 128 for char in text):
        return "ja"
    return "en"

def translate_issue(issue, target_languages):
    if not issue.body:
        return False

    original_content = get_original_content(issue.body)
    if not original_content:
        return False

    original_title = issue.title
    content_language = detect_language(original_content)
    target_lang = "ja" if content_language == "en" else "en"
    translated_title = translate_text(original_title, target_lang)

    translations = []
    for language in target_languages:
        translation = translate_text(original_content, language)
        if translation:
            language_name = LANGUAGE_NAMES.get(language, language.capitalize())
            translations.append(
                f"\n<h2>{translated_title}</h2>\n\n<details>\n<summary><b>{language_name}</b></summary>\n\n{translation}\n</details>"
            )

    original_language_name = LANGUAGE_NAMES.get(content_language, content_language.capitalize())
    if translations:
        updated_body = "\n\n".join(translations) + f"\n\n<b>{original_language_name}:</b>\n\n{original_content}\n"
        issue.edit(body=updated_body)
        return True

    return False

def main():
    if not all([GITHUB_TOKEN, REPO_NAME, ISSUE_NUMBER]):
        return

    try:
        issue_number = int(ISSUE_NUMBER)
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        issue = repo.get_issue(number=issue_number)

        original_content = get_original_content(issue.body)
        original_language = detect_language(original_content)

        if original_language == "en":
            target_languages = ["ja"]
        elif original_language == "ja":
            target_languages = ["en"]

        if translate_issue(issue, target_languages):
            issue.add_to_labels(TRANSLATED_LABEL)

    except ValueError:
        return
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()