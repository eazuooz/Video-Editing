from pathlib import Path
import json,subprocess,numpy as np,soundfile as sf,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';O=P/'production/local/reference-preserving-v2/edit';N=R/'shared/output/narration/game-reward-planning/reference-preserving-v2';timing=json.loads((N/'game-reward-planning-reference-v2.timing.json').read_text());patches=json.loads((N/'leveled-patched/patch-map.json').read_text(encoding='utf8'))
rate=48000;voice,sr=sf.read(O/'narration-stem.wav',dtype='float32');voice=voice.mean(axis=1)
p=subprocess.run(['ffmpeg','-v','error','-i',str(O/'game-reward-planning-v2-clean.mp4'),'-vn','-af','pan=mono|c0=0.5*c0+0.5*c1','-f','f32le','-ac','1','-ar',str(rate),'-'],capture_output=True,check=True);encoded=np.frombuffer(p.stdout,dtype='<f4');mask=np.zeros(len(voice),dtype=bool);scenes=[]
for i in range(1,12):
 sid=f'{i:02}';origin=next(x['start'] for x in timing['entries'] if x['scene_id']==sid)+2;duration=sf.info(N/'chunks'/f'{sid}-scene.wav').duration;asr=json.loads((N/'asr'/f'{sid}.json').read_text(encoding='utf8'));words=[]
 for w in asr['words']:
  a,b=w['timestamp'];a=0 if a is None else a;b=duration if b is None else b
  if any(s['scene']==sid and a<s['slot'][1] and b>s['slot'][0] for s in patches):continue
  words.append((a,b))
 for s in patches:
  if s['scene']!=sid:continue
  q=json.loads((N/'patches/asr'/f"{s['id']}.json").read_text(encoding='utf8'))
  words += [(s['start']+(w['timestamp'][0] or 0),s['start']+(w['timestamp'][1] or s['duration'])) for w in q['words']]
 for a,b in words:mask[max(0,round((origin+a-.06)*rate)):min(len(mask),round((origin+b+.06)*rate))]=True
 scenes.append({'id':sid,'start':origin,'duration':duration})
length=min(len(voice),len(encoded));voice=voice[:length];encoded=encoded[:length];mask=mask[:length];win=round(.4*rate);hop=round(.1*rate);pos=np.arange(0,length-win+1,hop);times=(pos+win/2)/rate
cov=np.r_[0,np.cumsum(mask,dtype=np.int64)];active=(cov[pos+win]-cov[pos])>=.3*win
def db(x):
 e=np.r_[0,np.cumsum(x.astype(np.float64)**2)];return 10*np.log10(np.maximum((e[pos+win]-e[pos])/win,1e-14))
v,f=db(voice),db(encoded);windows=[];summary=[]
for s in scenes:
 use=active&(times>=s['start'])&(times<=s['start']+s['duration']);median=float(np.median(v[use]));rows=[]
 for a in np.arange(s['start'],s['start']+s['duration'],3):
  b=min(a+3,s['start']+s['duration']);q=use&(times>=a)&(times<b)
  if sum(q)<5:continue
  row={'scene':s['id'],'start':round(a,3),'end':round(b,3),'speechWindows':int(sum(q)),'stemMedianDbfs':round(float(np.median(v[q])),2),'encodedMedianDbfs':round(float(np.median(f[q])),2),'encodedMinusStemDb':round(float(np.median(f[q]-v[q])),2),'belowSceneMedianDb':round(median-float(np.median(v[q])),2)};rows.append(row);windows.append(row)
 summary.append({'scene':s['id'],'first':rows[0],'last':rows[-1],'lastMinusFirstDb':round(rows[-1]['stemMedianDbfs']-rows[0]['stemMedianDbfs'],2)})
flags=[x for x in windows if x['belowSceneMedianDb']>5 or x['encodedMinusStemDb']<-1.5 or x['encodedMinusStemDb']>3]
report={'windowSeconds':.4,'hopSeconds':.1,'speechMask':'word timestamps, including3 replacement intervals; no amplitude gate','sourceDriftEvidence':'leveled/*.json retains original PCM vs smooth-stage measurements','processedNarration':'narration-stem.wav','finalEncoded':'game-reward-planning-v2-clean.mp4','captionedAudio':'must verify decoded-equivalent stream copy','sceneSummary':summary,'windows':windows,'flaggedRanges':flags,'wholeFileLufsDoesNotApproveContinuity':True,'humanListening':'pending user Drive review; quantitative evidence only'}
(O/'audio-level-continuity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'sceneLastMinusFirst':[{'scene':s['scene'],'dB':s['lastMinusFirstDb']} for s in summary],'flags':flags}))
