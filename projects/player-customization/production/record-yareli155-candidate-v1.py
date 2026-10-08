"""Record the directly observed fresh source and actual launch identity."""
from pathlib import Path
from datetime import datetime,timezone
import json,os
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
p=BASE.parent/'sources/game-candidates.json';j=read(p);review=read(BASE.parent/'planning/action-capacity-review-v3.json');candidate=review['additionalCandidate']
profile=j['additionalOfficialProfiles'];profile.setdefault('selected',[])
if not any(x.get('sourceVideoId')=='8eUfnQ8mWXs' for x in profile['selected']):
 profile['selected'].append(dict(candidate,acquisition='projects/player-customization/production/yareli155-acquisition-execution-v1.json',recentUseCheck='ExactID rg over projects, production and shared/publishing found only this newly-created candidate record; no prior selected use.',nativeActionApproved=False,footageQuotaApproved=False))
profile.update(reviewedAt=now(),next='Read this fresh official gameplay native source and selected exact intervals; no ratio or final pixel approval yet.');save(p,j)
launch=read(BASE/'yareli155-acquisition-execution-v1.session.json');sp=BASE/'yareli155-acquisition-execution-v1.json';s=read(sp)
assert launch['pid']==s['pid']==21388 and 'acquire-yareli155-v1.py' in launch['processIdentity']['CommandLine']
s.update(sessionId=launch['sessionId'],processIdentity=launch['processIdentity']);save(sp,s)
cp=read(BASE/'latest-checkpoint.json')
if cp['ownedJob']['pid']==launch['pid']:cp['ownedJob'].update(sessionId=launch['sessionId'],processIdentity=launch['processIdentity']);save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='player-customization')
if i['currentExecution']['pid']==launch['pid']:i['currentExecution'].update(sessionId=launch['sessionId'],processIdentity=launch['processIdentity'])
i.update(currentDuplicateContentRereview='projects/player-customization/production/current-lighting-project-duplicate-rereview-v1.json',currentDuplicateCheckPassed=True);q['updatedAt']=now();save(qp,q)
print(json.dumps({'candidateRecorded':True,'sessionId':launch['sessionId'],'pid':launch['pid'],'nativeApproved':False}))
