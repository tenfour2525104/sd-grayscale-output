
import gradio as gr
import numpy as np
import json
import os
from PIL import Image, ImageFilter, ImageEnhance
import modules.scripts as scripts
from modules.processing import Processed

PRESET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "presets.json")


def load_presets():
    if os.path.exists(PRESET_PATH):
        with open(PRESET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_presets(presets):
    with open(PRESET_PATH, "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)


def to_gray_arr(image, denoise):
    img = image.convert("RGB")
    if denoise > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=denoise))
    arr = np.array(img, dtype=np.float32)
    return arr[:,:,0]*0.299 + arr[:,:,1]*0.587 + arr[:,:,2]*0.114


def apply_contrast(gray, contrast):
    if contrast == 1.0:
        return gray
    return np.clip((gray - 128.0) * contrast + 128.0, 0, 255)


def finalize(gray_arr, sharpen, invert):
    g = np.clip(gray_arr, 0, 255)
    if invert:
        g = 255.0 - g
    g = g.astype(np.uint8)
    img = Image.fromarray(np.stack([g, g, g], axis=2), "RGB")
    if sharpen > 0:
        img = ImageEnhance.Sharpness(img).enhance(1.0 + sharpen * 2.0)
    return img


def mode_grayscale(image, contrast, denoise, sharpen, invert):
    g = apply_contrast(to_gray_arr(image, denoise), contrast)
    return finalize(g, sharpen, invert)


def mode_bw(image, contrast, threshold, sharpen, invert):
    g = apply_contrast(to_gray_arr(image, 0), contrast)
    return finalize(np.where(g >= threshold, 255.0, 0.0), sharpen, invert)


def mode_dark_extract(image, threshold, denoise, sharpen, soften, invert):
    g = to_gray_arr(image, denoise)
    if soften > 0:
        g_img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
        g = np.array(g_img.filter(ImageFilter.GaussianBlur(radius=soften)), dtype=np.float32)
    result = np.clip((g - threshold) / max(255.0 - threshold, 1.0) * 255.0, 0, 255)
    return finalize(result, sharpen, invert)


def mode_xdog(image, sigma, k, epsilon, phi, denoise, sharpen, invert):
    g = to_gray_arr(image, denoise) / 255.0
    try:
        import cv2
        g8 = (g * 255).astype(np.uint8)
        g1 = cv2.GaussianBlur(g8, (0, 0), sigma).astype(np.float32) / 255.0
        g2 = cv2.GaussianBlur(g8, (0, 0), sigma * k).astype(np.float32) / 255.0
    except ImportError:
        g_pil = Image.fromarray((g * 255).astype(np.uint8))
        g1 = np.array(g_pil.filter(ImageFilter.GaussianBlur(radius=sigma)), dtype=np.float32) / 255.0
        g2 = np.array(g_pil.filter(ImageFilter.GaussianBlur(radius=sigma * k)), dtype=np.float32) / 255.0
    dog = g1 - g2
    xdog = np.where(dog >= epsilon, 1.0, 1.0 + np.tanh(phi * (dog - epsilon)))
    xdog = np.clip(xdog, 0.0, 1.0)
    result = (1.0 - xdog) * 255.0
    return finalize(result, sharpen, invert)


def convert_image(image, mode, contrast, threshold, sharpen, denoise,
                  dark_soften, xdog_sigma, xdog_k, xdog_epsilon, xdog_phi, invert):
    if mode == "グレースケール":
        return mode_grayscale(image, contrast, denoise, sharpen, invert)
    elif mode == "白黒 (2値)":
        return mode_bw(image, contrast, threshold, sharpen, invert)
    elif mode == "暗部抽出（アニメ塗り向け）":
        return mode_dark_extract(image, threshold, denoise, sharpen, dark_soften, invert)
    elif mode == "XDoG線画（本格）":
        return mode_xdog(image, xdog_sigma, xdog_k, xdog_epsilon, xdog_phi, denoise, sharpen, invert)
    return image


MODES = ["グレースケール", "白黒 (2値)", "暗部抽出（アニメ塗り向け）", "XDoG線画（本格）"]


