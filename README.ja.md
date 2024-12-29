# バイリンガル-GitHub

バイリンガル-GitHub は、GitHub の問題を自動的に複数の言語に翻訳するために設計された Python ベースのツールです。このツールは GitHub の API と統合され、翻訳モデルを活用して、問題に翻訳されたコンテンツを追加します。

## 特徴

- 自動翻訳: オープンな GitHub の問題とマークダウンファイルの本文を複数の言語に翻訳します。

- 複数言語のサポート: 現在は日本語とフランス語をサポートしていますが、簡単に追加の言語をサポートするように拡張できます。

## インストール

1. リポジトリをクローンします:

```
git clone <リポジトリ-URL>
cd bilingual-github
```

2. 依存関係をインストールします:

```
pip install -r requirements.txt
```

3. あなたのリポジトリにツールを初期化します:

```
python src/hooks/install_hooks.py
```

## 使用法

### Git Hooks for Markdown Files

1. 実行して git hooks がインストールされていることを確認します:

```
python src/hooks/install_hooks.py
```

2. Markdown ファイル (* .md) に変更をコミットした後、post-commit hook が自動的にターゲット言語に翻訳します。

3. あなたのリポジトリ内で翻訳されたファイル (* .言語_コード.md) を確認します。

### GitHub Issues Translation

```
python src/actions/translate_issues.py
```

# こんにちは、元気ですか？あなたが元気であることを願っています。