"""Compare decoded master gameplay pixels to native source at mapped timestamps.

Detects missing/wrong/frozen inserts; does not prove whole-video teaching quality.
"""
from pathlib import Path
import json,sys,subprocess,hashlib,io
from PIL import Image,ImageChops,ImageStat
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def frame(p,t,final=False):
 vf=('crop=1280:720:0:130,' if final else '')+'scale=256:144'
 data=subprocess.check_output(['ffmpeg','-v','error','-nostdin','-ss',str(t),'-i',str(R/p),'-frames:v','1','-vf',vf,'-f','image2pipe','-vcodec','png','pipe:1'])
 return Image.open(io.BytesIO(data)).convert('RGB')
def mae(a,b):return sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
for ep in sys.argv[1:]:
 pp=V/(ep+'-plan.json');p=read(pp);H=R/'projects'/p['slug']/'production'/p['revision'];out=read(H/'outputs.json');patches=read(H/'patches.json')['patches'];master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'));dst=H/'native-frame-evidence.json'
 assert out['planSha256']==hashlib.sha256(pp.read_bytes()).hexdigest()
 if dst.exists() and read(dst)['masterSha256']==master['sha256'] and read(dst).get('allSourceIntervalsPresentAtSampledTimes'):
  print(ep,'native frame evidence already current',flush=True);continue
 rows=[]
 for q,placed in zip(p['patches'],patches):
  assert q.get('key',q['scene'])==placed['key'] and len(q['segments'])==1 and q['segments'][0]['kind']=='motion'
  seg=q['segments'][0];times=[.5,q['duration']*.55,q['duration']-.5];native=[];final=[];errors=[];rounding=[]
  for t in times:
   a=frame(p['sources'][q['source']]['path'],seg['in']+t);b=frame(master['path'],placed['start']+t,True);err=mae(a,b);delta=0
   if err>15:
    for off in [-1/30,-1/60,1/60,1/30]:
     other=frame(p['sources'][q['source']]['path'],seg['in']+t+off);e=mae(other,b)
     if e<err:a=other;err=e;delta=off
   native.append(a);final.append(b);errors.append(round(err,3));rounding.append(delta)
  row=dict(key=placed['key'],masterTimes=[round(placed['start']+t,4) for t in times],sourceTimes=[round(seg['in']+t,4) for t in times],source=p['sources'][q['source']]['path'],pixelMeanAbsoluteError=errors,sourceChange=round(mae(native[0],native[-1]),3),masterChange=round(mae(final[0],final[-1]),3))
  row['sourceFrameRoundingSeconds']=rounding
  row['reviewFlag']=max(errors)>15 or (row['sourceChange']>3 and row['masterChange']<1)
  rows.append(row)
 evidence=dict(master=master['path'],masterSha256=master['sha256'],method='Three decoded game-region frames per actual insert versus timestamp-matched native source; MAE on256x144 RGB including editorial guide differences.',noRetimedSegments=True,noFreezePaddingSegments=True,allSourceIntervalsPresentAtSampledTimes=not any(x['reviewFlag'] for x in rows),continuousPlayback=False,rows=rows)
 dst.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(ep,'native-frame flags',[x['key'] for x in rows if x['reviewFlag']],flush=True)
