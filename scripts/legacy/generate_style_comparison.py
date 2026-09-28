#!/usr/bin/env python3
"""
Generate the SAME 2 sample stickers in ALL 4 styles for visual comparison.

Use this BEFORE running generate_stickers.py to decide which style you like best.

USAGE:
    python generate_style_comparison.py

OUTPUT:
    סטיקרים לווצאפ/השוואת סגנונות/
        ├── 01_A_וואטרקולור.png
        ├── 01_B_עכשווי.png
        ├── 01_C_3D.png
        ├── 01_D_קווים_ונקודות.png
        ├── 13_A_וואטרקולור.png
        ├── 13_B_עכשווי.png
        ├── 13_C_3D.png
        ├── 13_D_קווים_ונקודות.png
        └── 00_השוואה.png   (all 8 in a comparison grid)

After viewing the results, edit generate_stickers.py and set:
    SELECTED_STYLE = "X"   # X = your chosen style (A/B/C/D)
"""
import os
import sys
import json
import time
import base64
import shutil
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = str(__import__("pathlib").Path(__file__).resolve().parents[2])
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "assets", "reference", "style-studies")

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "gemini-3-pro-image-preview"
MODEL_FALLBACK = "gemini-3.1-flash-image-preview"
API_KEYS = [key.strip() for key in os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", "")).split(",") if key.strip()]

ASPECT_RATIO = "1:1"
IMAGE_SIZE = "1K"

# Two contrasting sample stickers - one with action, one with emotion
SAMPLE_STICKERS = [
    ("01", "אני רוצה לבד!", "A toddler aged 2-3 with curly dark brown hair, sitting cross-legged on the floor, determinedly trying to put on their own small shoe. Tongue sticking out slightly in pure concentration. Eyes focused down on the shoe. One hand grips the shoe firmly. The pose communicates fierce independence and pride. Empty white background, square 1:1 framing."),
    ("13", "אני כועס",       "A toddler aged 2-3 with curly dark brown hair, arms crossed firmly across chest, eyebrows scrunched down, cheeks puffed out, mouth in a tight pout, slight steam puff icon by their ear. Communicates valid anger - intense but not scary. Empty white background, square 1:1 framing."),
]

STYLES = {
    "A": ("וואטרקולור", """STYLE: Premium hand-painted watercolor children's book illustration, in the style of high-end European children's brands like Babai, Lalo, or Blabla Kids. Visible watercolor brush strokes, gentle color bleeds at edges, subtle paper texture. Outlined with fine ink/pen lines that are slightly imperfect and hand-drawn. The character has soft warm features - rosy cheeks, expressive eyes, joyful presence.

COLOR PALETTE: STRICTLY limited to four brand colors plus skin/hair: cherry red (#E53935), warm sunshine yellow (#FDD835), fresh leaf green (#43A047), and bright sky blue (#1E88E5). Skin tone warm peach (#FFE0B2). Hair dark brown. Rosy pink cheeks (#FFB6C1). Background: pure clean white (#FFFFFF) - no patterns, no scenery.

COMPOSITION: Single subject perfectly centered in 1:1 frame with generous breathing room - subject occupies center 60% of canvas. Soft, joyful, picture-book quality. Premium and brandable.

NEGATIVE: NO TEXT, NO WORDS, NO LETTERS, NO HEBREW, NO TYPOGRAPHY, no busy backgrounds, no photorealism, no dark colors, no scary expressions, no harsh shadows.

SCENE: """),
    "B": ("עכשווי", """STYLE: Contemporary modern children's illustration with a Scandinavian indie children's brand aesthetic - think Sago Mini meets a premium picture book. Soft flat colors with subtle hand-drawn texture overlay. Light and airy, friendly stylized characters with simple but expressive features. Slightly geometric simplification of forms.

COLOR PALETTE: Brand palette of cherry red (#E53935), warm yellow (#FDD835), fresh green (#43A047), bright blue (#1E88E5), warm peach skin (#FFE0B2), soft cream backgrounds (#FFF8E7). Modern, harmonious. Background: pure white (#FFFFFF).

COMPOSITION: Single character centered at 1:1, occupying 60% of canvas with breathing room. Modern, polished, brandable. Joyful expression. The character feels alive and relatable to a 2-5 year old child.

NEGATIVE: NO TEXT, NO WORDS, NO LETTERS, NO HEBREW, NO TYPOGRAPHY, no realistic textures, no photorealism, no busy backgrounds, no harsh outlines, no dark moods.

SCENE: """),
    "C": ("3D", """STYLE: Premium soft 3D rendered character in the style of contemporary children's apps and brands like Lingokids, Khan Academy Kids, or Playdate. Soft subsurface scattering on skin, gentle rim lighting, smooth rounded forms with no sharp edges. Pixar-like quality but simpler and more iconic. Toy-like proportions with oversized head.

COLOR PALETTE: Cherry red (#E53935), warm yellow (#FDD835), fresh green (#43A047), bright blue (#1E88E5) used as primary clothing/prop colors. Warm skin tone, soft hair colors. Background: pure clean white (#FFFFFF) - no scene, no shadow.

COMPOSITION: Character centered at 1:1, three-quarter view or front view. Subject occupies 60% of frame. Soft studio-lit, no harsh shadows. Premium polished render.

NEGATIVE: NO TEXT, NO WORDS, NO LETTERS, NO HEBREW, no busy backgrounds, no photorealistic skin, no scary uncanny valley, no harsh lighting.

SCENE: """),
    "D": ("קווים_ונקודות", """STYLE: Bold modern vector illustration in a "lines and dots" graphic language directly inspired by the Kido brand logo. The character is constructed from THICK ROUNDED TUBE outlines (like rounded soft pipes) where many line endings terminate in small filled circles/dots - this is the signature brand element. Clean solid color fills inside the tube outlines. Slight hand-drawn imperfection but still crisp vector quality.

COLOR PALETTE: STRICT four-color palette - cherry red (#E53935), warm yellow (#FDD835), fresh green (#43A047), bright blue (#1E88E5). Each major shape gets one solid brand color. Outlines in dark charcoal (#2B2B2B). Background: pure white (#FFFFFF).

COMPOSITION: Character centered at 1:1, simplified iconic forms, subject occupies 60% of canvas. Bold, brandable, immediately recognizable as Kido. Joyful and playful.

NEGATIVE: NO TEXT, NO WORDS, NO LETTERS, NO HEBREW, no gradients, no shadows, no realistic detail, no muted colors, no busy backgrounds.

SCENE: """),
}


def generate_image_api(prompt, api_key, model):
    url = f"{API_BASE}/models/{model}:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": ASPECT_RATIO, "imageSize": IMAGE_SIZE},
        },
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    for p in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in p and p["inlineData"].get("data"):
            return base64.b64decode(p["inlineData"]["data"])
    return None


