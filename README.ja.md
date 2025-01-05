# バイリンガル-GitHub |
バイリンガル-GitHubは、GitHubのイシューを自動的に複数の言語に翻訳するために設計されたPythonベースのツールです。このツールはGitHubのAPIと統合され、翻訳モデルを活用してイシューに翻訳されたコンテンツを追加します。

## 機能
- 自動翻訳: オープンなGitHubのイシューやマークダウンファイルの本文を複数の言語に翻訳します。
- 複数言語のサポート: 現在は日本語とフランス語をサポートしていますが、他の言語も簡単に追加できます。

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

## 使用方法
### マークダウンファイルのためのGitフック
1. Gitフックがインストールされていることを確認するために、次のコマンドを実行します:
```
python src/hooks/install_hooks.py
```
2. マークダウンファイル（*.md）への変更をコミットした後、ポストコミットフックがターゲット言語に自動的に翻訳します。
3. リポジトリ内の翻訳されたファイル（*.language_code.md）を確認します。

### GitHubイシューの翻訳
```
python src/actions/translate_issues.py
```