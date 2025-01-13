import sys
import os
from github import Github

script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.append(src_dir)

from utils.translation import translate_text

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO_NAME = os.getenv("GITHUB_REPOSITORY", "").strip()
TRANSLATED_LABEL = "translated"
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER", "").strip()
ORIGINAL_MARKER = "**Original Content:**"
TRANSLATION_MARKER = "**Translation to"

def get_original_content(issue_body):
    if ORIGINAL_MARKER in issue_body:
        parts = issue_body.split(ORIGINAL_MARKER)
        return parts[1].strip()

    parts = issue_body.split(TRANSLATION_MARKER)
    if len(parts) == 1:
        return issue_body.strip()
        
    translations_at_top = issue_body.lower().startswith(TRANSLATION_MARKER.lower())
    
    if translations_at_top:
        sections = issue_body.split("\n\n")
        for i, section in enumerate(sections):
            if not section.lower().startswith(TRANSLATION_MARKER.lower()):
                return "\n\n".join(sections[i:]).strip()
        return ""
    
    return parts[0].strip()

def translate_issue(issue, target_languages):
    if not issue.body:
        return False

    original_content = get_original_content(issue.body)
    if not original_content:
        return False

    translations = []
    for language in target_languages:
        translation = translate_text(original_content, language)
        if translation:
            translations.append(f"{TRANSLATION_MARKER} {language}:**\n\n{translation}")

    if translations:
        updated_body = "\n\n".join(translations) + "\n\n" + ORIGINAL_MARKER + "\n\n" + original_content
        issue.edit(body=updated_body)
        return True
        
    return False

def main():
    if not all([GITHUB_TOKEN, REPO_NAME, ISSUE_NUMBER]):
        return

    try:
        issue_number = int(ISSUE_NUMBER)
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        issue = repo.get_issue(number=issue_number)
        
        if translate_issue(issue, ["ja", "fr"]):
            issue.add_to_labels(TRANSLATED_LABEL)
            
    except ValueError:
        return
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()