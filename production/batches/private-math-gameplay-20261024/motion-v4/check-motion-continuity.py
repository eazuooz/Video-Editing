"""Screen for added frozen runs in every selected native gameplay interval.

Samples at four frames per second; not a substitute for continuous viewing.
"""
from pathlib import Path
import json,subprocess,sys,hashlib
import numpy as np
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def motion(path,start,duration,final=False):
 vf=('crop=1280:720:0:130,' if final else '')+'fps=4,scale=64:36,format=gray'
 data=subprocess.check_output(['ffmpeg','-v','error','-nostdin','-ss',str(start),'-i',str(R/path),'-t',str(duration),'-vf',vf,'-an','-f','rawvideo','pipe:1'])
 frames=np.frombuffer(data,np.uint8).reshape(-1,36,64).astype(np.float32)
 assert len(frames)>=max(2,int(duration*4)-2)
 change=np.abs(np.diff(frames,axis=0)).mean(axis=(1,2));run=best=0
 for d in change:
  run=run+1 if d<.10 else 0;best=max(best,run)
 return dict(samples=len(frames),maxNearStaticSeconds=round(best/4,2),meanFrameChange=round(float(change.mean()),3),movingTransitions=int((change>=.10).sum()))
for ep in sys.argv[1:]:
 pp=V/(ep+'-plan.json');p=read(pp);H=R/'projects'/p['slug']/'production'/p['revision'];out=read(H/'outputs.json')
 assert out['planSha256']==hashlib.sha256(pp.read_bytes()).hexdigest()
 master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'));dst=H/'motion-continuity.json'
 if dst.exists() and read(dst)['masterSha256']==master['sha256']:
  print(ep,'existing sampled motion evidence',flush=True);continue
 rows=[]
 for q,a in zip(p['patches'],read(H/'patches.json')['patches']):
  seg=q['segments'][0];assert len(q['segments'])==1 and seg['kind']=='motion'
  # Exclude only the deliberate 150/180ms edit crossfades.
  duration=q['duration']-.4
  source=motion(p['sources'][q['source']]['path'],seg['in']+.2,duration)
  final=motion(master['path'],a['start']+.2,duration,True)
  flag=final['maxNearStaticSeconds']>max(1.5,source['maxNearStaticSeconds']+.5)
  rows.append(dict(key=a['key'],source=source,final=final,addedFreezeFlag=flag))
 d=dict(masterSha256=master['sha256'],method='4fps64x36 grayscale motion in game-region only, source-native interval versus final; near-static MAE<0.10. Crossfades excluded.',rows=rows,addedFreezeFlags=[x['key'] for x in rows if x['addedFreezeFlag']],nativeContinuousPlayback=False)
 dst.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(ep,'sampled added-freeze flags',d['addedFreezeFlags'],flush=True)
