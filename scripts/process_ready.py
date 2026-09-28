"""Assemble saved strips that have not yet been processed; never generates images."""
import json
from assemble_sticker import ROOT,assemble
c=json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
ready=[s['id'] for s in c['stickers'] if s['status']=='pending' and (ROOT/'animations'/s['id']/'source-strip.png').exists()]
for identifier in ready:assemble(identifier)
print('Processed:',len(ready))
