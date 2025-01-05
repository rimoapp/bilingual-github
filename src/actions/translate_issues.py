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

def translate_issue(issue, target_languages):
    """Translate the issue body to the target languages."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body. Skipping.")
        return

    translations = []
    for language in target_languages:
        # Skip if translation already exists
        if f"**Translation to {language}:**" in issue.body:
            print(f"Issue #{issue.number} already translated to {language}. Skipping.")
            continue

        # Perform translation
        print(f"Translating Issue #{issue.number} to {language}...")
        translation = translate_text(issue.body, language)
        if translation:
            print(f"Translation to {language} completed.")
            translations.append(f"**Translation to {language}:**\n\n{translation}")
        else:
            print(f"Translation to {language} failed.")

    # Update issue with translations
    if translations:
        updated_body = issue.body + "\n\n" + "\n\n".join(translations)
        print(f"Updating Issue #{issue.number}...")
        issue.edit(body=updated_body)
        print(f"Issue #{issue.number} updated successfully.")

def main():
    """Main function to process GitHub issues."""
    # Initialize GitHub client
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    # Fetch open issues
    issues = repo.get_issues(state="open")

    for issue in issues:
        # Skip if the translated label already exists
        if TRANSLATED_LABEL in [label.name for label in issue.labels]:
            print(f"Issue #{issue.number} already has the translated label. Skipping.")
            continue

        # Translate issue and add the label
        translate_issue(issue, ["ja", "fr"])
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
