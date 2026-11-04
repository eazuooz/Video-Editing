"""Verify the three observed dynamic-text failures after mesh refresh/warm-up."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];S=P/'production/unity-staging';R=S/'local-preflight-v4'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if R.exists():raise FileExistsError('Preserve previous evidence')
R.mkdir();marker=read(S/'LocalUnity-v6/M21_SANDBOX.json');jobs=[]
for name in ['grid','vertex','mixed']:
    cue=read(S/'local-preflight-v3'/(name+'.cue.json'));cue['id']='m21-preflight-v4-'+name
    save(R/(name+'.cue.json'),cue)
    job={'id':cue['id'],'command':'preflight','expectedFingerprint':marker['fingerprint'],'cueFile':str(R/(name+'.cue.json')),'output':str(R/name),'frames':480,'sampleFrames':[120,420]}
    save(R/(name+'.job.json'),job);jobs.append(str(R/(name+'.job.json')))
save(R/'queue.json',{'sandbox':str(S/'LocalUnity-v6'),'fingerprint':marker['fingerprint'],'unity':'C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','jobs':jobs,'purpose':'Three sparse-frame checks of dynamic font meshes and mixed-lighting label. No final media.'})
