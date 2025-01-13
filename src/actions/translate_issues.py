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

# Define constants for content markers
ORIGINAL_MARKER = "**Original Content:**"
TRANSLATION_MARKER = "**Translation to"

def get_original_content(issue_body):
    """
    Extract original content from the issue body, handling both orientations
    (translations before or after original content).
    """
    # Check if we have an explicit Original Content marker
    if ORIGINAL_MARKER in issue_body:
        parts = issue_body.split(ORIGINAL_MARKER)
        return parts[1].strip()

    # Split all content by translation markers
    parts = issue_body.split(TRANSLATION_MARKER)
    
    # If no translations exist yet, return the whole body
    if len(parts) == 1:
        return issue_body.strip()
        
    # Check the position of translations
    translations_at_top = issue_body.lower().startswith(TRANSLATION_MARKER.lower())
    
    if translations_at_top:
        # If translations are at the top, original content is after the last translation
        # Find the end of the last translation section
        sections = issue_body.split("\n\n")
        for i, section in enumerate(sections):
            if not section.lower().startswith(TRANSLATION_MARKER.lower()):
                # Found the start of original content
                return "\n\n".join(sections[i:]).strip()
        return ""  # No original content found
    else:
        # If translations are at the bottom, original content is before the first translation
        return parts[0].strip()

def translate_issue(issue, target_languages):
    """
    Translate the issue body to the target languages, placing translations before the original content.
    """
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return False

    # Get only the original content, removing all existing translations
    original_content = get_original_content(issue.body)
    if not original_content:
        print(f"Could not identify original content for Issue #{issue.number}. Skipping.")
        return False

    print(f"Original content detected: {original_content[:100]}...")  # Debug log

    # Translate the original content into target languages
    translations = []
    for language in target_languages:
        print(f"Translating content to {language}...")
        try:
            translation = translate_text(original_content, language)
            translations.append(f"{TRANSLATION_MARKER} {language}:**\n\n{translation}")
        except Exception as e:
            print(f"Error translating to {language}: {e}")
            continue

    if translations:
        # Place translations before the original content with clear separation
        updated_body = "\n\n".join(translations) + "\n\n" + ORIGINAL_MARKER + "\n\n" + original_content
        print(f"Updating issue #{issue.number} with new translations...")
        try:
            issue.edit(body=updated_body)
            print(f"Issue #{issue.number} updated successfully.")
            return True
        except Exception as e:
            print(f"Error updating issue: {e}")
            return False
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