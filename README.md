[README.md](https://github.com/user-attachments/files/29457778/README.md)
# sd-grayscale-output

Stable Diffusion WebUI (AUTOMATIC1111 / Forge) の拡張機能です。
生成した画像をグレースケール・白黒・マンガ調に変換します。
プロンプトで髪の色などを指定していても、出力だけ白黒にできます。

---

## 対応環境

- AUTOMATIC1111 stable-diffusion-webui
- Stable Diffusion WebUI Forge / Forge Neo (EasyForgeNeo など)

---

## インストール

### 方法1：Install from URL（推奨）

1. WebUI の **Extensions** タブ → **Install from URL**
2. 以下のURLを貼り付けて **Install** をクリック

```
https://github.com/tenfour2525104/sd-grayscale-output.git
```

3. **Installed** タブ → **Apply and restart UI**

### 方法2：手動インストール

1. このリポジトリをZIPでダウンロードして解凍
2. `sd-grayscale-output` フォルダを以下に配置

```
stable-diffusion-webui/extensions/sd-grayscale-output/
```

3. WebUIを再起動

---

## 使い方

1. txt2img または img2img の下にある **Grayscale Output** アコーディオンを開く
2. **「有効にする」** にチェックを入れる
3. 変換モードを選んで生成するだけ

---

## 変換モード

| モード | 説明 |
|---|---|
| **グレースケール** | 濃淡のある自然な白黒 |
| **白黒 (2値)** | しきい値で完全に黒か白かに分ける |
| **暗部抽出（アニメ塗り向け）** | 暗いピクセルだけ線として残す。アニメ画像に最適 |
| **XDoG線画（本格）** | ガウス差分によるエッジ抽出。仕上がり重視向け |

---

## プリセット機能

よく使う設定を名前をつけて保存・呼び出しができます。
デフォルトプリセットはなし。自分で保存したものだけが残ります。
保存先：`extensions/sd-grayscale-output/presets.json`

---

## ライセンス

MIT License
