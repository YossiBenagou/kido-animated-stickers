"""Package only visually approved, technically valid animated stickers."""
from pathlib import Path
import json,zipfile,argparse
from PIL import Image,ImageOps
from export_animation import validate
R=Path(__file__).resolve().parents[1]
c=json.loads((R/'catalog.json').read_text(encoding='utf-8'))
p=argparse.ArgumentParser();p.add_argument('--collection',default='boy-kippah');p.add_argument('--pack',type=int,default=1);a=p.parse_args()
siblings=[s for s in c['stickers'] if s['collection']==a.collection]
requested=siblings[(a.pack-1)*30:a.pack*30]
items=[s for s in requested if s['status']=='complete']
if len(items)!=len(requested):raise SystemExit('Complete the whole planned pack before packaging')
if not 3<=len(items)<=30:raise SystemExit('Pack requires 3–30 visually approved stickers')
pack_slug=f'{a.collection}-{a.pack:02d}'
folder=R/'dist'/pack_slug
for s in items:
    result=validate(R/s['output'])
    if not result['ok']:raise ValueError((s['id'],result))
with Image.open(R/items[0]['output']) as im:
    ImageOps.contain(im.convert('RGBA'),(96,96),Image.Resampling.LANCZOS).save(folder/'tray.png')
emoji={1:'👟',2:'🎉',3:'🤲',4:'👏',5:'🏆',6:'🤔',7:'🤷',8:'😋',9:'😴',10:'🥱',11:'😮',12:'😑',13:'😠',14:'😢',15:'😄',16:'🧘',17:'🤗',18:'🤗',19:'👏',20:'🥰',21:'⏳',22:'☕',23:'🧘',24:'❤️',25:'🌅',26:'🌙',27:'🍽️',28:'🛁',29:'🙏',30:'🧸'}
pack=dict(identifier=f'kido_{pack_slug.replace("-","_")}',name=f'Kido {a.collection} {a.pack}',publisher='Kido',tray_image_file='tray.png',image_data_version='1',animated_sticker_pack=True,stickers=[dict(image_file=Path(s['output']).name,emojis=[emoji.get(int(s['number']),'😊')],accessibility_text=f'A character expresses "{s["caption"] or s["id"]}" in Hebrew.') for s in items])
(folder/'contents.json').write_text(json.dumps({'sticker_packs':[pack]},ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(R/'dist'/f'kido-{pack_slug}.zip','w',zipfile.ZIP_DEFLATED) as z:
    for s in items:z.write(R/s['output'],f'{pack_slug}/{Path(s["output"]).name}')
    for name in ['tray.png','contents.json']:z.write(folder/name,f'{pack_slug}/{name}')
print('Packaged',len(items))
