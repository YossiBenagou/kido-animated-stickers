# Kido sticker project

- Continue from `catalog.json` and `docs/progress.md`; do not regenerate completed stickers unnecessarily.
- The user wants all collections, produced pack by pack. Each final sticker must be its own situation-specific animated WebP for WhatsApp.
- Use hatch-pet's grounded character/pose workflow and its deterministic extraction. The target is a WhatsApp loop, not a Codex pet atlas.
- Use the built-in imagegen tool under the existing subscription only. The user explicitly forbids additional expenditure. No paid API fallback, prepaid credit usage, Magnific, or automatic usage-reset redemption. If a usage limit is returned, stop generation, save state and continue in a later session.
- Use one lightweight generation worker per visual job, with the exact reference attached. An independent worker reviews contact sheets. The parent owns catalog updates, assembly, QA acceptance, packaging and commits.
- Preserve the original Hebrew caption as a static layer. Inspect its crop: several source captions touch hair, kippah or decorative effects. Per-sticker crop fixes belong in `scripts/assemble_sticker.py`.
- Do not fake animation by moving/rotating a whole static sticker. Generate meaningful pose/expression changes appropriate to the caption.
- Do not mark an item complete before its technical validation and visual QA pass. Review actual exported animation where practical; phone import has not been verified.
- Keep original unique art, generated strips, prompts and frames for future editing. Remove only demonstrated exact duplicates or disposable work/cache.
- Never commit credentials. Legacy generation scripts are retained for source history and must not run without separate authorization.
- For supported office documents, spreadsheets, presentations, EPUB, CSV or PDF, invoke convert-documents-to-markdown, preserve the source, convert under work/, and read the Markdown explicitly as UTF-8 through EOF. Supplement image-dependent documents with rendering/OCR and disclose unreadable content.
- Public GitHub repository: https://github.com/YossiBenagou/kido-animated-stickers. Commit and push at each completed pack checkpoint.
