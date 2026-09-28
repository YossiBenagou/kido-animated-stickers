#!/usr/bin/env python3
"""
Generate product stickers - the same Kido toddler character USING each product
from the מוצרים folder. The product is rendered as ILLUSTRATED (watercolor),
not as a photo, matching the rest of the sticker pack's style.

USAGE:
    python generate_product_stickers.py        # generates all 7 product stickers
    python generate_product_stickers.py 60     # generates just sticker #60

OUTPUT:
    Files saved to:    סטיקרים לווצאפ/חבילה סופית/גלם_מאוחד/A_מוצרים/60.png ... 66.png

INPUTS PER STICKER:
    Image 1: 01.png (character reference from main pack)
    Image 2: the product photo (so model knows what the product looks like)
    Prompt: instructions to render product as illustrated, with the child using it
"""
import os
import sys
import json
import time
import base64
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIG
# ============================================================
SELECTED_STYLE = "A"

SCRIPT_DIR = str(__import__("pathlib").Path(__file__).resolve().parents[2])
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "assets", "source", "collections", "גלם_מאוחד", "A_מוצרים")
PRODUCTS_DIR = os.path.join(SCRIPT_DIR, "assets", "reference", "products")

# Path to character reference (01.png from the main unified pack)
CHARACTER_REF = os.path.join(SCRIPT_DIR, "assets", "source", "collections", "גלם_מאוחד", SELECTED_STYLE, "01.png")
# Fallback to the original folder if 01 doesn't exist in גלם_מאוחד yet
CHARACTER_REF_FALLBACK = os.path.join(SCRIPT_DIR, "assets", "source", "collections", "גלם", SELECTED_STYLE, "01.png")

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL_PRO = "gemini-3-pro-image-preview"
MODEL_FLASH = "gemini-3.1-flash-image-preview"
USE_MODEL = MODEL_FLASH   # Nano Banana 2

