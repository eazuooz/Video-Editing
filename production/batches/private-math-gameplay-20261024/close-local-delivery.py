"""Close only the explicitly scoped revision after master-bound visual/technical QA."""
from pathlib import Path
import json,datetime
B=Path(__file__).resolve().parent;R=B.parents[2]
def rd(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
c=rd(B/'checkpoint.json');assert c['ready']==18 and c['encoded']==15 and c['retained']==3
rows=[]
for e in c['entries']:
 h=R/'projects'/e['slug']/'production/gameplay-v3';o=rd(h/'outputs.json');v=rd(h/'visual-review.json');t=rd(h/'technical-qa.json');s=rd(h/'semantic-review.json')
 cap=next(x for x in o['outputs'] if x['path'].endswith('.captioned.mp4'))
 assert cap['sha256']==v['captionedSha256']==s['captionedSha256'] and s['actualIntervalCount']>=3
 assert len(o['outputs'])==4
 for f in o['outputs']:assert (R/f['path']).is_file() and (R/f['path']).stat().st_size==f['bytes']
 for x in t['checks']:
  if x['path'].endswith('.mp4'):assert (x['width'],x['height'],x['fps'])==(1920,1080,60)
 rows.append(dict(id=e['id'],title=e['title'],index=f"output/{e['slug']}-gameplay-v3/index.html",outputs=o['outputs'],exampleCount=s['actualIntervalCount'],retained=o.get('retainedByteIdentical',False),technicalQa=str((h/'technical-qa.json').relative_to(R)),visualQa=str((h/'visual-review.json').relative_to(R)),semanticQa=str((h/'semantic-review.json').relative_to(R)),humanReview='pending',wholeListening=False))
now=datetime.datetime.now().astimezone().isoformat()
save(B/'delivery-manifest.json',dict(completedAt=now,status='local-human-review-pending',entries=rows,modified=15,retained=3,outputFiles=72,exampleIntervals=sum(x['exampleCount'] for x in rows),wholeListening=False,platformChanges=False))
control=R/'shared/publishing/video-production-control.json';d=rd(control);scope=d['scopedBatchAuthorizations'][B.name]
scope.update(status='local-review-ready',completedAt=now,renderAuthorized=False,deliveryManifest=str((B/'delivery-manifest.json').relative_to(R)),humanReview='pending',wholeListening=False)
save(control,d)
a=rd(B/'authorization.json');a.update(status='local-review-ready',completedAt=now,renderAuthorized=False,humanReview='pending',wholeListening=False);save(B/'authorization.json',a)
legacy=R/'output/private-game-math-polish/index.html'
if legacy.exists():
 text=legacy.read_text('utf-8-sig');mark='<!-- LATEST-GAMEPLAY-20261024 -->'
 if mark not in text:
  banner=mark+'<aside style="padding:20px;background:#173728;color:#fff;font:18px/1.5 system-ui"><b>최신 게임 장면·기즈모 수정본 18편</b> · <a style="color:#ffd773" href="../private-math-gameplay-20261024/index.html">최신 검수표 열기</a><br>아래 목록은 보존 중인 이전 버전입니다.</aside>'
  if '<body' in text:
   pos=text.index('>',text.index('<body'))+1;text=text[:pos]+banner+text[pos:]
  else:text+=banner
  legacy.write_text(text,encoding='utf8')
print('18 local deliveries closed for human review; 72 files; no platform changes')
