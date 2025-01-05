import sys
import os
from github import Github
import time

# Dynamically add the 'src' directory to sys.path to ensure it can be found
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)  # Append instead of insert

from utils.translation import translate_text

# GitHub token and repository name
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = "rimoapp/bilingual-github"
TRANSLATED_LABEL = "translated"

def get_existing_translations(issue_body):
    """Extract already present translations from the issue body."""
    translations = {}
    lines = issue_body.split("\n")
    current_language = None
    for line in lines:
        if line.startswith("**Translation to"):
            current_language = line.split("**Translation to ")[1].split(":**")[0]
        elif current_language and line.strip():  # Capture translation body
            translations[current_language] = translations.get(current_language, "") + line.strip() + "\n"
    return translations

def detect_new_content(issue_body, existing_translations):
    """Identify new content to translate by removing already translated sections."""
    for translation in existing_translations.values():
        issue_body = issue_body.replace(translation.strip(), "")
    return issue_body.strip()

def translate_issue(issue, target_languages):
    """Translate the issue body to the target languages."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return

    existing_translations = get_existing_translations(issue.body)
    new_content = detect_new_content(issue.body, existing_translations)
    if not new_content:
        print(f"No new content in Issue #{issue.number}. Skipping translation.")
        return

    translations = []
    for language in target_languages:
        if language in existing_translations:
            print(f"Issue #{issue.number} already translated to {language}. Skipping.")
            continue

        print(f"Calling translate_text for {language}...")
        try:
            translation = translate_text(new_content, language)
        except Exception as e:
            print(f"Error during translation for {language}: {e}")
            translation = None

        # Check if translation was successful
        if translation:
            print(f"Translation for {language}: {translation}")
            translations.append(f"**Translation to {language}:**\n\n{translation}")
        else:
            print(f"Translation failed for {language}.")
    
    if translations:
        # Place translations above the original body
        updated_body = "\n\n".join(translations) + "\n\n" + issue.body
        print(f"Updating issue #{issue.number} with new body...")
        issue.edit(body=updated_body)
        print(f"Issue #{issue.number} translated successfully.")

def main():
    """Main function to process and translate GitHub issues."""
    # Initialize GitHub client
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is not set.")
        return
    g = Github(GITHUB_TOKEN)

    try:
        repo = g.get_repo(REPO_NAME)
    except Exception as e:
        print(f"Error accessing repository {REPO_NAME}: {e}")
        return

    # Fetch all open issues
    try:
        issues = repo.get_issues(state="open")
    except Exception as e:
        print(f"Error fetching issues from {REPO_NAME}: {e}")
        return

    for issue in issues:
        # Translate the issue and add the translated label if it's not already present
        print(f"Processing Issue #{issue.number}: {issue.title}")
        translate_issue(issue, ["ja", "fr"])

        # Add the translated label if it doesn't already exist
        if TRANSLATED_LABEL not in [label.name for label in issue.labels]:
            try:
                issue.add_to_labels(TRANSLATED_LABEL)
                print(f"Translated label added to Issue #{issue.number}.")
            except Exception as e:
                print(f"Error adding label to Issue #{issue.number}: {e}")

if __name__ == "__main__":
    main()
