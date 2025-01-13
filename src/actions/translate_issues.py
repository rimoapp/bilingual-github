import sys
import os
from github import Github

# Dynamically add the 'src' directory to sys.path to ensure it can be found
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from utils.translation import translate_text

# GitHub token and repository name (dynamic detection for target repo)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = os.getenv("GITHUB_REPOSITORY", "").strip()
TRANSLATED_LABEL = "translated"

# Get issue number from the environment variable
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "").strip()

def get_original_content(issue_body):
    """
    Extract only the original content from the issue body by removing all translations.
    Returns the content that appears before any translation markers.
    """
    # Split on first occurrence of "Translation to" (case insensitive)
    parts = issue_body.lower().split("**translation to", 1)
    if len(parts) > 1:
        # Return the original content, using the original case from issue_body
        return issue_body[:len(parts[0])].strip()
    return issue_body.strip()

def translate_issue(issue, target_languages):
    """
    Translate the issue body to the target languages, replacing any existing translations.
    """
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return False

    # Get only the original content, removing all existing translations
    original_content = get_original_content(issue.body)
    if not original_content:
        print(f"Could not identify original content for Issue #{issue.number}. Skipping.")
        return False

    # Translate the original content into target languages
    translations = []
    for language in target_languages:
        print(f"Translating content to {language}...")
        try:
            translation = translate_text(original_content, language)
            translations.append(f"**Translation to {language}:**\n\n{translation}")
        except Exception as e:
            print(f"Error translating to {language}: {e}")

    if translations:
        # Combine original content with the new translations, separated by newlines
        updated_body = f"{original_content}\n\n" + "\n\n".join(translations)
        print(f"Updating issue #{issue.number} with new translations...")
        issue.edit(body=updated_body)
        print(f"Issue #{issue.number} updated successfully.")
        return True
    else:
        print(f"No translations were added for Issue #{issue.number}.")
        return False

def main():
    """Main function to process and translate GitHub issues."""
    # Initialize GitHub client
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is not set.")
        return
    if not REPO_NAME:
        print("Error: GITHUB_REPOSITORY is not set.")
        return
    if not ISSUE_NUMBER:
        print("Error: ISSUE_NUMBER is not set.")
        return

    # Convert ISSUE_NUMBER to integer
    try:
        issue_number = int(ISSUE_NUMBER)
    except ValueError:
        print(f"Error: Invalid issue number '{ISSUE_NUMBER}'")
        return

    g = Github(GITHUB_TOKEN)

    try:
        repo = g.get_repo(REPO_NAME)
    except Exception as e:
        print(f"Error accessing repository {REPO_NAME}: {e}")
        return

    # Fetch the specific issue
    try:
        issue = repo.get_issue(number=issue_number)
    except Exception as e:
        print(f"Error fetching Issue #{issue_number} from {REPO_NAME}: {e}")
        return

    # Translate the issue
    translated = translate_issue(issue, ["ja", "fr"])

    # Add the translated label only if translation was successful
    if translated:
        try:
            issue.add_to_labels(TRANSLATED_LABEL)
            print(f"Translated label added to Issue #{issue.number}.")
        except Exception as e:
            print(f"Error adding label to Issue #{issue.number}: {e}")

if __name__ == "__main__":
    main()