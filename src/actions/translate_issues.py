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

def translate_edited_issue(issue, target_languages):
    """Translate only the newly added content in an edited issue."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return False  # No translation was performed

    # Check if the issue has already been translated
    translations = []
    original_translations = []

    # Split the body to separate original and translated parts
    if "**Translation to" in issue.body:
        split_body = issue.body.split("**Translation to")
        original_body = split_body[-1].strip()  # Assume the last part is the original text
        original_translations = split_body[:-1]  # Everything before is considered translated parts
    else:
        original_body = issue.body

    # Identify the new part of the issue body that was edited
    new_content = original_body  # For simplicity, we consider the whole body edited (can be optimized)

    # Translate the new content
    for language in target_languages:
        if is_translation_present(issue, language):
            print(f"Issue #{issue.number} already translated to {language}. Skipping.")
            continue

        print(f"Translating new content for {language}...")
        try:
            translation = translate_text(new_content, language)
        except Exception as e:
            print(f"Error during translation for {language}: {e}")
            translation = None

        # Check if translation was successful
        if translation:
            print(f"New translation for {language}: {translation}")
            translations.append(f"**Translation to {language}:**\n\n{translation}")
        else:
            print(f"Translation failed for {language}.")

    if translations:
        # Combine new translations with original translations and the issue body
        updated_body = "\n\n".join(original_translations + translations) + "\n\n" + original_body
        print(f"Updating issue #{issue.number} with new translations...")
        issue.edit(body=updated_body)
        print(f"New translations added to Issue #{issue.number}.")
        return True  # Return True if new translations were added
    else:
        return False  # Return False if no new translations were added


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
