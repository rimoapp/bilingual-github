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
ORIGINAL_MARKER = "**Original Content:**"
ORIGINAL_TITLE_MARKER = "**Original Title:**"

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

    # Detect and translate title
    original_title = issue.title
    title_language = detect_language(original_title)
    translated_title = translate_text(original_title, target_languages[0])

    translations = []
    for language in target_languages:
        translation = translate_text(original_content, language)
        if translation:
            language_name = LANGUAGE_NAMES.get(language, language.capitalize())
            if language == target_languages[0]:  # Add translated title with the first translation
                translations.append(
                    f"\n{language_name}\n\nTitle: {translated_title}\n\n{translation}\n"
                )
            else:
                translations.append(
                    f"<details>\n<summary>{language_name}</summary>\n\n{translation}\n</details>"
                )

    if translations:
        updated_body = "\n\n".join(translations) + f"\n\n{ORIGINAL_TITLE_MARKER}\n\n{original_title}\n\n{ORIGINAL_MARKER}\n\n{original_content}"
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

        original_language = detect_language(issue.body)

        # Set target languages based on the detected language
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