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
REPO_NAME = os.getenv("GITHUB_REPOSITORY", "").strip()  # Detect the calling repo dynamically
TRANSLATED_LABEL = "translated"

# Get issue number from the environment variable (passed dynamically)
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "").strip()


def separate_original_content(issue_body, target_languages):
    """
    Extract only the original content from the issue body, excluding any translations.
    """
    lines = issue_body.splitlines()
    original_content = []
    in_translation_section = False

    for line in lines:
        if any(f"**Translation to {lang}:" in line for lang in target_languages):
            in_translation_section = True
        elif line.strip() == "" and in_translation_section:
            in_translation_section = False
        elif not in_translation_section:
            original_content.append(line)

    return "\n".join(original_content).strip()


def extract_new_content(original_content, existing_translations):
    """
    Extract new or modified content by comparing the original content
    against existing translations.
    """
    new_lines = []
    for line in original_content.splitlines():
        if not any(translation_marker in line for translation_marker in existing_translations):
            new_lines.append(line)
    return "\n".join(new_lines).strip()


def is_translation_present(issue, language):
    """Check if a translation for a specific language exists in the issue body."""
    marker = f"**Translation to {language}:**"
    return marker in issue.body if issue.body else False


def translate_issue(issue, target_languages):
    """
    Translate the issue body to the target languages, detecting new/edited content.
    """
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return False  # Return False if no translation was performed

    # Detect existing translations
    existing_translations = [f"**Translation to {lang}:**" for lang in target_languages]

    # Separate original content from translations
    original_content = separate_original_content(issue.body, target_languages)
    if not original_content:
        print(f"Could not identify original content for Issue #{issue.number}. Skipping.")
        return False

    # Extract new or modified content
    new_content = extract_new_content(original_content, existing_translations)
    print(new_content)
    if not new_content:
        print(f"No new content to translate for Issue #{issue.number}. Skipping.")
        return False

    translations = []
    for language in target_languages:
        # if is_translation_present(issue, language):
        #     print(f"Issue #{issue.number} already translated to {language}. Skipping.")
        #     continue

        print(f"Translating new content to {language}...")
        try:
            translation = translate_text(new_content, language)
            translations.append(f"**Translation to {language}:**\n\n{translation}")
        except Exception as e:
            print(f"Error translating to {language}: {e}")

    if translations:
        # Append translations below the existing body
        updated_body = issue.body + "\n\n" + "\n\n".join(translations)
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
