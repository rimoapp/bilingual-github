import sys
import os

# Dynamically add the 'src' directory to sys.path to ensure it can be found
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text  

from github import Github
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "rimoapp/bilingual-github"

def translate_issue(issue, target_languages):
    original_body = issue.body
    translations = []

    for language in target_languages:
        translation = translate_text(original_body, language)
        if translation:
            translations.append(f"Translation to {language}:\n\n{translation}")

    if translations:
        updated_body = f"{original_body}\n\n" + "\n\n".join(translations)
        issue.edit(body=updated_body)

def main():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    issues = repo.get_issues(state="open")

    for issue in issues:
        translate_issue(issue, ["ja", "fr"])

if __name__ == "__main__":
    main()
