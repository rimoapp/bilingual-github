import sys
import os
from github import Github

# Set up the script directory and source directory for importing modules
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from utils.translation import translate_text

# Environment variables and constants
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = os.getenv("GITHUB_REPOSITORY", "").strip()
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "").strip()
TRANSLATED_LABEL = "translated"
ORIGINAL_MARKER = "Original Content:"

LANGUAGE_NAMES = {
    "ja": "日本語",
    "en": "English"
}

def get_original_content(issue_body):
    """Extract the original content from the issue body."""
    if ORIGINAL_MARKER in issue_body:
        parts = issue_body.split(ORIGINAL_MARKER)
        return parts[1].strip()
    return issue_body.strip()

def detect_language(issue_body):
    """Detect the language of the issue body based on character encoding."""
    if any(ord(char) > 128 for char in issue_body):
        return "ja"
    return "en"

def translate_issue(issue, target_languages):
    """Translate the issue content into the target languages."""
    if not issue.body:
        return False

    original_content = get_original_content(issue.body)
    if not original_content:
        return False

    translations = []
    for language in target_languages:
        translation = translate_text(original_content, language)
        if translation:
            language_name = LANGUAGE_NAMES.get(language, language.capitalize())
            translations.append(f"\n{language_name}\n\n{translation}\n")

    if translations:
        updated_body = "\n\n".join(translations) + f"\n\n{ORIGINAL_MARKER}\n\n{original_content}"
        issue.edit(body=updated_body)
        return True

    return False

def main():
    """Main function to handle the translation of GitHub issues."""
    if not all([GITHUB_TOKEN, REPO_NAME, ISSUE_NUMBER]):
        return

    try:
        issue_number = int(ISSUE_NUMBER)
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        issue = repo.get_issue(number=issue_number)

        original_language = detect_language(issue.body)

        if original_language == "en":
            target_languages = ["ja"]
        elif original_language == "ja":
            target_languages = ["en"]
        else:
            target_languages = []

        if translate_issue(issue, target_languages):
            issue.add_to_labels(TRANSLATED_LABEL)

    except ValueError:
        print("Invalid issue number.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
