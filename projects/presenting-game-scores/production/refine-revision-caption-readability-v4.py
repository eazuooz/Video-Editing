"""Retain all literal bilingual text; merge only short adjacent English fragments."""
from pathlib import Path
from datetime import datetime,timezone
import json,copy,hashlib
P=Path(__file__).parent;B=P/'revision-balatro60-v2';ROOT=P.parents[2]
src=B/'caption-candidate-v3/captions.json';dst=B/'caption-candidate-v4';assert not dst.exists()
j=json.loads(src.read_text('utf-8'));old=copy.deepcopy(j);rows=j['en'];changes=[];i=0
while i<len(rows):
 r=rows[i]
 if r['endSeconds']-r['startSeconds']>=1:i+=1;continue
 assert i>0;prev=rows[i-1]
 assert (prev['scene'],prev['paragraph'],prev['chunk'],prev['placement'])==(r['scene'],r['paragraph'],r['chunk'],r['placement'])
 assert abs(prev['endSeconds']-r['startSeconds'])<.001
 text=' '.join((prev['en']+' '+r['en']).split());lines=[];cur=[]
 for w in text.split():
  if cur and len(' '.join(cur+[w]))>78:lines.append(' '.join(cur));cur=[]
  cur.append(w)
 if cur:lines.append(' '.join(cur))
 assert len(lines)<=2
 changes.append(dict(scene=r['scene'],paragraph=r['paragraph'],oldFragment=r['en'],oldFragmentSeconds=r['endSeconds']-r['startSeconds'],retainedText='\n'.join(lines),startSeconds=prev['startSeconds'],endSeconds=r['endSeconds']))
 prev.update(en='\n'.join(lines),endSeconds=r['endSeconds']);rows.pop(i)
for i,r in enumerate(rows,1):r['index']=i
norm=lambda s:''.join(s.split())
for p in j['paragraphs']:
 for lang in ('ko','en'):assert norm(''.join(r[lang] for r in j[lang] if r['scene']==p['scene'] and r['paragraph']==p['paragraph']))==norm(p[lang])
assert j['ko']==old['ko'] and changes
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
j.update(schemaVersion=4,preparedAt=datetime.now(timezone.utc).isoformat(),previousCandidate=dict(path=src.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),all175Ko77EnCueTextsDirectlyRead=True),englishReadabilityChanges=changes,enCueCount=len(rows),allCurrentCueTextsDirectlyRead=False)
dst.mkdir()
for lang in ('ko','en'):(dst/f'candidate.{lang}.srt').write_text('\n\n'.join(f'{r["index"]}\n{stamp(r["startSeconds"])} --> {stamp(r["endSeconds"])}\n{r[lang]}' for r in j[lang])+'\n','utf-8')
(dst/'captions.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(ko=len(j['ko']),en=len(rows),changes=changes,preparedOnly=True),ensure_ascii=False))
