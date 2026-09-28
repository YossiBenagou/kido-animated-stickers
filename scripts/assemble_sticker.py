"""Deterministic hatch-pet extraction + original caption + WhatsApp export."""
from pathlib import Path
import argparse,json
from PIL import Image, ImageDraw, ImageOps, ImageChops
from vendor.hatch_extract import component_frame_groups,component_group_image,connected_components
from export_animation import encode

ROOT=Path(__file__).resolve().parents[1]
def assemble(identifier):
    catalog=json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
    item=next(x for x in catalog['stickers'] if x['id']==identifier)
    folder=ROOT/'animations'/identifier
    with Image.open(folder/'source-strip.png') as im: strip=im.convert('RGBA')
    groups=component_frame_groups(strip,6)
    if groups is None or len(groups)!=6:raise ValueError('Expected six complete character groups')
    sprites=[component_group_image(strip,g,padding=3) for g in groups]
    bottoms=[max(c['bbox'][3] for c in g) for g in groups]
    # A shared scale preserves relative anatomy and intended pose changes.
    scale=min(440/max(x.width for x in sprites),340/max(x.height for x in sprites))
    with Image.open(ROOT/item['reference']) as src:
        src=src.convert('RGBA')
        cutoff={'boy-kippah-05':.210,'boy-kippah-08':.180,'boy-kippah-25':.200,'boy-kippah-37':.175}.get(identifier,.225)
        raw_crops={'boy-kippah-55':(115,114,909,306),'girl-07':(164,119,868,255)}
        if identifier in raw_crops:
            left,top,right,bottom=raw_crops[identifier]
            caption=src.crop((round(src.width*left/1024),round(src.height*top/1024),round(src.width*right/1024),round(src.height*bottom/1024)))
        else:
            caption=src.crop((0,0,src.width,round(src.height*cutoff)))
        parts=connected_components(caption)
        if parts:caption=component_group_image(caption,[max(parts,key=lambda p:p['area'])],padding=0)
        box=caption.getbbox()
        if box:caption=caption.crop(box)
        caption=ImageOps.contain(caption,(480,126),Image.Resampling.LANCZOS)
        mask=Image.new('L',caption.size)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,caption.width-1,caption.height-1),radius=caption.height//2,fill=255)
        caption.putalpha(ImageChops.multiply(caption.getchannel('A'),mask))
    frame_dir=folder/'frames';frame_dir.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(6*256,552),'#e8e7e3');draw=ImageDraw.Draw(sheet)
    frame_paths=[]
    for i,sprite in enumerate(sprites):
        sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.LANCZOS)
        frame=Image.new('RGBA',(512,512))
        frame.alpha_composite(caption,((512-caption.width)//2,14))
        lift=round((max(bottoms)-bottoms[i])*scale)
        frame.alpha_composite(sprite,((512-sprite.width)//2,490-sprite.height-lift))
        p=frame_dir/f'{i:02d}.png';frame.save(p);frame_paths.append(p.relative_to(ROOT).as_posix())
        small=frame.resize((256,256),Image.Resampling.LANCZOS)
        for row,color in enumerate(('#ece9e2','#252932')):
            tile=Image.new('RGBA',(256,256),color);tile.alpha_composite(small)
            sheet.paste(tile.convert('RGB'),(i*256,row*276))
        draw.text((i*256+6,260),str(i),fill='black')
    sheet.save(folder/'contact-sheet.jpg')
    siblings=[s['id'] for s in catalog['stickers'] if s['collection']==item['collection']]
    pack_index=siblings.index(identifier)//30+1
    out=ROOT/'dist'/f'{item["collection"]}-{pack_index:02d}'/f'{item["number"]}.webp'
    duration=450 if item['number'] in {'16','21','23','26'} else 240 if item['number'] in {'09','10','12','14','17','30'} else 180
    result=encode(frame_dir,out,duration)
    item.update(frames=frame_paths,output=out.relative_to(ROOT).as_posix(),status='awaiting_visual_qa')
    (ROOT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'qa.json').write_text(json.dumps(dict(technical=result,visual='pending',method='hatch-pet connected components; common scale; preserved original caption'),indent=2),encoding='utf-8')
    print(identifier,result)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('identifiers',nargs='+');a=p.parse_args()
    for identifier in a.identifiers:assemble(identifier)
