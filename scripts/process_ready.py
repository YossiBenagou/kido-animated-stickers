"""Assemble saved strips that have not yet been processed; never generates images."""
import json
from assemble_sticker import ROOT,assemble
c=json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
ready=[s['id'] for s in c['stickers'] if s['status']=='pending' and (ROOT/'animations'/s['id']/'source-strip.png').exists()]
failed=[]
for identifier in ready:
    try:assemble(identifier)
    except ValueError as error:
        failed.append(identifier)
        print('Needs repair:',identifier,str(error))
        latest=json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
        item=next(s for s in latest['stickers'] if s['id']==identifier)
        item['status']='needs_visual_repair'
        (ROOT/'catalog.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2),encoding='utf-8')
        (ROOT/'animations'/identifier/'qa.json').write_text(json.dumps({'technical':{'ok':False,'errors':[str(error)]},'visual':'pending'},indent=2),encoding='utf-8')
print('Processed:',len(ready)-len(failed))
if failed:raise SystemExit('Unprocessed: '+', '.join(failed))
