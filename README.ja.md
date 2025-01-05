# バイリンガル-GitHub
バイリンガル-GitHubは、GitHubのイシューを自動的に複数の言語に翻訳するために設計されたPythonベースのツールです。このツールは、GitHubのAPIと統合され、翻訳モデルを利用してイシューに翻訳されたコンテンツを追加します。

## 機能
- 自動翻訳: オープンなGitHubイシューやMarkdownファイルの本文を複数の言語に翻訳します。
- 複数言語のサポート: 現在は日本語とフランス語をサポートしていますが、追加の言語をサポートするために簡単に拡張できます。

## インストール
1. リポジトリをクローンします:
```
git clone <repository-url>
cd bilingual-github
```
2. 依存関係をインストールします:
```
pip install -r requirements.txt
```
3. リポジトリにツールを初期化します:
```
python src/hooks/install_hooks.py
```

## 使い方
### Markdownファイル用のGitフック
1. 次のコマンドを実行してGitフックがインストールされていることを確認します:
```
python src/hooks/install_hooks.py
```
2. Markdownファイル (*.md) に変更をコミットした後、post-commitフックが自動的にターゲット言語に翻訳します。
3. リポジトリ内の翻訳されたファイル (*.language_code.md) を確認します。

### GitHubイシューの翻訳
```
python src/actions/translate_issues.py
```