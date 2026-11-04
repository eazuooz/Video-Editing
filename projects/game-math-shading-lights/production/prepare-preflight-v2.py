"""Freeze actual mapped cues for a finite image QA run, never final playback."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
S=P/'production/unity-staging'
R=S/'local-preflight-v2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if R.exists():raise FileExistsError('Keep previous preflight evidence')
R.mkdir()
scenes=read(P/'planning/scene-bindings.json')['scenes']
marker=read(S/'LocalUnity-v5/M21_SANDBOX.json')
jobs=[]
for name,index in [('math-reflect',10),('grid',15),('cosine',19),('fresnel',35),('anisotropy',36),('triangle',40),('baked-uv',70),('vertex',71),('sh',73),('baked',74),('mixed',75),('environment',77)]:
    cue=dict(scenes[index]['cue']);cue.update(id='m21-preflight-v2-'+name,duration=8,cardSeconds=1)
    # Preview timings are explicitly not final spoken-word alignment.
    cue['stepTimes']=[0,1.5,3,4.5,6]
    save(R/(name+'.cue.json'),cue)
    job={'id':cue['id'],'command':'preflight','expectedFingerprint':marker['fingerprint'],'cueFile':str(R/(name+'.cue.json')),'output':str(R/name),'frames':480,'sampleFrames':[120,420]}
    save(R/(name+'.job.json'),job);jobs.append(str(R/(name+'.job.json')))
save(R/'queue.json',{'sandbox':str(S/'LocalUnity-v5'),'fingerprint':marker['fingerprint'],'unity':'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','jobs':jobs,'purpose':'Finite twelve image preflights after observed layout fixes; no final media or next-video job'})
print(str(R))
