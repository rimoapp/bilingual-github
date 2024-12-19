from github import Github
from src.utils.translation import translate_text

GITHUB_TOKEN = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
REPO_NAME = "your_username/your_repository"

def translate_issue(issue, target_languages):
    for language in target_languages:
        translation = translate_text(issue.body, language)
        if translation:
            issue.create_comment(f"Translation to {language}:\n\n{translation}")

def main():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    issues = repo.get_issues(state="open")

    for issue in issues:
        translate_issue(issue, ["ja", "fr"])

if __name__ == "__main__":
    main()
