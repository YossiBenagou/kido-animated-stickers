"""Read-only image inventory and contact sheets; never modifies source art."""
from pathlib import Path
import hashlib, json, collections
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work' / 'inventory'
OUT.mkdir(parents=True, exist_ok=True)
groups = collections.defaultdict(list)
records = []
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'} or any(x in p.relative_to(ROOT).parts for x in ('work', '.git')):
        continue
    raw = p.read_bytes()
    with Image.open(p) as im:
        rgba = im.convert('RGBA')
        rec = dict(path=p.relative_to(ROOT).as_posix(), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), width=im.width, height=im.height, alpha=rgba.getchannel('A').getextrema(), frames=getattr(im, 'n_frames', 1))
    records.append(rec)
    groups[str(p.parent.relative_to(ROOT))].append(rec)
for idx, (folder, items) in enumerate(groups.items()):
    sheet = Image.new('RGB', (1000, ((len(items)+5)//6)*155+40), '#e7e8eb')
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), f'Collection {idx:02d} — {len(items)} images', fill='black')
    for n, r in enumerate(items):
        with Image.open(ROOT/r['path']) as im:
            thumb=ImageOps.contain(im.convert('RGBA'), (150,125))
            x=(n%6)*166+(166-thumb.width)//2; y=40+(n//6)*155
            sheet.paste(thumb,(x,y),thumb)
        d.text(((n%6)*166+8,y+128), Path(r['path']).stem,fill='black')
    sheet.save(OUT/f'collection-{idx:02d}.jpg')
hashes=collections.defaultdict(list)
for r in records: hashes[r['sha256']].append(r['path'])
report=dict(images=records, collections=[dict(index=i,path=k,count=len(v)) for i,(k,v) in enumerate(groups.items())], duplicates=[v for v in hashes.values() if len(v)>1])
(OUT/'inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(files=len(records),unique=len(hashes),duplicate_copies=sum(len(v)-1 for v in hashes.values()),collections=report['collections']),ensure_ascii=False,indent=2))
