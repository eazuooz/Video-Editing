"""Prepare five representative font regression jobs without starting Unity."""
from pathlib import Path
import json
S=Path(__file__).resolve().parent;W=S/'local-preflight-v9'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not W.exists(),'Preserve existing regression evidence';W.mkdir()
record=read(S/'sandbox-preparation.json');jobs=[]
for version,name in [('v4','grid'),('v4','vertex'),('v4','mixed'),('v5','sh'),('v5','environment')]:
    prior=read(S/('local-preflight-'+version)/(name+'.job.json'));cue=read(Path(prior['cueFile']))
    sid='m21-preflight-v9-'+name;cue['id']=sid;save(W/(name+'.cue.json'),cue)
    prior.update(id=sid,expectedFingerprint=record['fingerprint'],cueFile=str(W/(name+'.cue.json')),output=str(W/name))
    if name in ['sh','environment']:prior['sampleFrames']=[0,120,240,420]
    job=W/(name+'.job.json');save(job,prior);jobs.append(str(job))
save(W/'queue.json',{'sandbox':record['sandbox'],'fingerprint':record['fingerprint'],'unity':'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','jobs':jobs,'purpose':'Windows OS raster label regression on five actual scenes; previous math/geometry unchanged.'})
print('Five font regression jobs prepared; no renderer started.')
