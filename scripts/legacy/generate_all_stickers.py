#!/usr/bin/env python3
"""
Generate ALL 56 Kido WhatsApp stickers (1-56) - unified pack.

USAGE:
    python generate_all_stickers.py        # generates all 56 (skips ones that exist)
    python generate_all_stickers.py 5      # regenerates just sticker #5
    python generate_all_stickers.py 35     # regenerates just sticker #35

OUTPUT:
    Files saved to:    סטיקרים לווצאפ/חבילה סופית/גלם/<STYLE>/01.png ... 56.png

CHANGES FROM PREVIOUS VERSION:
    - 56 stickers in one file (instead of 30 + 26 in two files)
    - Apron branding is now SIMPLE HEBREW TEXT "קידו" (instead of trying to reproduce the actual logo graphic)
    - Logo PNG is NOT sent to the model anymore (simpler, more reliable text-based approach)
    - Sticker 01.png is still used as reference for character consistency (sent for stickers 02-56)
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
# CHOOSE YOUR STYLE HERE - change to "A", "B", "C", or "D"
# ============================================================
SELECTED_STYLE = "A"   # A=וואטרקולור (מומלץ)  B=עכשווי  C=3D רך  D=קווים+נקודות

# ============================================================
# CONFIG (same pattern as generate_topic.py)
# ============================================================
SCRIPT_DIR = str(__import__("pathlib").Path(__file__).resolve().parents[2])
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "assets", "source", "collections", "גלם_מאוחד", SELECTED_STYLE)

API_BASE = "https://generativelanguage.googleapis.com/v1beta"

MODEL_PRO = "gemini-3-pro-image-preview"
MODEL_FLASH = "gemini-3.1-flash-image-preview"
USE_MODEL = MODEL_FLASH   # Nano Banana 2 - cheaper/faster than Pro

API_KEYS = [key.strip() for key in os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", "")).split(",") if key.strip()]

ASPECT_RATIO = "1:1"
IMAGE_SIZE = "1K"

LOGO_PATH = os.path.join(SCRIPT_DIR, "assets", "reference", "logo.png")
REFERENCE_STICKER_ID = "01"

# ============================================================
# PROMPT TEMPLATE
# ============================================================
PROMPT_TEMPLATE = """⚠️ READ THIS FIRST — REFERENCE IMAGE ⚠️

