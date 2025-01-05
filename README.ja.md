バイリンガル - GitHub

バイリンガル - GitHub は、GitHub の問題を自動的に複数の言語に翻訳するために設計された Python ベースのツールです。このツールは GitHub の API と統合され、翻訳モデルを活用して、翻訳されたコンテンツを問題に追加します。

## 機能

- 自動翻訳: オープンな GitHub の問題の本文とマークダウンファイルを複数の言語に翻訳します。
- 複数言語のサポート: 現在は日本語とフランス語をサポートしていますが、追加の言語のサポートに簡単に拡張できます。

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

3. リポジトリでツールを初期化します:

```
python src/hooks/install_hooks.py
```

## 使用方法
### Git Hooks for Markdown Files

1. git hooks がインストールされていることを確認するために、次のコマンドを実行します:

```
python src/hooks/install_hooks.py
```

2. Markdown ファイル (* .md) に変更をコミットした後、post-commit hook がそれを自動的にターゲット言語に翻訳します。

3. リポジトリ内の翻訳されたファイル (* .language_code.md) をチェックします。

### GitHub Issues Translation

```
python src/actions/translate_issues.py
```

# こんにちは、お元気ですか？