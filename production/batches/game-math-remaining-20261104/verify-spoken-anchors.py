"""Verify literal cue offsets following wording changes; no inferred timestamps."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scope=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert scope['productionAllowedNow']
tot=0;fix=0
for ep in read(B/'batch.json')['items'][1:]:
 p=R/'projects'/ep['slug'];assert p.name in scope['projectSlugs'];bp=p/'planning/scene-bindings.json';b=read(bp)
 script=read(p/'script/narration.ko.json');affected=[]
 assert [s['id'] for s in b['scenes']]==[s['id'] for s in script['scenes']]
 for row,n in zip(b['scenes'],script['scenes']):
  assert row['speech']==n['lines'][0]
  for a in row.get('speechPhaseAnchors',[]):
   tot+=1
   if row['speech'][a['character']:].startswith(a['phrase']):continue
   assert row['speech'].count(a['phrase'])==1,(p.name,row['id'],a['phrase'])
   pos=row['speech'].index(a['phrase']);affected.append(dict(scene=row['id'],phrase=a['phrase'],old=a['character'],new=pos));a['character']=pos
 if affected:
  before=sha(bp);save(bp,b);after=sha(bp)
  pp=p/'planning/production-plan.json';plan=read(pp);plan['sceneBindingsSha256']=after
  plan.setdefault('afterWordingChangeCueChecks',[]).append(dict(beforeSha256=before,afterSha256=after,changes=affected,narrationChanged=False,positionsAreNotTimestamps=True))
  save(pp,plan);fix+=len(affected)
print(tot,'literal animation anchors checked;',fix,'corrected unique offsets. No speech or scene times changed.')
