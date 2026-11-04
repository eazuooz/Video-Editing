"""Recheck observed issues only; frozen source and sparse samples are QA, not finals."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
S=P/'production/unity-staging'
R=S/'local-preflight-v3'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if R.exists():raise FileExistsError('Prior evidence must be preserved')
R.mkdir()
scenes=read(P/'planning/scene-bindings.json')['scenes']
marker=read(S/'LocalUnity-v6/M21_SANDBOX.json')
jobs=[]
for name,index in [('math-reflect',10),('grid',15),('fresnel',35),('anisotropy',36),('baked-uv',70),('vertex',71),('sh',73),('baked',74),('mixed',75),('environment',77)]:
    cue=dict(scenes[index]['cue']);cue.update(id='m21-preflight-v3-'+name,duration=8,cardSeconds=1)
    cue['stepTimes']=[0,1.5,3,4.5,6]
    save(R/(name+'.cue.json'),cue)
    job={'id':cue['id'],'command':'preflight','expectedFingerprint':marker['fingerprint'],'cueFile':str(R/(name+'.cue.json')),'output':str(R/name),'frames':480,'sampleFrames':[120,420]}
    save(R/(name+'.job.json'),job);jobs.append(str(R/(name+'.job.json')))
save(R/'queue.json',{'sandbox':str(S/'LocalUnity-v6'),'fingerprint':marker['fingerprint'],'unity':'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','jobs':jobs,'purpose':'Finite ten image preflights: correct term chips, preserve font meshes, left calculation layout, real lightmap texture. No final media or next-video job.'})
print(str(R))