API_KEYS = [key.strip() for key in os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", "")).split(",") if key.strip()]

ASPECT_RATIO = "1:1"
IMAGE_SIZE = "1K"

# ============================================================
# PROMPT TEMPLATE
# ============================================================
PROMPT_TEMPLATE = """⚠️ READ THIS FIRST — TWO REFERENCE IMAGES ARE ATTACHED ⚠️

  • IMAGE 1 (first attached) = a previously generated Kido sticker showing the TODDLER CHARACTER.
    → Use IMAGE 1 to match the CHARACTER (face, hair, proportions, skin tone, illustration style, color palette, line quality).
    → The toddler in this new sticker MUST look IDENTICAL to the toddler in IMAGE 1.

  • IMAGE 2 (second attached) = a PHOTO of a real Montessori product the child will use.
    → Use IMAGE 2 ONLY to understand the product's SHAPE, STRUCTURE, and COLORS.
    → DO NOT reproduce the photo style — instead RENDER the product as a HAND-PAINTED WATERCOLOR ILLUSTRATION matching IMAGE 1's artistic style (same painted children's-book quality as the rest of the Kido sticker pack).
    → Keep the product's recognizable structural features (proportions, key colors, distinctive parts) but render with watercolor brush strokes, hand-drawn ink lines, and gentle color bleeds — like an illustration in a premium picture book.

TASK: Design a single premium WhatsApp sticker for the Kido brand showing the toddler character interacting/playing with the illustrated product.

═══════════════════════════════════════════════
LAYOUT (CRITICAL - follow exactly):
═══════════════════════════════════════════════
• Square 1:1 composition.
• BACKGROUND: CLASSIC TRANSPARENCY-CHECKERBOARD PATTERN. The entire background of the canvas is filled with the standard digital "transparent background" indicator — a regular grid of small alternating squares of WHITE (#FFFFFF) and LIGHT GRAY (#CCCCCC). Each square is roughly 32x32 pixels. The pattern repeats edge-to-edge across the entire canvas as a perfect uniform grid. NO other texture, NO gradient, NO noise.
• THE CHARACTER + PRODUCT scene must be wrapped in a THICK WHITE STICKER OUTLINE — a smooth white border roughly 8-12 pixels thick that hugs the silhouette of the combined scene, exactly like a printed die-cut sticker peel-off.
• THE HEBREW TEXT sits inside a WHITE PILL-SHAPED SPEECH BUBBLE at the TOP of the sticker. The bubble has the SAME thick white sticker outline. Centered horizontally near the top.
• LAYOUT POSITIONS — BUBBLE AND SCENE FORM ONE CONNECTED STICKER:
   - TOP ~25% of canvas: White pill bubble containing Hebrew text
   - BOTTOM ~70% of canvas: The toddler USING the illustrated product, centered horizontally
   - The bottom edge of the bubble's white outline TOUCHES/CONNECTS with the top of the scene's white outline — they MERGE into ONE continuous unified sticker silhouette.
   - Together, the bubble + scene read as a SINGLE stamped sticker shape with one continuous white border around the whole thing.
   - One unified soft drop shadow falls behind the entire combined sticker shape on the checkerboard background.

═══════════════════════════════════════════════
HEBREW TEXT (must appear in the image - EXACT FONT SPECIFICATION):
═══════════════════════════════════════════════
• Render this exact Hebrew text at the top of the image: "{hebrew_text}"
• Spelling MUST be EXACTLY: {hebrew_text}  (read right-to-left as Hebrew)

• FONT — must match all other Kido stickers:
   - SUPER-ROUNDED, CHUBBY, PILLOW-SOFT hand-lettered Hebrew display font
   - All stroke endings smoothly rounded (perfect circles)
   - BOLD-CHUBBY uniform stroke weight (~16-18% of letter height)
   - Closest reference: chubby-rounded version of Rubik Bold or Heebo Black
   - Slight hand-lettered warmth, organic charm
   - Generous letter spacing
   - Punctuation matches the same fat-rounded style

• TEXT COLOR: SOLID DARK CHARCOAL #2B2B2B
• TEXT SIZE: bubble occupies roughly 55-70% of canvas width
• PILL BUBBLE: white fill with thick white sticker outline, very rounded capsule shape

═══════════════════════════════════════════════
CHARACTER (the same toddler from IMAGE 1):
═══════════════════════════════════════════════
The toddler is the EXACT same character as in IMAGE 1:
  • Age: 2-3 years old
  • Curly dark brown hair, voluminous and slightly tousled
  • Round chubby face, rosy pink cheeks
  • Large dark brown eyes with white catchlights
  • Tiny button nose, expressive small mouth
  • Warm peach skin tone
  • Wears a Montessori-style apron with the Hebrew word "קידו" (4 letters: ק-י-ד-ו) printed/embroidered on the chest pocket area in a small label
  • Apron color may vary per scene to fit naturally

═══════════════════════════════════════════════
PRODUCT (from IMAGE 2 - render as watercolor illustration):
═══════════════════════════════════════════════
{product_block}

═══════════════════════════════════════════════
SCENE (the action - child using the product):
═══════════════════════════════════════════════
{scene}

═══════════════════════════════════════════════
VISUAL STYLE:
═══════════════════════════════════════════════
Premium hand-painted watercolor children's book illustration, in the style of high-end European children's brands like Babai, Lalo, or Blabla Kids. Visible watercolor brush strokes ON THE CHARACTER AND THE PRODUCT (background stays the checkerboard pattern). Gentle color bleeds at edges. Outlined with fine ink/pen lines that are slightly imperfect and hand-drawn. Soft warm features.

COLOR PALETTE: Brand colors of cherry red (#E53935), warm yellow (#FDD835), fresh green (#43A047), bright sky blue (#1E88E5), warm peach skin (#FFE0B2), dark brown hair, rosy pink cheeks. The product's specific colors (from IMAGE 2) should be preserved but rendered in watercolor.

═══════════════════════════════════════════════
NEGATIVE (avoid all of these):
═══════════════════════════════════════════════
• NO photorealistic rendering of the product — it MUST be illustrated/painted, NOT a photo or photo-realistic.
• NO solid color background — must be checkerboard transparency pattern.
• NO missing white outline.
• NO text floating without the bubble.
• NO English text, NO random letters, NO typos in Hebrew, NO scrambled characters.
• NO additional text other than "{hebrew_text}".
"""


# ============================================================
# 7 PRODUCT STICKERS - one per product
# ============================================================
PRODUCT_STICKERS = [
    {
        "id": "60",
        "hebrew_text": "סע! סע!",
        "product_file": "בימבה.jpg",
        "product_block": "The product is a wooden BABY BALANCE PUSH-BIKE (בימבה) with 4 round wooden wheels, a turquoise/mint colored seat and back, natural wood handlebars and frame. Render it as an ILLUSTRATED watercolor version with the same proportions and turquoise + natural-wood color scheme, but painted (not photographic).",
        "scene": "The toddler SITS on the wooden balance bike, both tiny hands gripping the turquoise handlebar, both feet on the floor pushing forward, body leaning slightly forward in fast riding mode, mouth open in excited shouting laugh, eyes squinted with thrill, hair flying back from speed. Maybe small motion lines or speed-zoom marks behind. Pure 'WEEEE I'm RIDING!' joy energy.",
    },
    {
        "id": "61",
        "hebrew_text": "קטן עלי!",
        "product_file": "מסלול איזון.jpg",
        "product_block": "The product is a wooden BALANCE TRACK (מסלול איזון) — wooden balance beam pieces. Render as ILLUSTRATED watercolor with natural wood tones and any pastel accents from the photo, painted not photographic.",
        "scene": "The toddler walks carefully along the wooden balance track, arms spread wide for balance like a tightrope walker, one foot lifted mid-step, tongue sticking out slightly in concentration, focused eyes looking down at the next step, body slightly wobbling. Pure focused balance challenge.",
    },
    {
        "id": "62",
        "hebrew_text": "אני בפסגה!",
        "product_file": "משולש פיקלר.jpg",
        "product_block": "The product is a Pikler triangle climbing structure (משולש פיקלר) made of natural light wood with pastel-colored rungs (yellow, mint green, pink) and a wooden ramp/slide attached. Render as ILLUSTRATED watercolor — natural wood tones with the pastel rungs, painted not photographic.",
        "scene": "The toddler triumphantly stands at the very TOP of the Pikler triangle, both small arms raised high in V-for-victory, beaming the biggest proudest grin like a mountain climber who just summited Everest, eyes sparkling with achievement, slightly leaning forward. Pure 'I CONQUERED IT!' triumph.",
    },
    {
        "id": "63",
        "hebrew_text": "תיראו מי בא!",
        "product_file": "סוס נדנדה.jpg",
        "product_block": "The product is a wooden ROCKING HORSE (סוס נדנדה) with a coral red horse-shaped body, natural wood seat with a small backrest, natural wood rocker base. Render as ILLUSTRATED watercolor — coral red horse shape + natural wood, painted not photographic.",
        "scene": "The toddler RIDES the rocking horse with pure cowboy glee, one hand holding the wooden post tightly, the other raised up in the air like swinging a lasso, mouth wide open in a joyful 'YEEHAW' shout, eyes bright with adventure, body leaning back slightly with the rocking motion, hair flying. Small motion arcs around the horse showing the rocking. Pure 'GIDDY UP!' cowboy joy.",
    },
    {
        "id": "64",
        "hebrew_text": "קטן עליך!",
        "product_file": "קשת טיפוס.jpeg",
        "product_block": "The product is a WOODEN CLIMBING ARCH (קשת טיפוס) — an arched/curved wooden frame with rungs in pastel colors (pink, mint green, yellow). Render as ILLUSTRATED watercolor — natural wood arch with pastel rungs, painted not photographic.",
        "scene": "The toddler climbs up and over the wooden arch, one foot on a lower rung and one hand reaching for an upper rung, body in mid-climb action, focused determined expression, tongue sticking out slightly in concentration, looking at the next handhold, fierce 'I CAN DO THIS' energy. Pure little-mountaineer determination.",
    },
    {
        "id": "65",
        "hebrew_text": "אני עסוק!",
        "product_file": "שולחן סנסורי.jpg",
        "product_block": "The product is a WOODEN SENSORY TABLE (שולחן סנסורי) — a small wooden table with TWO SEPARATE stainless-steel BOWLS/BINS inset into the wooden top (the bowls are TWO DISTINCT INDIVIDUAL ROUND/RECTANGULAR STAINLESS STEEL CONTAINERS sitting in cutout holes in the wood — they are NOT joined or merged into one big basin, they are clearly two separate stainless bowls). The table also has a paper roll attached on one side and mint/turquoise accent feet caps. Render as ILLUSTRATED watercolor — natural wood, the two distinct silvery stainless bowls clearly visible as separate items, mint accents — painted not photographic.",
        "scene": "The toddler stands at the sensory table FULLY ENGAGED — both hands plunged into the sensory tray (with rice, beans, water beads or sand visible cartoon-style), eyes wide with wonder, mouth in a delighted 'O' of discovery, completely absorbed in tactile exploration. Maybe colorful sensory items spilling joyfully. Pure deep-focus sensory play.",
    },
    {
        "id": "66",
        "hebrew_text": "אני עובד!",
        "product_file": "שולחן עבודה.jpg",
        "product_block": "The product is a WOODEN CHILDREN'S WORK TABLE (שולחן עבודה) — a small Montessori-style work table with a flat surface where the child can do activities. Render as ILLUSTRATED watercolor — natural wood, painted not photographic.",
        "scene": "The toddler sits at the small wooden work table doing a 'serious work' activity — pretending to write/draw with a chubby pencil or organizing wooden Montessori materials/blocks neatly, brow furrowed in serious 'professional' concentration, tongue poking out, looking like a tiny important office worker dealing with very important business. Maybe a tiny clipboard or stack of papers. Pure cute mock-grown-up working energy.",
    },
]


# ============================================================
# API CALL
# ============================================================
def generate_image_api(prompt, api_key, model, input_images=None):
    url = f"{API_BASE}/models/{model}:generateContent?key={api_key}"
    parts = []
    for img_bytes, mime in (input_images or []):
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        parts.append({"inlineData": {"mimeType": mime, "data": img_b64}})
    parts.append({"text": prompt})

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": ASPECT_RATIO, "imageSize": IMAGE_SIZE},
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    for p in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in p and p["inlineData"].get("data"):
            return base64.b64decode(p["inlineData"]["data"])
        if "text" in p:
            print(f"    Model returned text: {p['text'][:150]}")
    return None


def generate_with_rotation(prompt, max_attempts=6, input_images=None):
    models = [USE_MODEL, MODEL_FLASH] if USE_MODEL == MODEL_PRO else [MODEL_FLASH]
    for attempt in range(max_attempts):
        key = API_KEYS[attempt % len(API_KEYS)]
        model = models[min(attempt // len(API_KEYS), len(models) - 1)]
        try:
            print(f"    Attempt {attempt + 1} with model {model}, key #{(attempt % len(API_KEYS)) + 1}...")
            img = generate_image_api(prompt, key, model, input_images=input_images)
            if img:
                return img
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")[:200]
            print(f"    HTTP {e.code}: {err}")
            if e.code == 429:
                time.sleep(5)
        except Exception as e:
            print(f"    Error: {str(e)[:200]}")
        time.sleep(2)
    return None


# ============================================================
# MAIN
# ============================================================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load character reference (sticker 01)
    ref_path = CHARACTER_REF if os.path.exists(CHARACTER_REF) else CHARACTER_REF_FALLBACK
    if os.path.exists(ref_path):
        with open(ref_path, "rb") as f:
            character_bytes = f.read()
        print(f"✓ Character reference loaded: {ref_path} ({len(character_bytes)//1024} KB)")
    else:
        print(f"✗ ERROR: Character reference 01.png not found.")
        print(f"   Looked in: {CHARACTER_REF}")
        print(f"   Fallback:  {CHARACTER_REF_FALLBACK}")
        print(f"   Please generate sticker 01 first using generate_all_stickers.py")
        return

    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Model: {USE_MODEL}\n")

    # Filter by argument if provided
    targets = PRODUCT_STICKERS
    if len(sys.argv) > 1:
        try:
            target_num = int(sys.argv[1])
            targets = [s for s in PRODUCT_STICKERS if int(s["id"]) == target_num]
            if not targets:
                print(f"No product sticker #{target_num}")
                return
        except ValueError:
            print(f"Invalid arg: {sys.argv[1]}")
            return

    success = 0
    failed = []
    for ps in targets:
        sid = ps["id"]
        hebrew = ps["hebrew_text"]
        product_file = ps["product_file"]
        product_path = os.path.join(PRODUCTS_DIR, product_file)

        out_path = os.path.join(OUTPUT_DIR, f"{sid}.png")
        if os.path.exists(out_path) and len(sys.argv) == 1:
            print(f"[{sid}] {hebrew} - SKIP (exists)")
            continue

        print(f"\n[{sid}] {hebrew}  (product: {product_file})")

        if not os.path.exists(product_path):
            print(f"    ✗ Product image not found: {product_path}")
            failed.append((sid, hebrew, "no product image"))
            continue

        with open(product_path, "rb") as f:
            product_bytes = f.read()
        print(f"    ✓ Product image loaded ({len(product_bytes)//1024} KB)")
        print(f"    ✓ Character reference attached")

        # Determine MIME type from extension
        ext = os.path.splitext(product_file)[1].lower()
        product_mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

        # Build input images: character ref FIRST, product SECOND
        input_images = [
            (character_bytes, "image/png"),    # IMAGE 1 - character
            (product_bytes, product_mime),     # IMAGE 2 - product
        ]

        full_prompt = PROMPT_TEMPLATE.format(
            hebrew_text=hebrew,
            product_block=ps["product_block"],
            scene=ps["scene"],
        )

        img = generate_with_rotation(full_prompt, input_images=input_images)
        if img:
            with open(out_path, "wb") as f:
                f.write(img)
            print(f"    Saved: {out_path}")
            success += 1
        else:
            print(f"    FAILED")
            failed.append((sid, hebrew, "generation failed"))
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"Done. Success: {success}/{len(targets)}")
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
