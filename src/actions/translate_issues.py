import sys
import os
from github import Github

# Dynamically add the 'src' directory to sys.path to ensure it can be found
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

# GitHub token and repository name
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = "rimoapp/bilingual-github"
TRANSLATED_LABEL = "translated"

def is_already_translated(issue, language):
    """Check if the translation for a specific language already exists in the issue body."""
    if issue.body and f"**Translation to {language}:**" in issue.body:
        return True
    return False

def get_new_content(original_body, current_body):
    """Get the newly added content in the issue body after an edit."""
    if original_body != current_body:
        # New content is the difference between original and current body
        return current_body[len(original_body):]
    return None

def translate_issue(issue, target_languages, original_body):
    """Translate the issue body to the target languages."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return

    new_content = get_new_content(original_body, issue.body)
    if not new_content:
        print(f"No new content in Issue #{issue.number}. Skipping translation.")
        return

    translations = []
    for language in target_languages:
        if is_already_translated(issue, language):
            print(f"Issue #{issue.number} already translated to {language}. Skipping.")
            continue

        translation = translate_text(new_content, language)
        if translation:
            translations.append(f"**Translation to {language}:**\n\n{translation}")

    if translations:
        # Place translations above the original body
        updated_body = "\n\n".join(translations) + "\n\n" + issue.body
        issue.edit(body=updated_body)
        print(f"Issue #{issue.number} translated successfully.")

def main():
    """Main function to process and translate GitHub issues."""
    # Initialize GitHub client
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    # Fetch all open issues
    issues = repo.get_issues(state="open")

    for issue in issues:
        # Check if the issue already has the translated label
        if TRANSLATED_LABEL in [label.name for label in issue.labels]:
            print(f"Issue #{issue.number} is already translated. Skipping.")
            continue

        # Save the original body before translation
        original_body = issue.body
        # Translate the issue and add the translated label
        print(f"Translating Issue #{issue.number}: {issue.title}")
        translate_issue(issue, ["ja", "fr"], original_body)

        # Add the translated label
        issue.add_to_labels(TRANSLATED_LABEL)
        print(f"Translated label added to Issue #{issue.number}.")

if __name__ == "__main__":
    main()
