import sys
import os
from github import Github

# Add the 'src' directory to sys.path
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from utils.translation import translate_text

# GitHub token and repository details
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = "rimoapp/bilingual-github"
TRANSLATED_LABEL = "translated"

def extract_original_body(issue_body):
    """Extract the original untranslated content from the issue body."""
    if not issue_body:
        return ""
    
    # Locate the start of translations in the issue body
    translation_marker = "**Translation to"
    marker_index = issue_body.find(translation_marker)
    
    # If no translation marker exists, the entire body is original
    if marker_index == -1:
        return issue_body.strip()
    
    # Extract the original body (before translations)
    return issue_body[:marker_index].strip()

def is_translated(issue_body, language):
    """Check if the issue body already contains a translation for a specific language."""
    return f"**Translation to {language}:**" in issue_body

def translate_issue(issue, target_languages):
    """Translate the issue body to the target languages."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body. Skipping.")
        return False

    # Extract the original untranslated content
    original_body = extract_original_body(issue.body)
    if not original_body:
        print(f"Issue #{issue.number} has no original content to translate. Skipping.")
        return False

    # Collect translations for any missing languages
    translations = []
    for language in target_languages:
        if is_translated(issue.body, language):
            print(f"Issue #{issue.number} already translated to {language}. Skipping.")
            continue

        print(f"Translating Issue #{issue.number} to {language}...")
        translation = translate_text(original_body, language)
        if translation:
            print(f"Translation to {language}: {translation}")
            translations.append(f"**Translation to {language}:**\n\n{translation}")
        else:
            print(f"Translation to {language} failed.")

    # If new translations were generated, update the issue
    if translations:
        updated_body = issue.body + "\n\n" + "\n\n".join(translations)
        print(f"Updating Issue #{issue.number} with new translations...")
        issue.edit(body=updated_body)
        print(f"Issue #{issue.number} updated successfully.")
        return True

    print(f"No new translations needed for Issue #{issue.number}.")
    return False

def main():
    """Main function to process GitHub issues."""
    # Initialize GitHub client
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    # Fetch open issues
    issues = repo.get_issues(state="open")

    for issue in issues:
        # Check if the issue body has changed since it was last translated
        if TRANSLATED_LABEL in [label.name for label in issue.labels]:
            print(f"Issue #{issue.number} has the translated label. Checking for changes...")
            current_original_body = extract_original_body(issue.body)
            last_translation_marker = "**Translation to"
            marker_index = issue.body.find(last_translation_marker)

            if marker_index != -1:
                previously_translated_body = issue.body[:marker_index].strip()
                if current_original_body == previously_translated_body:
                    print(f"Issue #{issue.number} has no new changes. Skipping.")
                    continue

        # Translate the issue and update the label if needed
        print(f"Processing Issue #{issue.number}: {issue.title}")
        translated = translate_issue(issue, ["ja", "fr"])

        # Add the 'translated' label if translations were added
        if translated and TRANSLATED_LABEL not in [label.name for label in issue.labels]:
            issue.add_to_labels(TRANSLATED_LABEL)
            print(f"Translated label added to Issue #{issue.number}.")

if __name__ == "__main__":
    # Debug GitHub token and repo details
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is not set. Exiting.")
        sys.exit(1)

    if not REPO_NAME:
        print("Error: REPO_NAME is not set. Exiting.")
        sys.exit(1)

    print(f"Starting translation script for repository: {REPO_NAME}")
    main()