If a reference image is attached:
  • It is a previously generated sticker from this same Kido pack.
  • Use it as a reference for the CHARACTER (the toddler's face, hair, proportions, skin tone, illustration style).
  • Match the character appearance and overall illustration style of that reference exactly.

If no reference image is attached:
  • This is the first sticker — establish the character from the description in this prompt.

TASK: Design a single premium WhatsApp sticker for the Kido brand (a Hebrew-language Montessori children's brand).

═══════════════════════════════════════════════
LAYOUT (CRITICAL - follow exactly):
═══════════════════════════════════════════════
• Square 1:1 composition.
• BACKGROUND: CLASSIC TRANSPARENCY-CHECKERBOARD PATTERN. The entire background of the canvas is filled with the standard digital "transparent background" indicator — a regular grid of small alternating squares of WHITE (#FFFFFF) and LIGHT GRAY (#CCCCCC). Each square is roughly 32x32 pixels. The pattern repeats edge-to-edge across the entire canvas as a perfect uniform grid. This signals "transparent PNG" visually. The pattern is soft, neutral, and clearly secondary to the sticker design floating on top of it. NO other texture, NO gradient, NO noise — just the clean checkerboard pattern.
• THE CHARACTER ITSELF must be wrapped in a THICK WHITE STICKER OUTLINE — a smooth white border roughly 8-12 pixels thick that hugs the silhouette of the character, exactly like a printed die-cut sticker peel-off. The white outline cleanly separates the colorful character from the dark background. Subtle soft shadow drops behind the white outline onto the checkerboard background for depth.
• THE HEBREW TEXT sits inside a WHITE PILL-SHAPED SPEECH BUBBLE (rounded rectangle with very high corner radius, almost capsule-shaped) at the TOP of the sticker. The bubble has the SAME thick white sticker outline as the character (matching style). The bubble is sized to comfortably contain the text with padding ~25% of text height around it. The bubble is centered horizontally near the top.
• LAYOUT POSITIONS — BUBBLE AND CHARACTER FORM ONE CONNECTED STICKER:
   - TOP ~25% of canvas: White pill bubble containing Hebrew text, centered horizontally.
   - BOTTOM ~70% of canvas: Character with white sticker outline, centered horizontally.
   - CRITICAL: The bottom edge of the bubble's white outline TOUCHES/CONNECTS with the top of the character's white outline — they are MERGED into ONE continuous unified sticker silhouette (like a speech bubble naturally connecting to the figure that's "speaking"). NO gap between them. The white outline flows from bubble to character as one unbroken white border.
   - Together, the bubble + character read as a SINGLE stamped sticker shape with one continuous white border around the whole thing.
   - One unified soft drop shadow falls behind the entire combined sticker shape on the checkerboard background.

═══════════════════════════════════════════════
HEBREW TEXT (must appear in the image - EXACT FONT SPECIFICATION):
═══════════════════════════════════════════════
• Render this exact Hebrew text at the top of the image: "{hebrew_text}"
• Spelling MUST be EXACTLY: {hebrew_text}  (read right-to-left as Hebrew)

• FONT — THIS EXACT SPECIFICATION (must be IDENTICAL across every sticker in the pack):
   - A SUPER-ROUNDED, CHUBBY, PILLOW-SOFT hand-lettered Hebrew display font — think balloon letters or marshmallow letters, but elegant.
   - EVERY STROKE is FAT AND ROUNDED with a perfectly circular cross-section feel — no flat sides, no sharp angles, no corners ANYWHERE.
   - Each letter looks like it was drawn with a thick rounded marker pen on a smooth surface.
   - All stroke endings terminate in PERFECT CIRCLES (rounded caps), like the ends of pipe-cleaners or rope.
   - Stroke weight: BOLD-CHUBBY and UNIFORM — consistent fat thickness across all strokes (~16-18% of letter height). Letters feel plush and friendly.
   - Letter junctions are SOFTLY CURVED — where two strokes meet, the corner is filleted/rounded, never sharp.
   - Closest commercial Hebrew references: a CHUBBIER-rounder version of Rubik Bold or Heebo Black, with the rounded plushness of "Quicksand Bold" but in Hebrew.
   - Slight hand-lettered warmth — very subtle organic charm in the curves, NOT a perfect digital font, but still very consistent and clean.
   - Generous letter spacing (kerning ~6-10% of letter height between letters).
   - Punctuation marks (! ? ...) match the same fat-rounded style — exclamation marks are CHUBBY VERTICAL CAPSULES with a CIRCLE DOT below, ellipses are 3 PERFECT FAT DOTS.
   - NOT thin. NOT serif. NOT script/cursive. NOT angular. NOT decorative-flourish.
   - VISUAL TARGET: Imagine the warmest, friendliest, rounded "balloon" Hebrew lettering on a premium baby brand product packaging.

• TEXT COLOR: SOLID DARK CHARCOAL #2B2B2B — the text is dark and clearly readable against the white bubble fill. No gradient, no outline on the text itself, no shadow on the text. Just clean dark Hebrew letters inside the white pill bubble.
• TEXT SIZE: large and clearly readable, the text fills the white bubble nicely with comfortable padding around it. The bubble itself occupies roughly 55-70% of canvas width.
• PILL BUBBLE: white fill (#FFFFFF), with the same THICK WHITE STICKER OUTLINE around its edge as the character has, very rounded capsule shape (high corner radius, almost half-circle ends). Soft drop shadow behind the bubble.
• CONSISTENCY IS CRITICAL: This font must look IDENTICAL to the font used in every other Kido sticker — same letterforms, same weight, same hand-lettered character.

═══════════════════════════════════════════════
CHARACTER (the same toddler appears in every sticker - keep IDENTICAL across the pack):
═══════════════════════════════════════════════
The character is ALWAYS the same specific toddler, with these EXACT features:
  • Age: 2-3 years old toddler
  • Hair: messy voluminous CURLY DARK BROWN hair, slightly tousled and natural, falling around the head with cute spirals/curls. Hair is a defining feature.
  • Face shape: round chubby toddler face with soft baby cheeks
  • Cheeks: rosy pink natural blush on both cheeks (a key feature)
  • Eyes: large round expressive dark brown eyes, with small white catchlight highlights for life. Slightly innocent/sweet expression.
  • Nose: tiny soft button nose
  • Mouth: small rosebud mouth, expressive (changes per scene)
  • Skin: warm soft peach skin tone (#FFE0B2)
  • Body: classic chubby toddler proportions — slightly oversized head relative to body, short stubby arms and legs, soft little tummy
  • Outfit: a small Montessori-style apron (color varies per scene to fit naturally) over a simple t-shirt or plain top
  • Footwear: small simple shoes (or barefoot if scene requires)
  • Personality conveyed: warm, sweet, innocent, slightly mischievous when appropriate, deeply expressive

THIS IS THE SAME CHARACTER as in every other Kido sticker. Render the toddler IDENTICALLY each time — same face, same hair, same proportions, same skin tone. The ONLY thing that changes between stickers is the ACTION/POSE/EXPRESSION and the apron color.

{branding_block}

═══════════════════════════════════════════════
VISUAL STYLE:
═══════════════════════════════════════════════
{style_visual}

═══════════════════════════════════════════════
SCENE (the action/expression):
═══════════════════════════════════════════════
{scene}

═══════════════════════════════════════════════
NEGATIVE (avoid all of these):
═══════════════════════════════════════════════
• NO solid color background (no white, no dark, no any solid) — background MUST be the checkerboard transparency pattern (white + light gray small squares).
• NO missing white outline around the character — the white sticker-cutout border is REQUIRED.
• NO text floating without the bubble — text MUST be inside the white pill bubble.
• NO light/colored text — text must be DARK CHARCOAL #2B2B2B inside the white bubble.
• NO English text, NO random letters, NO typos in Hebrew, NO scrambled characters.
• NO character covering the top of the frame (the bubble area must stay clear).
• NO additional text other than "{hebrew_text}".
• NO scary, dark, or unsettling expressions on the character.
• NO photorealism (this is illustration, not photography).
• NO checkerboard squares larger than ~32px or with weird colors — keep it the standard subtle transparency pattern.
"""

BRANDING_BLOCK_WITH_APRON = """═══════════════════════════════════════════════
CHARACTER BRANDING (small "קידו" text on apron pocket):
═══════════════════════════════════════════════
• Dress the child in a small Montessori-style apron (סינר). Choose an apron color that fits the scene naturally (cream, sage, terracotta, soft blue, etc).
• The apron MUST have a visible chest pocket area (or upper-left chest like a brand label spot).
• On that pocket, print the Hebrew brand name "קידו" (4 Hebrew letters: ק-י-ד-ו, reading right-to-left) in a small embroidered/printed style.
• TEXT STYLE for "קידו":
   - Same chubby rounded hand-lettered Hebrew font as the main sticker text (matching the brand typography)
   - Color: dark charcoal #2B2B2B on a light apron, OR cream #FFF8E7 on a dark apron - whichever has strong contrast
   - Looks like it's either embroidered with thread or printed naturally onto the apron fabric
   - Slightly imperfect organic quality (not a stiff digital paste)
• SIZE: SMALL — the word "קידו" should occupy about 20-25% of the apron's bib width.
• POSITION: centered on the apron's chest pocket area.
• Spelling MUST be EXACTLY the 4 Hebrew letters קידו — never invent, scramble, or substitute characters."""

BRANDING_BLOCK_NONE = """═══════════════════════════════════════════════
CHARACTER BRANDING:
═══════════════════════════════════════════════
• This particular sticker does NOT include the Kido logo (the scene doesn't allow for natural placement).
• Do NOT add the logo, watermark, or any brand mark anywhere in the image.
• The reference image is attached for STYLE/aesthetic guidance only — do NOT reproduce the logo in this sticker."""

NO_LOGO_STICKERS = {"09", "26", "53"}   # stickers without apron/character

# ============================================================
# VISUAL STYLE BLOCKS
# ============================================================
STYLES = {
    "A": """Premium hand-painted watercolor children's book illustration in the style of high-end European children's brands like Babai, Lalo, or Blabla Kids. Visible watercolor brush strokes ON THE CHARACTER ONLY (the dark background and white outlines are clean flat colors, not watercolor), gentle color bleeds at the character's edges within the watercolor figure. Outlined with fine ink/pen lines INSIDE the character's silhouette (separate from the thick white sticker outline border around them). The character has soft warm features - rosy cheeks, expressive eyes, joyful presence.

COLOR PALETTE: STRICTLY limited to four brand colors plus skin/hair: cherry red (#E53935), warm sunshine yellow (#FDD835), fresh leaf green (#43A047), and bright sky blue (#1E88E5). Skin tone warm peach (#FFE0B2). Hair dark brown. Rosy pink cheeks (#FFB6C1).""",

    "B": """Contemporary modern children's illustration with a Scandinavian indie children's brand aesthetic - think Sago Mini meets a premium picture book. Soft flat colors. Light and airy, friendly stylized character with simple but expressive features. Slightly geometric simplification of forms.

COLOR PALETTE: Brand palette of cherry red (#E53935), warm yellow (#FDD835), fresh green (#43A047), bright blue (#1E88E5), warm peach skin (#FFE0B2). Modern, harmonious.""",

    "C": """Premium soft 3D rendered character in the style of contemporary children's apps and brands like Lingokids, Khan Academy Kids, or Playdate. Soft subsurface scattering on skin, gentle rim lighting, smooth rounded forms with no sharp edges. Pixar-like quality but simpler and more iconic. Toy-like proportions with oversized head.

COLOR PALETTE: Cherry red (#E53935), warm yellow (#FDD835), fresh green (#43A047), bright blue (#1E88E5) used as primary clothing/prop colors. Warm skin tone, soft hair colors.""",

    "D": """Bold modern vector illustration in a "lines and dots" graphic language directly inspired by the Kido brand logo. The character is constructed from THICK ROUNDED TUBE outlines (like rounded soft pipes) where many line endings terminate in small filled circles/dots - this is the signature brand element. Clean solid color fills inside the tube outlines.

COLOR PALETTE: STRICT four-color palette - cherry red (#E53935), warm yellow (#FDD835), fresh green (#43A047), bright blue (#1E88E5). Each major shape gets one solid brand color. Outlines in dark charcoal (#2B2B2B).""",
}

# ============================================================
# 30 STICKER SCENES
# ============================================================
STICKERS = [
    ("01", "אני רוצה לבד!",          "A toddler aged 2-3 with curly dark brown hair, sitting on the floor with one bare foot extended forward. ONE small shoe is already sitting empty on the floor next to them (visible). The toddler holds the OTHER small shoe in both tiny hands, dramatically focused on trying to put it onto their bare extended foot themselves. Tongue sticking out in pure concentration. Pure independent toddler determination. Empty background, square 1:1 framing."),
    ("02", "הצלחתי!!!",           "A toddler aged 2-3 with curly dark brown hair, RADIATING PURE OVERWHELMING JOY — both tiny fists raised triumphantly high above the head in a victory pose, the BIGGEST possible open-mouthed grin showing baby teeth, eyes squeezed almost shut from the intensity of happiness with crinkles at the corners, cheeks lifted high in a huge smile, head tilted up to the sky, slightly jumping with excitement. Glowing aura of accomplishment. Tiny stars and sparkles bursting around them celebrating the win. The toddler looks absolutely thrilled and proud — their whole body screams 'I JUST DID IT!'. Empty background, square 1:1 framing."),
    ("03", "תני לי!!",            "A toddler aged 2-3 with curly dark brown hair, small hand reaching out forward demandingly with palm up, eyes locked on something they want, mouth slightly open in anticipation. Direct toddler 'gimme!' demand. Empty white background, square 1:1 framing."),
    ("04", "עוד! עוד!!",          "A toddler aged 2-3 with curly dark brown hair clapping hands excitedly above their head, mouth wide open in pure delight, eyes squinted with joy, slightly jumping. Communicates 'again! again! again!' with infectious enthusiasm. The toddler wears a LIGHT-COLORED apron (cream, soft beige, or pale sage) so that the embroidered Kido logo on the apron pocket appears in DARK CHARCOAL THREAD for strong contrast. Empty background, square 1:1 framing."),
    ("05", "אני אלוף!",           "A toddler aged 2-3 with curly dark brown hair successfully standing on top of a small wooden Montessori stool, both arms raised in V-for-victory, triumphant beaming smile, eyes bright. Pure champion moment. Empty white background, square 1:1 framing."),
    ("06", "רגע, חושב...",        "A toddler aged 2-3 with curly dark brown hair, finger pressed thoughtfully to temple, eyes looking up to the side in deep thought, tiny pursed lips. A small bright lightbulb floats above their head. Communicates concentrated thinking. Empty white background, square 1:1 framing."),
    ("07", "לא אני!!",            "A toddler aged 2-3 with curly dark brown hair, both palms turned up dramatically in a 'wasn't me!' shrug, eyebrows raised high in exaggerated innocence, small mischievous smile barely hidden. Communicates playful denial. Empty white background, square 1:1 framing."),
    ("08", "אני מת מרעב!!",        "A toddler aged 2-3 with curly dark brown hair STANDING UPRIGHT (full body visible from head to feet, NOT sitting), BOTH HANDS clutching their soft round belly tightly, looking extremely hungry — mouth slightly open, lips downturned with hunger longing, eyes large and a bit dramatic with that 'I am STARVING' look (intense hunger, but cute not sad), maybe a tiny grumbling-tummy line/sparkle near the belly. Standing posture slightly bent forward at the waist toward the belly, body language of 'oh my belly is SO empty'. The toddler wears a LIGHT-COLORED apron (cream, soft beige, or pale sage) so the embroidered Kido logo on the apron pocket appears in DARK CHARCOAL THREAD for strong contrast. Empty background, square 1:1 framing."),
    ("09", "עוד שנייה!!",          "A toddler aged 2-3 with curly dark brown hair lying face-down on a soft pillow, one arm dangling over the edge of the bed, hair messy, eyes barely open in sleepy protest, blanket askew. Communicates classic morning 'just five more minutes!' protest. Empty white background, square 1:1 framing."),
    ("10", "אני לא עייף בכלל!",    "A toddler aged 2-3 with curly dark brown hair rubbing one eye with a tiny fist, while obviously exhausted - eyes half-closed, mouth caught mid-yawn they tried to hide, pajamas slightly visible. Communicates absolute denial of being sleepy. Empty white background, square 1:1 framing."),
    ("11", "למממהה??",            "A toddler aged 2-3 with curly dark brown hair in PURE SHOCK AND DISBELIEF — mouth dropped open WIDE in a big stunned 'O' shape, eyes ENORMOUSLY wide and round (almost popping out), eyebrows shot WAY UP high above the eyes in disbelief, both tiny hands raised dramatically up by the cheeks (classic shock pose, palms forward), head tilted slightly back from the surprise, frozen mid-reaction. A tiny shock cloud or sparkles burst around the head emphasizing the stun. The toddler looks utterly bewildered and shocked, like they just heard the most unbelievable news. Empty background, square 1:1 framing."),
    ("12", "משעמם לי!!",           "A toddler aged 2-3 with curly dark brown hair COMPLETELY MELTED with extreme boredom — slumped/draped against a wall or piece of furniture, body totally limp like jello, head hanging forward heavily or tilted to the side, eyes half-closed and glazed over staring blankly at nothing in particular (zero focus), mouth slightly hanging open with a tiny dramatic sigh escaping, one tiny arm dangling lifelessly. Body language screams 'I have NOTHING to do, my life is OVER'. The toddler is the absolute picture of dramatic toddler ennui — exaggerated melodramatic boredom that's cute and funny. Maybe a tiny zZz or sigh-cloud floating up. Empty background, square 1:1 framing."),
    ("13", "אני כל כך כועס!!",     "A toddler aged 2-3 with curly dark brown hair, arms crossed firmly across chest, eyebrows scrunched DOWN hard, cheeks puffed out red, mouth in a tight pout, two visible steam puff icons by their ears. Communicates valid intense anger - dramatic but cute, not scary. The toddler wears a LIGHT-COLORED apron (cream, soft beige, or pale sage) so the embroidered Kido logo on the apron pocket appears in DARK CHARCOAL THREAD for strong contrast. Empty background, square 1:1 framing."),
    ("14", "בא לי לבכות...",       "A toddler aged 2-3 with curly dark brown hair sitting curled up small, knees hugged to chest, big sparkling tears welling up in lower eyelids about to spill, mouth quivering in a soft pre-cry frown, eyes downcast. Tender pre-cry moment. Empty white background, square 1:1 framing."),
    ("15", "כייייף!!!",            "A toddler aged 2-3 with curly dark brown hair caught mid-jump in the air, both arms wide open above their head, legs slightly kicked back, biggest most genuine open-mouthed laugh, eyes crinkled with pure joy. Sparkles and tiny stars around them. Empty white background, square 1:1 framing."),
    ("16", "בוא ננשום יחד",        "A toddler aged 2-3 with curly dark brown hair sitting cross-legged in a calm meditation pose, eyes peacefully closed, one small hand resting gently on chest, soft gentle smile, shoulders relaxed. A subtle soft swirl of breath visible around them. Empty white background, square 1:1 framing."),
    ("17", "רגשות זה בסדר",        "A toddler aged 2-3 with curly dark brown hair standing while wrapping both arms around themselves in a gentle self-hug, soft warm smile, eyes closed peacefully, glowing peaceful aura. Communicates self-acceptance. IMPORTANT: For this specific sticker, the embroidered Kido logo on the apron pocket should be EVEN SMALLER than usual — about 10-12% of the apron bib width (smaller than the standard 15-20%). Make it a subtle small embroidered label, almost like a quiet detail. Empty background, square 1:1 framing."),
    ("18", "חיבוק!!",            "A toddler aged 2-3 with curly dark brown hair, ARMS WIDE OPEN in a big eager open-armed hug-me pose, leaning slightly forward with a warm yearning soft pleading expression — eyes big and tender looking up hopefully, mouth in a soft sweet half-smile that looks like it might tremble, slightly puppy-dog eyes that say 'PLEASE hug me, I really need it'. Body language is warm, vulnerable, and OPEN — radiating need for affection and warmth. The toddler clearly NEEDS a hug right now, not playfully demanding but genuinely emotionally yearning for one. A few small floating hearts around them emphasize the warm love-seeking energy. Empty background, square 1:1 framing."),
    ("19", "כל הכבוד!!!",          "A FULL toddler aged 2-3 with curly dark brown hair, body visible from head to feet, enthusiastically clapping their hands LOUDLY together in front of their chest, hands meeting with energy (slight motion blur on the clap), eyes bright and beaming with joy, mouth wide open in a delighted YAY shout. Golden confetti and small sparkles bursting outward around them. Pure full-body celebratory toddler cheering. Empty background, square 1:1 framing."),
    ("20", "אני גאה בך!",          "A toddler aged 2-3 with curly dark brown hair standing proudly next to a small tower of stacked wooden Montessori blocks/cubes that they just built. Several MORE WOODEN BLOCKS/CUBES (in natural wood + soft brand colors) are scattered around the toddler's feet on the floor. The toddler stands with chest puffed out proudly, big beaming triumphant smile, eyes bright and looking forward seeking approval, one tiny hand resting on top of the block tower they built. Pure achievement and pride moment. The toddler wears their normal Montessori apron with the embroidered Kido logo clearly visible on the chest pocket. Empty background, square 1:1 framing."),
    ("21", "סבלנות...",            "A toddler aged 2-3 with curly dark brown hair sitting calmly cross-legged on the floor, body relaxed and still, ACTIVELY PRACTICING PATIENCE — both small hands folded politely in their lap (one resting on top of the other), eyes peacefully closed or half-closed in calm focus, soft serene smile, shoulders relaxed and dropped, a small wooden Montessori hourglass/sand-timer beside them with sand slowly trickling down (clearly showing the passage of time and patience). Subtle peaceful aura around them. The toddler clearly communicates 'I am being patient and waiting calmly' — Montessori emotional self-regulation in action. Empty background, square 1:1 framing."),
    ("22", "אמא צריכה קפה",         "A large warm steaming coffee mug front and center, with a small toddler aged 2-3 with curly dark hair clinging affectionately to the side of the mug as if it were a person they love. Steam curls upward. Cute and humorous. Empty white background, square 1:1 framing."),
    ("23", "נשימה עמוקה",          "A toddler aged 2-3 with curly dark brown hair shown in three-quarter view (slightly turned to the side but the chest is visible to the viewer), gently blowing out a soft visible breath stream from puffed cheeks, eyes peacefully closed in calm focus, one tiny hand resting on the chest in a mindful breathing pose, calm wave of breath visible flowing out. Communicates mindful breathing and self-regulation. The toddler wears their normal Montessori apron with the embroidered Kido logo clearly visible on the chest pocket area. Empty background, square 1:1 framing."),
    ("24", "המון אהבה!",           "A toddler aged 2-3 with curly dark brown hair hugging a huge soft glowing cherry-red heart that is bigger than their head, holding it close to their chest with both arms wrapped lovingly around it, eyes closed peacefully with a sweet warm smile, rosy cheeks, pure tender love radiating. The toddler wears their normal apron. Small floating colored dots in the brand colors (yellow, green, blue) scattered playfully around them. CRITICAL: the embroidered Kido logo appears ONLY on the apron pocket as usual — NOT on the heart. The heart itself is completely clean and pure with NO logo, NO text, NO marks of any kind on its surface. Empty background, square 1:1 framing."),
    ("25", "בוקר טוב",             "A toddler aged 2-3 with curly dark brown hair sitting up in bed stretching both arms way up overhead, mouth in a wide yawn, sleepy peaceful smile, a bright golden sun peeking from the corner of the frame. Empty white background, square 1:1 framing."),
    ("26", "לילה טוב",             "A toddler aged 2-3 with curly dark brown hair curled up sleeping peacefully under a soft cozy blanket, hugging a small teddy bear, eyes closed, tiny zZz floating up, a small crescent moon and stars in the corner. Empty white background, square 1:1 framing."),
    ("27", "אני רוצה אוכל!",        "A toddler aged 2-3 with curly dark brown hair sitting at a small table with empty plate in front of them, banging a wooden spoon on the table demandingly, eager smile, eyes bright with hunger anticipation. Empty white background, square 1:1 framing."),
    ("28", "אמבטיהההה!",            "A toddler aged 2-3 with curly dark brown hair sitting INSIDE a foamy bubble bath up to the shoulders, head clearly visible above the bubbles with a HUGE joyful open-mouthed laugh, eyes squinted with delight, both small hands raised splashing the water playfully, water droplets and big soap bubbles flying through the air around them, a yellow rubber duck floating beside them. A small folded towel rests on the rim of the bathtub beside them with a tiny embroidered Kido logo visible on its corner (the brand mark appears as a label on the towel since the toddler is in the bath without clothes). Pure bath-time joy. Empty background, square 1:1 framing."),
    ("29", "תודה!",                "A toddler aged 2-3 with curly dark brown hair standing with both small hands pressed together at chest in a gentle namaste/gratitude pose, eyes warmly closed, sweet thankful smile, slight bow of the head. Empty white background, square 1:1 framing."),
    ("30", "לישוןןןן...",          "A toddler aged 2-3 with curly dark brown hair hugging a soft teddy bear close to their chest with both arms, rubbing one sleepy eye with a tiny fist, mouth open in a big yawn, eyes barely open, wearing soft pajamas, slow nodding-off energy. The toddler wears a LIGHT-COLORED apron (cream, soft beige, or pale sage) so the embroidered Kido logo on the apron pocket appears in DARK CHARCOAL THREAD for strong contrast. Empty background, square 1:1 framing."),

    # ═══════ Extra pack: stickers 31-56 ═══════
    # ═══ קטגוריה A: דרמות ואסונות יומיומיים ═══
    ("31", "אויי... שיט!",                "A toddler aged 2-3 with curly dark brown hair STANDING in a small visible BATHROOM SCENE — a clear toilet/potty in the background behind them, light bathroom tiled floor and walls visible. On the bathroom floor in front of the toddler is a CLEAR CARTOON POOP EMOJI 💩 STYLE pile (the classic brown swirly soft-serve poop emoji shape — universally recognized, cute and stylized, NOT realistic, with little smile if appropriate). The toddler stands beside the cartoon poop pile, looking down at it confused, with brown smears (matching the cartoon-emoji style) on their tiny raised hands which they hold up looking at, mouth in a small surprised 'oh!' expression. Pure innocent toilet-training mishap with both the BATHROOM SETTING (toilet visible) and the cartoon poop CLEARLY VISIBLE on the floor — playful and cartoony, NOT gross or realistic. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background outside the bathroom scene, square 1:1 framing."),
    ("32", "אוי לא...",            "A toddler aged 2-3 with curly dark brown hair STANDING beside an overturned cup of milk that has spilled in a big puddle on the floor, looking down at the disaster with wide shocked eyes and a small open mouth in pure 'oh no!' realization, hands raised slightly. Empty cup tipped on its side beside the puddle. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("33", "ציירתי על הקיר!",      "A toddler aged 2-3 with curly dark brown hair STANDING proudly in front of a white wall covered with colorful crayon scribbles (red, yellow, green, blue lines), holding a big crayon up triumphantly in one hand, beaming proud smile, eyes sparkling with pride at their 'masterpiece'. Pure innocent toddler artistic pride (oblivious to having done something wrong). The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("34", "דחוף!!",          "A toddler aged 2-3 with curly dark brown hair STANDING with legs crossed dramatically in URGENT bathroom emergency pose, both hands clutching/holding the pelvis area, face scrunched in panicked urgency, eyes wide and pleading, mouth in a desperate 'O', slightly hopping on the spot. Pure 'I gotta go RIGHT NOW' panic. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("35", "סיימתי! הכל נקי",            "A toddler aged 2-3 with curly dark brown hair STANDING completely covered in food/sauce/chocolate smears all over the face, hands, and apron, hair messy with bits of food, mouth in a HUGE proud delighted grin, eyes sparkling with joy, arms spread wide showing off the mess. Pure 'look how I ate!' pride. The toddler wears their normal apron with the embroidered Kido logo barely visible through the mess on the chest pocket. Empty background, square 1:1 framing."),
    ("36", "חתכתי לעצמי שיער",     "A toddler aged 2-3 with curly dark brown hair, but with a TERRIBLE chunky uneven self-haircut — one side dramatically shorter than the other, missing patches, holding child-safe scissors in one tiny hand and a small lock of cut hair in the other, beaming a HUGELY proud smile like they just accomplished something amazing, completely oblivious to the disaster. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("37", "זה היה כבר ככה...",    "A toddler aged 2-3 with curly dark brown hair STANDING beside a clearly broken/damaged item (broken vase pieces or scattered toys), pointing innocently at it with one tiny finger, OVERLY innocent wide-eyed expression with raised eyebrows, halo-like glow above the head (visual joke), mouth in a tight little 'wasn't me' smile. Pure deflection energy. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),

    # ═══ קטגוריה B: התקפי זעם ודרמה ═══
    ("38", "לאאאאא!!!",            "A toddler aged 2-3 with curly dark brown hair COMPLETELY MELTED DOWN — lying flat on the floor on their back in full tantrum mode, both fists pounding the floor, legs kicking, mouth WIDE OPEN in a dramatic wailing cry, eyes squeezed shut with two big dramatic tears flying out, face slightly red. Pure dramatic toddler tantrum theater (cute, exaggerated, not scary). The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("39", "זה שלי!!",             "A toddler aged 2-3 with curly dark brown hair clutching a small toy (teddy bear or favorite item) tightly to their chest with both arms, body slightly turned away protectively, eyebrows scrunched down possessively, mouth in a fierce determined pout, eyes glaring sideways at someone trying to take it. Pure toddler ownership rage. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("40", "אני שונא!",            "A toddler aged 2-3 with curly dark brown hair sitting at a small table with a plate of food (vegetables) in front of them, arms firmly crossed across chest, looking down at the food with disgusted scrunched-up face, lips pursed sideways in a refusing pout, eyebrows angry. Pure 'I hate this food' refusal energy. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("41", "אני לא מדברת!",        "A toddler aged 2-3 with curly dark brown hair STANDING with their head turned dramatically all the way away from the viewer (back of head and curls visible, profile of one cheek), arms crossed firmly, body language saying 'I'm giving you the silent treatment'. Maybe one eye peeking back to check. Pure dramatic toddler silent treatment. The toddler wears their normal apron with the embroidered Kido logo visible on the chest pocket. Empty background, square 1:1 framing."),
    ("42", "אני אגיד לאמא!!",      "A toddler aged 2-3 with curly dark brown hair STANDING with one tiny accusing finger dramatically pointed forward, mouth open in mid-shout, eyebrows up in self-righteous fury, the OTHER hand holding an imaginary phone to ear or pointing to themselves, body angled like they're about to run away to tattle. Pure 'I'm telling mom!' threat energy. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),

    # ═══ קטגוריה C: רגעים מתוקים ═══
    ("43", "אני אוהב אותך",        "A toddler aged 2-3 with curly dark brown hair giving a BIG warm hug to a MOTHER'S LEG — only the mom's leg is visible from mid-thigh down. The mom is wearing comfortable PANTS (soft cotton lounge pants or jeans) that come down to the ankle area, and her FOOT IS BARE (NO SOCKS, NO SHOES — just bare skin foot with cute pedicured toes peeking out from below the pant cuff). The child wraps their tiny arms tenderly around the mom's pants-covered calf, eyes peacefully closed, soft tender smile, cheeks pressed against the leg lovingly. Small floating hearts around them. Pure unconditional toddler love. The toddler wears a LIGHT-COLORED apron (cream, soft beige, or pale sage) so the embroidered Kido logo on the apron pocket appears in DARK CHARCOAL THREAD for strong contrast. Empty background, square 1:1 framing."),
    ("44", "תקראי לי..?",          "A toddler aged 2-3 with curly dark brown hair STANDING holding a small picture book up toward the viewer with both small hands, eyes large and pleading sweetly, mouth in an irresistible little half-smile, head tilted slightly. Pure 'please read to me' hopeful charm. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("45", "בוא נשחק!",            "A toddler aged 2-3 with curly dark brown hair STANDING enthusiastically holding out a small wooden Montessori toy with both hands toward the viewer in invitation, beaming bright welcoming smile, eyes sparkling with hope and excitement, body language of 'come play with me!'. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("46", "אני מתגעגע",           "A toddler aged 2-3 with curly dark brown hair sitting on the floor beside the front door, small backpack beside them, looking up at the door with big sad longing eyes, one small tear, soft yearning expression of pure missing someone. Pure tender separation longing. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("47", "תפסה אותי!",           "A toddler aged 2-3 with curly dark brown hair caught mid-running away with an enormous laughing open-mouthed grin, looking back over the shoulder with playful eyes, hair flying in the motion, arms swinging in playful escape, slight motion lines showing speed. Pure playful chase energy. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),

    # ═══ קטגוריה D: לוגיקת ילדים מטורפת ═══
    ("48", "למה לכלב יש זנב?",     "A toddler aged 2-3 with curly dark brown hair STANDING with one tiny finger thoughtfully on the chin in a deep philosophical pondering pose, head tilted dramatically, eyes large and contemplative looking up at the sky, mouth slightly open in deep thought. A small cute illustrated dog with a wagging tail beside them being studied. Pure profound toddler philosophy. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("49", "אני אהיה אסטרונאוט!",  "A toddler aged 2-3 with curly dark brown hair STANDING wearing an oversized adult astronaut helmet (way too big, falling over the eyes) and a too-large NASA jacket draped on shoulders, beaming a huge dreamy proud smile, both arms triumphantly raised. Pure aspirational toddler dream-up. The toddler wears their normal apron under the oversized jacket with the embroidered Kido logo barely peeking out. Empty background, square 1:1 framing."),
    ("50", "אני יכול לעוף!",       "A toddler aged 2-3 with curly dark brown hair caught mid-jump from a low ottoman/cushion with both arms spread wide like wings, hair flying up, mouth wide open in a daring shouting laugh, eyes squeezed in pure joy, totally convinced they can fly. Pure toddler invincibility. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("51", "השמש הולכת לישון",     "A toddler aged 2-3 with curly dark brown hair STANDING by a window pointing one tiny finger up toward a setting sun (warm orange/pink glow visible through the window), looking up with wonder, mouth in a soft 'oh!' of discovery, eyes wide and curious. Pure innocent toddler observation of nature. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),

    # ═══ קטגוריה E: Voice של הורים ═══
    ("52", "אמא צריכה רגע...",     "An adult mother (only the upper body visible from chest up, soft warm features, hair tied back, no specific identifying features) sitting on the bathroom floor with back against the wall, both hands covering the face in exhaustion, slightly disheveled, a small floating thought-bubble showing a coffee cup. Pure mom-needs-a-break exhaustion (cute, relatable, not sad). NO TODDLER in this sticker — just the mom alone needing a moment. The mom wears a small Montessori-style apron (the same kind the toddler wears in other stickers, but adult-sized) with the embroidered Kido logo CLEARLY VISIBLE on the apron chest area — positioned BELOW her hands so it stays in view (her hands cover her face, leaving the chest/apron area unobstructed). Square 1:1 framing."),
    ("53", "מתי הם יישנו?",         "An adult parent figure (warm features, only upper body) sitting on a couch with one hand on the forehead in tired exasperation, the other hand pointing toward a wall clock that shows it's late at night, eyes droopy with exhaustion, soft tired smile. NO TODDLER in this sticker. A small zZz cloud above the parent. Empty background, square 1:1 framing."),
    ("54", "5,4,3...",             "An adult parent's hand visible from the elbow down, fingers raised counting down (showing 5 fingers, with one in the process of curling down), the parent's stern but warm pointing posture, with a small toddler (2-3 with curly dark brown hair) in the foreground/corner of the frame looking up nervously realizing they need to comply NOW. Pure parent count-down warning. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("55", "לקחת את החטיף?",       "A peace-offering scene: an adult parent's hand visible from the side holding out a small cute-looking snack/cookie toward the viewer in a making-up gesture, with a small toddler (2-3 with curly dark brown hair) tentatively reaching for it with one small hand, expression softening from upset to being won over. Pure parent peace-offering charm. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
    ("56", "אמא תמיד צודקת",     "A toddler aged 2-3 with curly dark brown hair standing with one tiny finger raised UPWARDS WISELY (like delivering profound life wisdom), looking sideways/up at a DAD figure beside them (only the dad's lower face, shoulder, and upper torso visible from the side — dad is kneeling down to the toddler's level to hear). The toddler has a SERIOUS WISE SAGE-LIKE expression with a tiny knowing smile, mouth slightly open mid-sentence as if delivering IMPORTANT TRUTH, eyes confident and matter-of-fact. The dad listens attentively with a soft amused smile, slightly leaning in. A tiny floating wisdom sparkle or small lightbulb above the toddler's head emphasizes the wise pronouncement. Pure cheeky toddler stating an obvious fact. The toddler wears their normal apron with the embroidered Kido logo on the chest pocket. Empty background, square 1:1 framing."),
]


# ============================================================
# API CALL
# ============================================================
def generate_image_api(prompt, api_key, model, input_images=None):
    """Generate via Gemini. input_images: list of (bytes, mime) tuples to send as reference."""
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
    """Try generating with key rotation and model fallback."""
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


def load_reference_sticker():
    """Load sticker 01 from output dir if it exists - used as a style reference."""
    ref_path = os.path.join(OUTPUT_DIR, f"{REFERENCE_STICKER_ID}.png")
    if os.path.exists(ref_path):
        with open(ref_path, "rb") as f:
            return f.read()
    return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    style_visual = STYLES[SELECTED_STYLE]

    if not os.path.exists(LOGO_PATH):
        print(f"WARNING: Logo not found at {LOGO_PATH}")
        logo_bytes = None
    else:
        with open(LOGO_PATH, "rb") as f:
            logo_bytes = f.read()
        print(f"Loaded logo: {LOGO_PATH} ({len(logo_bytes)//1024} KB)")

    # Load sticker 01 if it exists - it'll be sent as 2nd reference for stickers 02-30
    # to enforce character consistency across the pack.
    reference_bytes = load_reference_sticker()
    if reference_bytes:
        print(f"✓ Found {REFERENCE_STICKER_ID}.png — will use as character reference for stickers 02-30")
    else:
        print(f"  No {REFERENCE_STICKER_ID}.png yet — first sticker will be generated without character reference")

    print(f"Style: {SELECTED_STYLE}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Model: {USE_MODEL}\n")

    targets = STICKERS
    if len(sys.argv) > 1:
        try:
            target_num = int(sys.argv[1])
            targets = [s for s in STICKERS if int(s[0]) == target_num]
            if not targets:
                print(f"No sticker #{target_num}")
                return
        except ValueError:
            print(f"Invalid arg: {sys.argv[1]}")
            return

    success = 0
    failed = []
    for sid, hebrew, scene in targets:
        out_path = os.path.join(OUTPUT_DIR, f"{sid}.png")
        if os.path.exists(out_path) and len(sys.argv) == 1:
            print(f"[{sid}] {hebrew} - SKIP (exists)")
            continue

        branding = BRANDING_BLOCK_NONE if sid in NO_LOGO_STICKERS else BRANDING_BLOCK_WITH_APRON
        has_logo = sid not in NO_LOGO_STICKERS
        print(f"\n[{sid}] {hebrew}"
              f"{'  (no logo)' if not has_logo else ''}")

        # Build input images:
        # - For sticker 01: send LOGO only (no reference yet)
        # - For stickers 02-30: send REFERENCE STICKER (01) FIRST, then LOGO LAST
        #   The model gives more weight to the LAST image, so logo (truth source) goes last
        using_ref = sid != REFERENCE_STICKER_ID and reference_bytes is not None
        input_images = []
        if using_ref:
            input_images.append((reference_bytes, "image/png"))   # IMAGE 1: character/style reference
            print(f"    ✓ Attaching reference sticker ({REFERENCE_STICKER_ID}.png) for character consistency")
        if logo_bytes:
            input_images.append((logo_bytes, "image/png"))         # IMAGE 2 (LAST): authoritative logo
            print(f"    ✓ Attaching logo image ({len(logo_bytes)//1024} KB) as logo source")
        else:
            print(f"    ✗ NO LOGO IMAGE ATTACHED (logo file was not loaded!)")



        full_prompt = PROMPT_TEMPLATE.format(
            hebrew_text=hebrew,
            style_visual=style_visual,
            scene=scene,
            branding_block=branding,
        )

        img = generate_with_rotation(full_prompt, input_images=input_images)
        if img:
            with open(out_path, "wb") as f:
                f.write(img)
            print(f"    Saved: {out_path}")
            success += 1
            # If we just generated 01, refresh reference for subsequent iterations
            if sid == REFERENCE_STICKER_ID:
                reference_bytes = img
                print(f"    Now using {sid}.png as character reference for remaining stickers")
        else:
            print(f"    FAILED")
            failed.append((sid, hebrew))
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"Done. Success: {success}/{len(targets)}")
    if failed:
        print(f"Failed: {failed}")
        print(f"Re-run individual ones with: python {os.path.basename(__file__)} <number>")


if __name__ == "__main__":
    main()
