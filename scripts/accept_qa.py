"""Apply explicit independent visual verdicts after technical revalidation."""
from pathlib import Path
import json
from export_animation import validate
R=Path(__file__).resolve().parents[1]
c=json.loads((R/'catalog.json').read_text(encoding='utf-8'))
verdicts={}
for file in sorted((R/'docs').glob('visual-qa-*.json')):
    for row in json.loads(file.read_text(encoding='utf-8'))['stickers']:verdicts[row['id']]=row
for verdict in verdicts.values():
    item=next(s for s in c['stickers'] if s['id']==verdict['id'])
    if verdict['verdict']=='pass':
        report=validate(R/item['output'])
        if not report['ok']:raise ValueError((item['id'],report))
        item['status']='complete'
    else:item['status']='needs_visual_repair'
    path=R/'animations'/item['id']/'qa.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    data['visual']=verdict
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'catalog.json').write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
print('Complete:',sum(s['status']=='complete' for s in c['stickers']))
