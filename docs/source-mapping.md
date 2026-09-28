# Reference mapping audit

The source filenames are not always semantic sticker numbers. A visual audit of all 56 girl caption crops found these mismatches in the transparent-source folder:

- Transparent `08.png` is the denial illustration for girl-07.
- Transparent `09.png` is the hungry illustration for girl-08.
- The sleepy-bed girl-09 uses the original opaque `09.png`.
- Transparent `31.png` is the spill illustration for girl-32; girl-31 uses original `31.png`.
- girl-53 keeps the source caption `הם עוד לא במיטה`.

`catalog.json` records the corrected references. The early girl-08 strip and girl-09 candidate were rejected and regenerated from the matching references. The rejected girl-09 candidate remains as an explicitly named reference, excluded from export. Original source files are preserved unchanged. Verify the pictured caption and scene, not only the filename, before every generation job.

