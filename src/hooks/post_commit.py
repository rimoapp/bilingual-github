import os
import sys
import subprocess
from pathlib import Path
from difflib import unified_diff

# Add the script's src directory to the path
script_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

from utils.translation import translate_text

# Define target languages for translation
TARGET_LANGUAGES = ["ja", "fr"]

# Get environment variables for target repository
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
TARGET_REPO_DIR = os.getenv("GITHUB_REPOSITORY", "").strip()  # Directory for target repo

def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            return file.read()

def save_translated_file(file_path, content, language):
    translated_file = Path(file_path).with_suffix(f'.{language}.md')
    translated_file.write_text(content, encoding='utf-8')
    # Stage the translated file
    subprocess.run(["git", "add", str(translated_file)], cwd=TARGET_REPO_DIR)
    print(f"Staged file: {translated_file}")

def get_changed_files():
    try:
        # Check for changed and staged files
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            cwd=TARGET_REPO_DIR,
            check=True
        )
        staged_files = [f for f in result.stdout.splitlines() if f.strip()]

        # Check for untracked files
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            cwd=TARGET_REPO_DIR,
            check=True
        )
        untracked_files = [f for f in result.stdout.splitlines() if f.strip()]

        # Combine and return both staged and untracked files
        return list(set(staged_files + untracked_files))

    except subprocess.CalledProcessError as e:
        print(f"Error detecting changed files: {str(e)}")
        return []

def is_original_markdown(file_path):
    path = Path(file_path)
    return (path.suffix == '.md' and 
            not any(path.name.endswith(f'.{lang}.md') for lang in TARGET_LANGUAGES))

def sync_translations(original_file, target_languages):
    try:
        content = read_file(original_file)
        original_path = Path(original_file)

        for language in target_languages:
            translated_file = original_path.with_suffix(f'.{language}.md')
            
            needs_translation = True
            if translated_file.exists():
                existing_translation = read_file(translated_file)
                diff = list(unified_diff(
                    existing_translation.splitlines(),
                    content.splitlines(),
                    lineterm=""
                ))
                needs_translation = bool(diff)

            if needs_translation:
                translated_content = translate_text(content, language)
                if translated_content:
                    save_translated_file(original_file, translated_content, language)
                    print(f"Updated translation and staged {translated_file}")
            else:
                print(f"No changes detected for {translated_file}. Skipping.")

    except Exception as e:
        print(f"Error processing {original_file}: {str(e)}")

def main():
    if not TARGET_REPO_DIR or not os.path.exists(TARGET_REPO_DIR):
        print("Error: Target repository directory is not set or doesn't exist.")
        return

    # Pull the latest changes in the target repository
    try:
        subprocess.run(["git", "pull"], cwd=TARGET_REPO_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error pulling latest changes: {str(e)}")
        return

    # Get changed files in the target repository
    changed_files = get_changed_files()
    for file in changed_files:
        file_path = os.path.join(TARGET_REPO_DIR, file)
        if os.path.exists(file_path) and is_original_markdown(file_path):
            sync_translations(file_path, TARGET_LANGUAGES)

    # Commit and push the changes if there are any
    try:
        subprocess.run(["git", "commit", "-m", "Update translations for Markdown files"], cwd=TARGET_REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=TARGET_REPO_DIR, check=True)
        print("Committed and pushed translation updates.")
    except subprocess.CalledProcessError as e:
        print(f"No changes to commit or error committing changes: {str(e)}")

if __name__ == "__main__":
    main()
