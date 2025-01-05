import sys
import os
from github import Github
import time

# Dynamically add the 'src' directory to sys.path to ensure it can be found
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from utils.translation import translate_text

# GitHub token and repository name
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = "rimoapp/bilingual-github"
TRANSLATED_LABEL = "translated"
EDIT_TRANSLATED_LABEL = "edit-translated"

def is_translation_present(issue, language):
    """Check if the translation for a specific language already exists in the issue body."""
    if issue.body and f"**Translation to {language}:**" in issue.body:
        return True
    return False

def detect_new_content(original_body, current_body):
    """Detect new or modified content in the issue body."""
    if not original_body:
        return current_body  # If there was no original body, the entire current body is new
    if original_body == current_body:
        return None  # No changes detected
    # Return only the part of the current body that's different from the original
    return current_body[len(original_body):]

def translate_issue(issue, target_languages, original_body):
    """Translate the issue body to the target languages."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return

    # Detect new or modified content in the issue body
    new_content = detect_new_content(original_body, issue.body)
    if not new_content:
        print(f"No new content in Issue #{issue.number}. Skipping translation.")
        return

    translations = []
    for language in target_languages:
        if is_translation_present(issue, language):
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
        # Fetch the labels on the issue
        labels = [label.name for label in issue.labels]

        # If the issue has no translation or edit label, treat it as a new issue
        if TRANSLATED_LABEL not in labels and EDIT_TRANSLATED_LABEL not in labels:
            print(f"Translating new Issue #{issue.number}: {issue.title}")
            translate_issue(issue, ["ja", "fr"], issue.body)

            # Add the translated label
            try:
                issue.add_to_labels(TRANSLATED_LABEL)
                print(f"Translated label added to Issue #{issue.number}.")
            except Exception as e:
                print(f"Error adding label to Issue #{issue.number}: {e}")

        # Check if the issue has been edited
        elif issue.updated_at > issue.created_at and EDIT_TRANSLATED_LABEL not in labels:
            print(f"Issue #{issue.number} was edited. Translating edits...")
            translate_issue(issue, ["ja", "fr"], issue.body)

            # Add the edit-translated label
            try:
                issue.add_to_labels(EDIT_TRANSLATED_LABEL)
                print(f"Edit-translated label added to Issue #{issue.number}.")
            except Exception as e:
                print(f"Error adding label to Issue #{issue.number}: {e}")

if __name__ == "__main__":
    main()
