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
ORIGINAL_LANGUAGE_MARKER = "<!-- original_language:"
EDIT_MARKER = "<!-- last_processed_content:"

LANGUAGE_NAMES = {
    "ja": "日本語",
    "en": "English"
}

def get_original_content(issue_body):
    if ORIGINAL_MARKER in issue_body:
        parts = issue_body.split(ORIGINAL_MARKER)
        return parts[1].split(ORIGINAL_LANGUAGE_MARKER)[0].strip()
    return issue_body.strip()

def detect_language(text):
    if any(ord(char) > 128 for char in text):
        return "ja"
    return "en"

def extract_original_language(issue_body):
    if ORIGINAL_LANGUAGE_MARKER in issue_body:
        start = issue_body.find(ORIGINAL_LANGUAGE_MARKER) + len(ORIGINAL_LANGUAGE_MARKER)
        end = issue_body.find("-->", start)
        return issue_body[start:end].strip()
    return None

def extract_last_processed_content(issue_body):
    if EDIT_MARKER in issue_body:
        start = issue_body.find(EDIT_MARKER) + len(EDIT_MARKER)
        end = issue_body.find("-->", start)
        return issue_body[start:end].strip()
    return ""

def update_translations(original_content, original_language, issue_body, target_languages, last_processed_content):
    new_content = original_content[len(last_processed_content):].strip()
    if not new_content:
        return "", last_processed_content

    new_translations = []
    for language in target_languages:
        translation = translate_text(new_content, language)
        if translation:
            language_name = LANGUAGE_NAMES.get(language, language.capitalize())
            new_translations.append(
                f"<details>\n<summary><b>{language_name}</b></summary>\n\n{translation}\n</details>"
            )

    updated_last_processed_content = original_content
    return "\n".join(new_translations), updated_last_processed_content

def translate_issue(issue, original_content, original_language, issue_body, target_languages, last_processed_content):
    new_translations, updated_last_processed_content = update_translations(
        original_content, original_language, issue_body, target_languages, last_processed_content
    )

    if new_translations:
        updated_body = (
            issue_body.split(ORIGINAL_MARKER)[0] +  # Preserve existing translations
            f"\n\n{new_translations}\n\n"
            f"<details>\n<summary><b>{LANGUAGE_NAMES.get(original_language, original_language.capitalize())}</b></summary>\n\n{original_content}\n</details>\n\n"
            f"{ORIGINAL_LANGUAGE_MARKER}{original_language}-->\n"
            f"{EDIT_MARKER}{updated_last_processed_content}-->"
        )
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

        original_language = extract_original_language(issue.body) or detect_language(issue.body)
        original_content = get_original_content(issue.body)
        last_processed_content = extract_last_processed_content(issue.body)

        target_languages = ["ja"] if original_language == "en" else ["en"]

        if translate_issue(issue, original_content, original_language, issue.body, target_languages, last_processed_content):
            if TRANSLATED_LABEL not in [label.name for label in issue.labels]:
                issue.add_to_labels(TRANSLATED_LABEL)

    except ValueError:
        return
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()