class GrayscaleOutputScript(scripts.Script):
    def title(self):
        return "Grayscale Output"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("Grayscale Output", open=False):
            enabled = gr.Checkbox(label="有効にする", value=False)

            with gr.Group():
                gr.Markdown("### プリセット")
                with gr.Row():
                    preset_dd = gr.Dropdown(label="プリセット選択",
                                            choices=list(load_presets().keys()),
                                            value=None, scale=3)
                    load_btn = gr.Button("読込", scale=1)
                with gr.Row():
                    preset_name = gr.Textbox(label="保存名", placeholder="名前を入力", scale=3)
                    save_btn = gr.Button("保存", scale=1)
                    del_btn  = gr.Button("削除", scale=1)
                status = gr.Markdown("")

            mode = gr.Radio(label="変換モード", choices=MODES, value="グレースケール")

            with gr.Group():
                gr.Markdown("### 共通設定")
                contrast = gr.Slider(label="コントラスト", minimum=0.5, maximum=3.0, step=0.05, value=1.0)
                denoise  = gr.Slider(label="ノイズ除去",   minimum=0.0, maximum=3.0, step=0.1,  value=0.0)
                sharpen  = gr.Slider(label="シャープネス", minimum=0.0, maximum=3.0, step=0.1,  value=0.0)
                invert   = gr.Checkbox(label="白黒を反転（線=白・背景=黒）", value=False)

            with gr.Group():
                gr.Markdown("### 白黒・暗部抽出 設定")
                threshold   = gr.Slider(label="しきい値", minimum=0, maximum=240, step=1, value=100)
                dark_soften = gr.Slider(label="輪郭ぼかし（暗部抽出専用）", minimum=0.0, maximum=3.0, step=0.1, value=0.5)

            with gr.Group():
                gr.Markdown("### XDoG 設定（本格線画専用）")
                gr.Markdown("*アニメ塗り画像の輪郭線だけを綺麗に抽出します*")
                xdog_sigma   = gr.Slider(label="Sigma（線の細さ）",        minimum=0.3, maximum=3.0,  step=0.1,  value=0.8)
                xdog_k       = gr.Slider(label="K（コントラスト）",        minimum=1.1, maximum=5.0,  step=0.1,  value=1.6)
                xdog_epsilon = gr.Slider(label="Epsilon（線のしきい値）",  minimum=-0.5, maximum=0.5, step=0.01, value=0.01)
                xdog_phi     = gr.Slider(label="Phi（エッジの鋭さ）",     minimum=1,   maximum=200,  step=1,    value=10)

            all_p = [mode, contrast, threshold, sharpen, denoise,
                     dark_soften, xdog_sigma, xdog_k, xdog_epsilon, xdog_phi, invert]

            def do_load(name):
                presets = load_presets()
                if name not in presets:
                    return [gr.update()] * len(all_p) + ["❌ 見つかりません"]
                p = presets[name]
                return [
                    gr.update(value=p.get("mode",         "グレースケール")),
                    gr.update(value=p.get("contrast",     1.0)),
                    gr.update(value=p.get("threshold",    100)),
                    gr.update(value=p.get("sharpen",      0.0)),
                    gr.update(value=p.get("denoise",      0.0)),
                    gr.update(value=p.get("dark_soften",  0.5)),
                    gr.update(value=p.get("xdog_sigma",   0.8)),
                    gr.update(value=p.get("xdog_k",       1.6)),
                    gr.update(value=p.get("xdog_epsilon", 0.01)),
                    gr.update(value=p.get("xdog_phi",     10)),
                    gr.update(value=p.get("invert",       False)),
                    gr.update(value=f"✅ 「{name}」読込"),
                ]

            load_btn.click(fn=do_load, inputs=[preset_dd], outputs=all_p + [status])

            def do_save(name, m, cont, thr, sh, dn, ds, xs, xk, xe, xp, inv):
                if not name.strip():
                    return gr.update(), "❌ 名前を入力してください"
                presets = load_presets()
                presets[name] = dict(mode=m, contrast=cont, threshold=thr,
                                     sharpen=sh, denoise=dn, dark_soften=ds,
                                     xdog_sigma=xs, xdog_k=xk, xdog_epsilon=xe,
                                     xdog_phi=xp, invert=inv)
                save_presets(presets)
                return gr.update(choices=list(presets.keys()), value=name), f"✅ 「{name}」保存"

            save_btn.click(fn=do_save, inputs=[preset_name] + all_p,
                           outputs=[preset_dd, status])

            def do_del(name):
                presets = load_presets()
                if name not in presets:
                    return gr.update(), "❌ 見つかりません"
                del presets[name]
                save_presets(presets)
                rem = list(presets.keys())
                return gr.update(choices=rem, value=rem[0] if rem else None), f"🗑️ 「{name}」削除"

            del_btn.click(fn=do_del, inputs=[preset_dd], outputs=[preset_dd, status])

        return [enabled] + all_p

    def postprocess_image(self, p, pp, enabled, mode, contrast, threshold, sharpen, denoise,
                          dark_soften, xdog_sigma, xdog_k, xdog_epsilon, xdog_phi, invert):
        if not enabled:
            return
        pp.image = convert_image(pp.image, mode, contrast, threshold, sharpen, denoise,
                                 dark_soften, xdog_sigma, xdog_k, xdog_epsilon, xdog_phi, invert)

    def postprocess(self, p, processed: Processed, enabled, mode, contrast, threshold, sharpen, denoise,
                    dark_soften, xdog_sigma, xdog_k, xdog_epsilon, xdog_phi, invert):
        if not enabled:
            return processed
        for i, img in enumerate(processed.images):
            if not isinstance(img, Image.Image):
                continue
            processed.images[i] = convert_image(img, mode, contrast, threshold, sharpen, denoise,
                                                 dark_soften, xdog_sigma, xdog_k, xdog_epsilon,
                                                 xdog_phi, invert)
        return processed
