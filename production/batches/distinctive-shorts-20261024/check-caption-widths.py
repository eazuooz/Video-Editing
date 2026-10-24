from pathlib import Path
import json
from PIL import ImageFont
R=Path(__file__).resolve().parents[3];font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',60)
for p in R.glob('projects/shorts-*/script/clauses.json'):
 if p.parts[-3] not in json.loads((Path(__file__).parent/'batch.json').read_text(encoding='utf8'))['authorization']['slugs']:continue
 for c in json.loads(p.read_text(encoding='utf8'))['clauses']:
  for lang in ['ko','en']:
   rows=[];line=''
   for w in c[lang].split():
    cand=(line+' '+w).strip()
    if line and font.getlength(cand)>796:rows.append(line);line=w
    else:line=cand
   if line:rows.append(line)
   if len(rows)>2:print(p.parts[-3],c['id'],lang,repr(c[lang]))
