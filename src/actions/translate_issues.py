import sys
import os
from github import Github

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

def translate_edited_issue(issue, target_languages):
    """Translate only newly added/edited content in an issue."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return False

    # Check if the issue has been updated
    if issue.updated_at > issue.created_at:
        print(f"Issue #{issue.number} has been updated. Processing edits...")
    else:
        print(f"Issue #{issue.number} has not been updated since creation. Forcing processing...")

    # Extract original and translated content
    body_lines = issue.body.splitlines()
    original_content = []
    existing_translations = []

    for line in body_lines:
        if line.strip().startswith("**Translation to"):
            existing_translations.append(line.strip())
        else:
            original_content.append(line.strip())

    original_body = "\n".join(original_content).strip()
    if not original_body:
        print(f"Original content for Issue #{issue.number} is empty. Skipping translation.")
        return False

    # Extract already translated languages
    translated_languages = [
        line.split(":")[1].strip()
        for line in existing_translations
        if "**Translation to" in line
    ]

    # Translate the newly added/edited content
    translations = []
    for language in target_languages:
        if language in translated_languages:
            print(f"Issue #{issue.number} already translated to {language}. Skipping.")
            continue

        print(f"Translating updated content to {language}...")
        try:
            translation = translate_text(original_body, language)
            translations.append(f"**Translation to {language}:**\n\n{translation}")
        except Exception as e:
            print(f"Error translating to {language}: {e}")

    if translations:
        updated_body = issue.body + "\n\n" + "\n\n".join(translations)
        issue.edit(body=updated_body)
        print(f"Updated Issue #{issue.number} with translations.")
        return True
    else:
        print(f"No translations added for Issue #{issue.number}.")
        return False

def is_translation_present(issue, language):
    """Check if the translation for a specific language already exists in the issue body."""
    if issue.body and f"**Translation to {language}:**" in issue.body:
        return True
    return False

def translate_issue(issue, target_languages):
    """Translate the issue body to the target languages."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return False  # Return False if no translation was performed

    translations = []
    for language in target_languages:
        if is_translation_present(issue, language):
            print(f"Issue #{issue.number} already translated to {language}. Skipping.")
            continue

        print(f"Calling translate_text for {language}...")
        try:
            translation = translate_text(issue.body, language)
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
        return True  # Return True if translation was performed
    else:
        return False  # Return False if no translation was performed

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

        # If the issue has no translation label, treat it as a new issue
        if TRANSLATED_LABEL not in labels and EDIT_TRANSLATED_LABEL not in labels:
            print(f"Translating new Issue #{issue.number}: {issue.title}")
            translated = translate_issue(issue, ["ja", "fr"])

            # Add the translated label only if translation was successful
            if translated:
                try:
                    issue.add_to_labels(TRANSLATED_LABEL)
                    print(f"Translated label added to Issue #{issue.number}.")
                except Exception as e:
                    print(f"Error adding label to Issue #{issue.number}: {e}")

        # Check if the issue has been edited
        elif issue.updated_at > issue.created_at and EDIT_TRANSLATED_LABEL not in labels:
            print(f"Issue #{issue.number} was edited. Translating newly added content...")
            translated = translate_edited_issue(issue, ["ja", "fr"])

            # Add the edit-translated label only if translation was successful
            if translated:
                try:
                    issue.add_to_labels(EDIT_TRANSLATED_LABEL)
                    print(f"Edit-translated label added to Issue #{issue.number}.")
                except Exception as e:
                    print(f"Error adding label to Issue #{issue.number}: {e}")


if __name__ == "__main__":
    main()
