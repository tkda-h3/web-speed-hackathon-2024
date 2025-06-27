# ローカル環境セットアップガイド

## Node.jsバージョン要件

このプロジェクトはNode.js v20.11.1で動作するように設計されています。
Node.js v22以降では`better-sqlite3`のビルドエラーが発生します。

## セットアップ方法

### 1. Voltaを使用している場合

プロジェクトの`volta`設定が自動的に適用されるはずですが、適用されない場合：

```bash
volta install node@20.11.1
volta pin node@20.11.1
```

### 2. nvmを使用している場合

```bash
nvm install 20.11.1
nvm use 20.11.1
```

### 3. nodebrewを使用している場合

```bash
nodebrew install v20.11.1
nodebrew use v20.11.1
```

## Docker環境での実行（推奨）

ローカルのNode.jsバージョン問題を回避するには、Dockerを使用することを推奨します：

```bash
docker compose up
```

## トラブルシューティング

### better-sqlite3のビルドエラー

Node.js v22を使用している場合は、以下のエラーが発生します：

```
Error: The module '...better-sqlite3.node' was compiled against a different Node.js version
```

解決方法：
1. Node.js v20.11.1に切り替える
2. `rm -rf node_modules pnpm-lock.yaml && pnpm install`を実行

### pnpm startでvoltaエラー

Docker環境では`volta`コマンドが存在しないため、package.jsonからvolta依存を削除しています。