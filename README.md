# SD Forge Queue Manager

![Screenshot](assets/screenshot.png)

Stable Diffusion Forge の API をリモート操作し、キュー管理と自動生成を行う軽量デスクトップクライアントです。

## 主な機能 (Features)

- **複数プロンプトの連続生成（キューシステム）**: 多数のジョブを溜めて順次処理。
- **シチュエーションとキャラクターの分割プリセット機能**: 組み合わせを自由に変更可能。
- **非同期処理による高レスポンス**: 生成中も UI がフリーズせず操作可能。
- **最新拡張機能への対応**: FreeU Integrated, ADetailer の API 操作に対応。

## システム要件 (Requirements)

### サーバー側 (Server)
- **Stable Diffusion Forge**
- 起動引数に `--api --listen` が必須です。

### クライアント側 (Client)
- **Python 3.x**
- ネットワーク経由で Forge サーバーにアクセスできる環境。

## インストールと起動方法 (Installation & Usage)

1. リポジトリをクローンまたはダウンロードします。
2. 必要なライブラリをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
3. 設定ファイルを準備します。
   `config.example.json` を `config.json` に、`presets.example.json` を `presets.json` にリネームまたはコピーして使用してください。
4. アプリを起動します。
   ```bash
   python main.py
   ```

### 初期設定
初回起動時に、画面上の歯車アイコン（設定ボタン）から以下の項目を設定してください。
- **API URL**: Forge サーバーの URL (例: `http://192.168.1.100:7860`)
- **Save Directory**: 生成された画像の保存先ローカルパス

## ライセンス (License)
MIT License
