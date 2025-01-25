# Bilingual-GitHub 

## Overview
The bilingual-github repository provides reusable GitHub Actions workflows for translating GitHub issues and comments.
This documentation explains how to use the workflows for:
- Translating GitHub Issues
- Translating GitHub Comments

## Steps to Use the Reusable Workflows in a Target Repository

#### 1. Translate GitHub Issues
To use the workflow for translating issues, create the following file in the target repository:
```bash
.github/workflows/translate_issues.yml
```
#### Code for the Calling Workflow (Translate Issues)
```python
name: Translate GitHub Issues

on:
  issues:
    types:
      - opened
      - edited

jobs:
  call-translate-issues:
    uses: rimoapp/bilingual-github/.github/workflows/translate-issues.yml@main
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    with:
      issue_number: ${{ github.event.issue.number }}
```
#### 2. Translate GitHub Comments
To use the workflow for translating comments, create the following file in the target repository:
```base
.github/workflows/translate_comments.yml
```
#### Code for the Calling Workflow (Translate Comments)
```python
name: Translate Issue Comments

on:
  issue_comment:
    types:
      - created
      - edited

jobs:
  call-translate-comments:
    uses: rimoapp/bilingual-github/.github/workflows/translate-comments.yml@main
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    with:
      issue_number: ${{ github.event.issue.number }}
      comment_id: ${{ github.event.comment.id }}
```    
## Steps to Configure the Target Repository

#### 1. Add Secrets
- Navigate to target repository's settings on GitHub.
- Under **Security > Secrets and variables > Actions**, add the following
  secret:
  - **OPENAI_API_KEY:** Your OpenAI API key for translations.

#### 2. Enable the Workflows
Ensure that GitHub Actions are enabled for the repository. The workflows will trigger on the following events:
- **Translate Issues:**
  - When an issue is created or edited.
- **Translate Comments:**
  - When a comment is added or edited.

## Testing the Integration

#### 1. Translate Issues
- Open or edit an issue in the target repository.
- The ```call-translate-issues``` job will trigger and translate the issue.

#### 2. Translate Comments
- Add or edit a comment in an issue in the target repository.
- The ```call-translate-comments``` job will trigger and translate the comment.

#### 3. Monitor the Workflow
- Go to the **Actions** tab in the target repository.
- Check the status of the ```Translate GitHub Issues``` and ```Translate Issue Comments``` workflows.
- If successful, the translated content will appear in the issue or 
  comment.