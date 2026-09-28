# Production contract

Current target: WhatsApp animated stickers, generated one situation at a time using hatch-pet's identity/reference discipline and connected-component extraction. Codex-pet v2 atlases are outside the requested WhatsApp deliverable.

Original illustration and captions are preserved as references. Generated strips omit captions; the original Hebrew caption is composited consistently onto every frame. Deterministic extraction uses the installed hatch-pet extraction code copied to `scripts/vendor/hatch_extract.py`. A common scale across a strip preserves pose proportions. Tiny disconnected extraction noise is filtered by the hatch-pet component threshold. Existing transparency is retained.

Generation uses the built-in imagegen tool only. No external API billing, prepaid credits, Magnific or paid fallback is authorized for this run. Stop on a generation usage-limit response; preserve status and resume later. Legacy Gemini generators are retained only as source history and must not be executed without separate authorization.

Checks per sticker: six distinct generated poses; matching character and props; visual action appropriate to caption; no visible clipping; caption legible; transparent 512px canvas; actual animation; <=500,000 bytes; each frame >=8ms; total <=10s; loop=0. Technical validation does not replace visual QA. `awaiting_visual_qa` is not `complete`.

Production proceeds by collection in packs of up to 30; `catalog.json` and `progress.md` record the current queue and approved outputs. Alternate older art and curated final choices remain available for later edits rather than being discarded as duplicates.
