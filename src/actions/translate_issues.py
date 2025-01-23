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

def detect_language(text):
    """Detect the language of the given text."""
    if any(ord(char) > 128 for char in text):
        return "ja"
    return "en"

def extract_original_language(issue_body):
    """Extract the original language marker from the issue body."""
    if ORIGINAL_LANGUAGE_MARKER in issue_body:
        start = issue_body.find(ORIGINAL_LANGUAGE_MARKER) + len(ORIGINAL_LANGUAGE_MARKER)
        end = issue_body.find("-->", start)
        return issue_body[start:end].strip()
    return None

def translate_issue(issue, original_content, original_language, target_languages):
    """Translate the issue title and body and update the issue."""
    # Translate the issue title
    translated_titles = {}
    for language in target_languages:
        translated_title = translate_text(issue.title, language)
        if translated_title:
            translated_titles[language] = translated_title

    # Translate the issue body
    translations = {}
    for language in target_languages:
        translation = translate_text(original_content, language)
        if translation:
            translations[language] = translation

    # Build the updated issue body
    updated_body = ""

    for language in target_languages:
        language_name = LANGUAGE_NAMES.get(language, language.capitalize())
        if language in translated_titles:
            updated_body += f"**{translated_titles[language]} ({language_name})**\n\n"
        if language in translations:
            updated_body += f"<details>\n<summary><b>{language_name}</b></summary>\n\n{translations[language]}\n</details>\n\n"

    updated_body += f"<h2>Original Content (English)</h2>\n\n{original_content}\n\n"
    updated_body += f"{ORIGINAL_LANGUAGE_MARKER}{original_language}-->"
    
    # Update the issue body with the new content
    issue.edit(body=updated_body)

    return True

def main():
    """Main function to handle the translation logic."""
    if not all([GITHUB_TOKEN, REPO_NAME, ISSUE_NUMBER]):
        return

    try:
        issue_number = int(ISSUE_NUMBER)
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        issue = repo.get_issue(number=issue_number)

        # Extract the original content and language
        original_content = get_original_content(issue.body)
        original_language = extract_original_language(issue.body) or detect_language(original_content)

        # Set target languages for translation
        target_languages = ["ja"] if original_language == "en" else ["en"]

        # Perform translation and update issue
        if translate_issue(issue, original_content, original_language, target_languages):
            if TRANSLATED_LABEL not in [label.name for label in issue.labels]:
                issue.add_to_labels(TRANSLATED_LABEL)

    except ValueError:
        return
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()