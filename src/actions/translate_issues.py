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

def is_already_translated(issue, language):
    """Check if the translation for a specific language already exists in the issue body."""
    if issue.body and f"**Translation to {language}:**" in issue.body:
        return True
    return False

def translate_issue(issue, target_languages):
    """Translate the issue body to the target languages."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return

    # Check if the issue already has translations for all target languages
    untranslated_languages = [
        language for language in target_languages
        if not is_already_translated(issue, language)
    ]

    if not untranslated_languages:
        print(f"Issue #{issue.number} is already fully translated. Skipping.")
        return

    # Translate the issue to all remaining languages
    translations = []
    for language in untranslated_languages:
        print(f"Calling translate_text for {language}...")
        translation = translate_text(issue.body, language)
        
        # Check if translation was successful
        if translation:
            print(f"Translation for {language}: {translation}")
            translations.append(f"**Translation to {language}:**\n\n{translation}")
        else:
            print(f"Translation failed for {language}.")
    
    if translations:
        # Append translations below the original body
        updated_body = issue.body + "\n\n" + "\n\n".join(translations)
        print(f"Updating issue #{issue.number} with new body...")
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

        # Translate the issue and add the translated label
        print(f"Translating Issue #{issue.number}: {issue.title}")
        translate_issue(issue, ["ja", "fr"])

        # Add the translated label
        issue.add_to_labels(TRANSLATED_LABEL)
        print(f"Translated label added to Issue #{issue.number}.")

if __name__ == "__main__":
    main()