def generate_with_retry(prompt, max_attempts=4):
    models = [MODEL, MODEL_FALLBACK]
    for attempt in range(max_attempts):
        key = API_KEYS[attempt % len(API_KEYS)]
        model = models[min(attempt // 2, len(models)-1)]
        try:
            print(f"      attempt {attempt+1} ({model})...")
            img = generate_image_api(prompt, key, model)
            if img:
                return img
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")[:150]
            print(f"      HTTP {e.code}: {err}")
            time.sleep(3)
        except Exception as e:
            print(f"      Error: {str(e)[:150]}")
            time.sleep(2)
    return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw_dir = os.path.join(SCRIPT_DIR, "assets", "source", "collections", "גלם", "A")

    for sid, hebrew, scene in SAMPLE_STICKERS:
        print(f"\n=== Sticker {sid}: {hebrew} ===")
        for style_key, (style_name, style_prompt) in STYLES.items():
            out_name = f"{sid}_{style_key}_{style_name}.png"
            out_path = os.path.join(OUTPUT_DIR, out_name)

            # If style A and we already have the file in raw/, just copy it (saves API calls)
            if style_key == "A":
                src = os.path.join(raw_dir, f"{sid}.png")
                if os.path.exists(src):
                    shutil.copy(src, out_path)
                    print(f"   [{style_key}] {style_name} - copied from existing")
                    continue

            if os.path.exists(out_path):
                print(f"   [{style_key}] {style_name} - exists, skip")
                continue

            print(f"   [{style_key}] {style_name}")
            img = generate_with_retry(style_prompt + scene)
            if img:
                with open(out_path, "wb") as f:
                    f.write(img)
                print(f"      saved")
            else:
                print(f"      FAILED")
            time.sleep(2)

    # Build comparison grid
    print("\n=== Building comparison grid ===")
    try:
        from PIL import Image, ImageDraw, ImageFont
        TILE = 380
        PAD = 20
        LABEL_H = 35
        # 4 columns (styles) x 2 rows (stickers)
        cols, rows = 4, 2
        W = PAD + cols*(TILE + PAD)
        H = 90 + rows*(TILE + LABEL_H + PAD) + PAD

        comp = Image.new("RGB", (W, H), "#FAF6EC")
        cd = ImageDraw.Draw(comp)
        try:
            head_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except Exception:
            head_font = ImageFont.load_default()
            label_font = ImageFont.load_default()

        # Header
        title = "השוואת סגנונות - קידו סטיקרים"
        tb = cd.textbbox((0,0), title, font=head_font)
        cd.text(((W-(tb[2]-tb[0]))//2 - tb[0], 25), title, fill="#2B2B2B", font=head_font)

        # Column labels
        col_labels = ["A: וואטרקולור", "B: עכשווי", "C: 3D רך", "D: קווים+נקודות"]
        for i, lbl in enumerate(col_labels):
            x = PAD + i*(TILE + PAD) + TILE//2
            lb = cd.textbbox((0,0), lbl, font=label_font)
            cd.text((x - (lb[2]-lb[0])//2 - lb[0], 75), lbl, fill="#444", font=label_font)

        for row_i, (sid, hebrew, _) in enumerate(SAMPLE_STICKERS):
            for col_i, (style_key, (style_name, _)) in enumerate(STYLES.items()):
                p = os.path.join(OUTPUT_DIR, f"{sid}_{style_key}_{style_name}.png")
                if not os.path.exists(p):
                    continue
                img = Image.open(p).convert("RGB").resize((TILE, TILE), Image.LANCZOS)
                x = PAD + col_i*(TILE + PAD)
                y = 105 + row_i*(TILE + LABEL_H + PAD)
                comp.paste(img, (x, y))
                cd.rectangle([x-1, y-1, x+TILE, y+TILE], outline="#888", width=1)
                # Sticker label below
                slabel = f"#{sid} {hebrew}"
                lb = cd.textbbox((0,0), slabel, font=label_font)
                cd.text((x + TILE//2 - (lb[2]-lb[0])//2 - lb[0], y + TILE + 8), slabel, fill="#2B2B2B", font=label_font)

        comp_path = os.path.join(OUTPUT_DIR, "00_השוואה.png")
        comp.save(comp_path)
        print(f"Saved: {comp_path}")
    except Exception as e:
        print(f"Could not build comparison grid: {e}")
        print("(Install Pillow if missing: pip install Pillow)")

    print("\n" + "="*60)
    print("Done. Open the folder 'השוואת סגנונות' to compare styles.")
    print("Then edit generate_stickers.py:")
    print('   SELECTED_STYLE = "X"   # X = A, B, C, or D')


if __name__ == "__main__":
    main()
