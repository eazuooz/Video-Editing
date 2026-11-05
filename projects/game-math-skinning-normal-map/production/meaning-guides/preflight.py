from pathlib import Path
import json
from prepare import P,read,save
s=P/'production/unity-staging';mk=read(s/'sandbox-preparation.json');out=s/'local-preflight-meaning-v1';assert not out.exists();out.mkdir()
plan=read(P/'planning/scene-bindings.json');q=read(s/'local-preflight-v5/queue.json')
q.update(sandbox=mk['sandbox'],fingerprint=mk['fingerprint'],scope='M22 purpose/surface anchors verified against the same project used for final capture',jobs=[])
for i in (5,20,28):
 id=f'{i:03}';shot=dict(plan['scenes'][i]['shot'],durationSeconds=8,stepSeconds=[],stepPositions=[])
 save(out/(id+'.shot.json'),shot);job=dict(read(s/'local-preflight-v5/006.job.json'),id='m22-guides-'+id,output=str(out/id),shotFile=str(out/(id+'.shot.json')),expectedFingerprint=mk['fingerprint'],sampleFrames=[90,230,420])
 path=out/(id+'.job.json');save(path,job);q['jobs'].append(str(path))
save(out/'queue.json',q)

