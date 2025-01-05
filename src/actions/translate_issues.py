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
TRANSLATION_MARKER = "<!-- TRANSLATION_MARKER -->"

def extract_translation_marker(issue_body):
    """Extract the marker for tracking the last translated content."""
    if TRANSLATION_MARKER in issue_body:
        return issue_body.split(TRANSLATION_MARKER)[-1].strip()
    return ""

def update_translation_marker(issue, last_translated_content):
    """Add or update the translation marker in the issue body."""
    marker_section = f"{TRANSLATION_MARKER}\n{last_translated_content}"
    if TRANSLATION_MARKER in issue.body:
        # Update existing marker
        updated_body = issue.body.split(TRANSLATION_MARKER)[0].strip() + "\n\n" + marker_section
    else:
        # Add a new marker
        updated_body = issue.body.strip() + "\n\n" + marker_section
    issue.edit(body=updated_body)

def translate_issue(issue, target_languages):
    """Translate the issue body to the target languages."""
    if not issue.body:
        print(f"Issue #{issue.number} has no body to translate. Skipping.")
        return

    # Extract last translated content marker
    last_marker = extract_translation_marker(issue.body)

    # Detect new or modified content
    new_content = issue.body.split(TRANSLATION_MARKER)[0].strip() if TRANSLATION_MARKER in issue.body else issue.body
    new_content = new_content.replace(last_marker, "").strip()

    if not new_content:
        print(f"No new content in Issue #{issue.number}. Skipping translation.")
        return

    translations = []
    for language in target_languages:
        print(f"Translating Issue #{issue.number} to {language}...")
        try:
            translation = translate_text(new_content, language)
        except Exception as e:
            print(f"Error during translation for {language}: {e}")
            continue

        if translation:
            translations.append(f"**Translation to {language}:**\n\n{translation}")
            print(f"Translation for {language}: {translation}")
        else:
            print(f"Translation failed for {language}.")

    if translations:
        # Add translations above the original body without duplicating the original content
        existing_content = issue.body.split(TRANSLATION_MARKER)[0].strip() if TRANSLATION_MARKER in issue.body else issue.body
        updated_body = "\n\n".join(translations) + "\n\n" + existing_content + f"\n\n{TRANSLATION_MARKER}\n{new_content}"
        issue.edit(body=updated_body)
        print(f"Issue #{issue.number} updated with translations.")

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
        # Skip already translated issues unless they are edited
        if TRANSLATED_LABEL in [label.name for label in issue.labels]:
            print(f"Issue #{issue.number} already translated. Checking for edits...")
        else:
            print(f"Processing new Issue #{issue.number}: {issue.title}")

        # Translate and add the "translated" label if necessary
        translate_issue(issue, ["ja", "fr"])
        if TRANSLATED_LABEL not in [label.name for label in issue.labels]:
            try:
                issue.add_to_labels(TRANSLATED_LABEL)
                print(f"Translated label added to Issue #{issue.number}.")
            except Exception as e:
                print(f"Error adding label to Issue #{issue.number}: {e}")

if __name__ == "__main__":
    main()
