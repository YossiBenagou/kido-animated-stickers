"""Encode approved RGBA frames as a WhatsApp animated WebP.

This performs only deterministic sizing/encoding, never creates animation poses.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image

def validate(path):
    path=Path(path)
    errors=[]
    with Image.open(path) as im:
        if im.size!=(512,512): errors.append('Canvas must be 512x512')
        if im.format!='WEBP': errors.append('Must be WebP')
        if getattr(im,'n_frames',1)<2: errors.append('Must be animated')
        duration=0; unique=set(); transparent=True
        for i in range(getattr(im,'n_frames',1)):
            im.seek(i); rgba=im.convert('RGBA'); im.load()
            ms=im.info.get('duration',0);duration+=ms
            if ms<8: errors.append(f'Frame {i} duration below 8 ms')
            unique.add(hashlib.sha256(rgba.tobytes()).hexdigest())
            transparent &= rgba.getchannel('A').getextrema()[0]==0
        if not transparent: errors.append('Every frame must have transparent background')
        if len(unique)<2: errors.append('Frames have no visible change')
        if duration>10000: errors.append('Animation exceeds 10 seconds')
        if im.info.get('loop',None)!=0: errors.append('Must loop indefinitely')
        count=getattr(im,'n_frames',1)
    if path.stat().st_size>500000: errors.append('File exceeds conservative 500 KB limit')
    return dict(ok=not errors,errors=errors,bytes=path.stat().st_size,frames=count,duration_ms=duration,distinct_frames=len(unique),transparent=transparent)

def encode(frames_dir, output, duration):
    files=sorted(Path(frames_dir).glob('*.png'))
    if len(files)<2: raise ValueError('At least two generated/approved PNG frames required')
    frames=[]
    for f in files:
        with Image.open(f) as im:
            if im.size!=(512,512): raise ValueError(f'{f}: expected 512x512')
            frames.append(im.convert('RGBA'))
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    for quality in [90,85,80,75,65]:
        frames[0].save(output,'WEBP',save_all=True,append_images=frames[1:],duration=duration,loop=0,quality=quality,method=4,minimize_size=True,background=(0,0,0,0))
        if output.stat().st_size<=500000:break
    result=validate(output)
    output.with_suffix('.validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    if not result['ok']:raise ValueError(result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('frames_dir',nargs='?');p.add_argument('output',nargs='?');p.add_argument('--duration',type=int,default=140);p.add_argument('--validate')
    a=p.parse_args()
    if a.validate:
        result=validate(a.validate);print(json.dumps(result));raise SystemExit(0 if result['ok'] else 1)
    if not a.frames_dir or not a.output:p.error('frames_dir and output required')
    print(json.dumps(encode(a.frames_dir,a.output,a.duration)))
