"""Inspect the four removed-passage joins without replaying unchanged scene work."""
from pathlib import Path
import json,subprocess,math
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';D=P/'production/reference-preserving-v2';B=P/'production/local/reference-preserving-v2/edit';O=B/'original-deletion-v4';Q=O/'qa';Q.mkdir(exist_ok=True);plan=json.loads((D/'original-deletion-v4-plan.json').read_text(encoding='utf8'));rows=json.loads((O/'caption-tracks.json').read_text(encoding='utf8'))
voice,sr=sf.read(O/'narration-stem.wav',dtype='float32',always_2d=True);mix,_=sf.read(O/'final-mix.wav',dtype='float32',always_2d=True)
vpath=O/'game-reward-planning-v2-clean.mp4';raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(vpath),'-vn','-af','pan=mono|c0=0.5*c0+0.5*c1','-ar','48000','-f','f32le','-']);encoded=np.frombuffer(raw,dtype='<f4');v=voice.mean(axis=1);mask=np.zeros(min(len(v),len(encoded)),bool)
for row in rows:mask[max(0,int(row['start']*sr)):min(len(mask),int(row['end']*sr))]=True
win=round(.4*sr);hop=round(.1*sr);pos=np.arange(0,len(mask)-win+1,hop);times=(pos+win/2)/sr;cov=np.r_[0,np.cumsum(mask,dtype=np.int64)];active=(cov[pos+win]-cov[pos])>=.3*win
def db(a):
 c=np.r_[0,np.cumsum(a.astype('float64')**2)];return 10*np.log10(np.maximum((c[pos+win]-c[pos])/win,1e-14))
vd,ed=db(v),db(encoded);levels=[];points=[]
for i,x in enumerate(plan['deletions']):
 t=x['newJoinFrame']/60
 for side,a,b in [('before',t-3,t-.02),('after',t+.02,t+3)]:
  use=active&(times>=a)&(times<=b);med=float(np.median(vd[use]));delta=float(np.median(ed[use]-vd[use]));levels.append({'join':i+1,'scene':x['scene'],'side':side,'from':a,'to':b,'stemSpeechMedianDbfs':med,'encodedMinusStemDb':delta,'speechWindows':int(use.sum())})
 for dt in [-.25,-1/60,1/60,.3,1.2]:points.append({'join':i+1,'scene':x['scene'],'time':t+dt,'offset':dt})
 for j,delta in enumerate([-.25,.25]):
  sourceTime=(x['startFrame'] if delta<0 else x['endFrame'])/60+delta;dst=Q/f'baseline-join{i+1}-{j}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(sourceTime),'-i',str(B/'game-reward-planning-v2-clean.mp4'),'-frames:v','1',str(dst)],check=True)
for i,p in enumerate(points):
 dst=Q/f'{i:02}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(p['time']),'-i',str(O/'game-reward-planning-v2-captioned.mp4'),'-frames:v','1',str(dst)],check=True);p['frame']=dst.relative_to(R).as_posix()
for page in range(4):
 group=points[page*5:(page+1)*5];sheet=Image.new('RGB',(1920,1770),(235,235,235));draw=ImageDraw.Draw(sheet)
 for n,p in enumerate(group):
  im=Image.open(R/p['frame']).resize((960,540));x=n%2*960;y=n//2*590;sheet.paste(im,(x,y));draw.text((x+8,y+548),f"join {p['join']} t={p['time']:.3f} offset={p['offset']:.3f}",fill='black')
 sheet.save(Q/f'contact-{page:02}.jpg',quality=92)
mobile=Image.new('RGB',(1500,240),(220,220,220))
for i in range(4):mobile.paste(Image.open(R/points[i*5+4]['frame']).resize((375,211),Image.Resampling.LANCZOS),(375*i,0))
mobile.save(Q/'mobile.jpg',quality=94)
flags=[x for x in levels if x['encodedMinusStemDb']< -1.5 or x['encodedMinusStemDb']>3]
for i in range(4):
 pair=levels[i*2:(i+1)*2]
 if abs(pair[1]['stemSpeechMedianDbfs']-pair[0]['stemSpeechMedianDbfs'])>5:flags.append({'join':i+1,'reason':'adjacent speech median difference exceeds5dB'})
report={'frames':points,'captionCount':len(rows),'directPixelReview':'pending','joinAudio':levels,'flaggedRanges':flags,'unchangedAudioEvidence':'deletion-evidence.json: retained samples identical outside millisecond fades','retainedVisualEvidence':'Original v2 reviewed source/cut/annotation input retained; only selected time intervals removed','humanListening':'pending user review'};(O/'join-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'samples':len(points),'audioFlags':flags}))
