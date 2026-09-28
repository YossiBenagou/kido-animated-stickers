from pathlib import Path
from collections import Counter
import json
R=Path(__file__).resolve().parents[1]
c=json.loads((R/'catalog.json').read_text(encoding='utf-8'))['stickers']
lines=['# מצב הפקת הסטיקרים','','היצירה באמצעות imagegen המובנה בלבד, ללא API בתשלום או הוצאה נוספת.','', '| אוסף | הושלמו | בבדיקה | ממתינים |','|---|---:|---:|---:|']
for group in dict.fromkeys(s['collection'] for s in c):
    count=Counter(s['status'] for s in c if s['collection']==group)
    lines.append(f'| {group} | {count["complete"]} | {count["awaiting_visual_qa"]+count["needs_visual_repair"]} | {count["pending"]} |')
lines+=['','## חבילות להורדה','']
for p in sorted((R/'dist').glob('*.zip')):lines.append(f'- [{p.name}](../{p.relative_to(R).as_posix()})')
lines+=['','## המשך עבודה','','1. לקרוא את catalog.json ולבחור את הסטיקר הבא שלא הושלם.','2. להמשיך יצירת תנוחות דרך hatch-pet / imagegen המובנה.','3. להריץ assemble_sticker.py עבור המזהה, לבדוק דף מגע ורצף, לשמור דוח QA.','4. להריץ accept_qa.py, package_pack.py עם אוסף ומספר חבילה, build_gallery.py ו־update_progress.py.','5. לבצע commit ו־push לאחר כל חבילה.','','ייבוא בטלפון עצמו עדיין לא נבדק.']
(R/'docs/progress.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(Counter(s['status'] for s in c))
