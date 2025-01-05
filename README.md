# Bilingual-GitHub |
Bilingual-GitHub is a Python-based tool designed to automatically translate GitHub issues into multiple languages. This tool integrates with GitHub’s API and leverages translation models to add translated content to issues.

## Features
- Automatic Translation: Translates the body of open GitHub issues and markdown files into multiple languages.
- Support for Multiple Languages: Currently supports Japanese and French, but can be easily extended to support additional languages.

## Installation
1. Clone the repository:
```
git clone <repository-url>
cd bilingual-github
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Initialize the tool in your repository:
```
python src/hooks/install_hooks.py
```

## Usage
### Git Hooks for Markdown Files
1. Ensure git hooks are installed by running:
```
python src/hooks/install_hooks.py
```
2. After committing changes to a Markdown file (*.md), the post-commit hook automatically translates it into the target languages.
3. Check the translated files (*.language_code.md) in your repository.

### GitHub Issues Translation
```
python src/actions/translate_issues.py
```
