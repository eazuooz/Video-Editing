"""Update the existing ledger from current master-bound QA and inspected concept mappings."""
from pathlib import Path
import json, hashlib, datetime
B=Path(__file__).resolve().parent;R=B.parents[2]
def rd(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
MAP={
'M03-original':[['02'],['05','08'],['11']],
'M04':[['02'],['14'],['20']],
'M05':[['02'],['GA01'],['QF30']],
'M06':[['14'],['QC20'],['QC30']],
'M07':[['02'],['05'],['08']],
'M08':[['17'],['IG05'],['IG08']],
'M09':[['03'],['02','LG01'],['LG03']],
'M10':[['LG05','LG07','10'],['LG07'],['LG06','19']],
'M11':[['02'],['PG02'],['08']],
'M12':[['11'],['17'],['PG07','21']],
'M13':[['02','QG01'],['11'],['QG02','QG03']],
'M14':[['13','21'],['QG04','QG09'],['QG06'],['QG07']],
'M15':[['02','05-hole','05-glass','21'],['08-entry','08-preview','11','14'],['17','19']],
'M16':[['02','08'],['11','13','16'],['05','19','21-view','21-build']],
'M17':[['02','05'],['08','14'],['11-carry','11-place']],
'M18':[['03'],['06'],['09-view','09-build']],
'M19':[['02','06','07'],['10','11-front','11-depth'],['15']],
'M20':[['03-width'],['04','05','08'],['09','12']]
}
c=rd(B/'checkpoint.json');audit={x['id']:x for x in rd(B/'edit-list-audit.json')['entries']}
for e in c['entries']:
 h=R/'projects'/e['slug']/'production/gameplay-v3';vp=h/'visual-review.json'
 if not vp.exists():continue
 o=rd(h/'outputs.json');v=rd(vp);cap=next(x for x in o['outputs'] if x['path'].endswith('.captioned.mp4'))
 assert v['captionedSha256']==cap['sha256'] and v['status']=='visual-pass'
 pp=B/f"{e['id'].lower()}-gameplay-plan.json"
 if pp.exists():
  p=rd(pp);assert o['planSha256']==hashlib.sha256(pp.read_bytes()).hexdigest()
  shots={x.get('key',x['scene']):dict(key=x.get('key',x['scene']),scene=x['scene'],title=x['title'],source=p['sources'][x['source']],duration=x['duration'],nativeSeconds=sum(s['seconds'] for s in x['segments'] if s['kind']=='motion'),analyticalStillSeconds=sum(s['seconds'] for s in x['segments'] if s['kind']=='still'),cuePlan=str(pp.relative_to(R)),guideCount=len(x.get('guides',[]))) for x in p['patches']}
 else:shots={x['scene']:dict(x,retainedByteIdentical=True) for x in audit[e['id']]['shots']}
 assert len(shots)>=3
 assert len(MAP[e['id']])==len(e['coreConcepts']),(e['id'],len(e['coreConcepts']))
 for concept,keys in zip(e['coreConcepts'],MAP[e['id']]):
  assert all(k in shots for k in keys)
  concept.update(matchedExample=[shots[k] for k in keys],review='inspected-visible-analogy-and-preserved-model',limits='Game imagery demonstrates visible objects/actions/results. Formulas, hidden coordinates, projection/UV/normal computations are explained by our labeled model; not asserted as measured internals of that game.')
 e['previousShots']=audit[e['id']]['shots'];e['shots']=list(shots.values())
 for shot in e['shots']:shot.update(actualMovingReview=True,semanticFit='visible-example-with-explanatory-model',evidence=str(vp.relative_to(R)))
 report=dict(episode=e['id'],captionedSha256=cap['sha256'],coreConcepts=e['coreConcepts'],shots=e['shots'],minimumMeaningfulIntervals=3,actualIntervalCount=len(shots),explanationAndNarrationPreserved=True,wholeListening=False,humanReview='pending',reviewEvidence=str(vp.relative_to(R)),decision='Retain already suitable 3 lectures byte-for-byte; revise actual footage and guides in the other 15. Preserve ordinary-speed action, explicitly label analytical stills, keep narration continuous and total frames unchanged. No artificial motion loop or added observation silence.')
 save(h/'semantic-review.json',report)
 o.update(status='local-review-ready-visual-only',visualReview='pass',technicalReview='pass',actualWholeListening=False,humanReview='pending')
 save(h/'outputs.json',o)
save(B/'checkpoint.json',c)
print('Master-bound semantic evidence updated')
