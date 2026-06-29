sd-grayscale-output
Stable Diffusion WebUI (AUTOMATIC1111 / Forge) の拡張機能です。
生成した画像をグレースケール・白黒・マンガ調に変換します。
プロンプトで髪の色などを指定していても、出力だけ白黒にできます。

対応環境
AUTOMATIC1111 stable-diffusion-webui

Stable Diffusion WebUI Forge / Forge Neo (EasyForgeNeo など)

インストール
方法1：Install from URL（推奨）
WebUI の Extensions タブ → Install from URL

以下のURLを貼り付けて Install をクリック


text
https://github.com/tenfour2525104/sd-grayscale-output.git
Installed タブ → Apply and restart UI

方法2：手動インストール
このリポジトリをZIPでダウンロードして解凍

sd-grayscale-output フォルダを以下に配置


text
stable-diffusion-webui/extensions/sd-grayscale-output/
WebUIを再起動

使い方
txt2img または img2img の下にある Grayscale Output アコーディオンを開く

「有効にする」 にチェックを入れる

変換モードを選んで生成するだけ

変換モード
モード	説明
グレースケール	濃淡のある自然な白黒
白黒 (2値)	しきい値で完全に黒か白かに分ける
少年マンガ調	太い線・荒めのトーン・強いコントラスト
少女マンガ調	繊細な線・2角度重ねトーン・ふわっとした仕上がり
青年マンガ調	細かい網点・リアルな線画・写実的な仕上がり
ホラー調	超高コントラスト・極太線・トーンなし
設定パラメータ
共通設定
パラメータ	説明
グレースケール変換方式	Luminosity（推奨）/ Average / Desaturate
コントラスト	明暗の差を強調する（0.5〜3.0）
白黒しきい値	白黒・マンガ調で黒白の境目を調整
マンガ調設定
パラメータ	説明
ノイズ除去	変換前のガウスぼかし（0.1刻み）
シャープネス	最終出力の輪郭強調
Cannyエッジ 下限/上限	線画の検出感度（OpenCV使用）
線の太さ	エッジの太さ（0.1刻み）
線の濃さ	エッジの黒さ
スクリーントーン	中間グレーを網点に変換（ON/OFF）
ドットサイズ	網点の大きさ
ドット角度	網点の傾き
プリセット機能
よく使う設定を名前をつけて保存・呼び出しができます。

デフォルトプリセット：少年マンガ / 少女マンガ / 青年マンガ / ホラー（削除不可）

ユーザープリセット：自由に保存・削除可能

保存先：extensions/sd-grayscale-output/presets.json（WebUI再起動後も保持）

必要なライブラリ
以下は install.py で自動インストールされます。

numpy

opencv-python（Cannyエッジ検出に使用。未インストールの場合はPILでフォールバック）

ライセンス
MIT License
