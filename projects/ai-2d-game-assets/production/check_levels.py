"""Measure current encoded audio without pretending metrics are a listening review."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np
import soundfile as sf
P=Path(__file__).resolve().parents[1];L=P/'production/local';Q=L/'qa'
def read(p):return json.loads(p.read_text('utf-8'))
decoded=Q/'encoded-mix.wav'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(L/'final-mix.m4a'),'-c:a','pcm_f32le',str(decoded)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
x,sr=sf.read(decoded,dtype='float32');x=x.mean(axis=1) if x.ndim>1 else x
tm=read(L/'timeline.json');asr=read(Q/'narration.timestamps.json');records=[];flags=[]
for scene in tm['scenes']:
 words=[w for w in asr['chunks'] if None not in w['timestamp'] and scene['start']<=sum(w['timestamp'])/2<=scene['speechEnd']]
 points=[]
 for t in np.arange(scene['start'],scene['speechEnd']-.4,.1):
  coverage=sum(max(0,min(t+.4,w['timestamp'][1])-max(t,w['timestamp'][0])) for w in words)
  if coverage<.25:continue
  a=x[round(t*sr):round((t+.4)*sr)];db=20*np.log10(max(1e-8,float(np.sqrt(np.mean(a*a)))))
  points.append((float(t),float(db)))
 median=float(np.median([db for t,db in points]));ranges=[];active=[]
 for t,db in points:
  if db<median-6:
   if active and t-active[-1][0]>.151:
    if active[-1][0]-active[0][0]+.1>=.5:ranges.append(active)
    active=[]
   active.append((t,db))
  elif active:
   if active[-1][0]-active[0][0]+.1>=.5:ranges.append(active)
   active=[]
 if active and active[-1][0]-active[0][0]+.1>=.5:ranges.append(active)
 for group in ranges:flags.append({'scene':scene['id'],'start':group[0][0],'end':group[-1][0]+.4,'relativeDb':float(np.median([v for t,v in group])-median),'review':'Contextual listening pending; not automatically corrected or declared a defect'})
 records.append({'id':scene['id'],'medianSpeechWindowDbfs':median,'speechWindows':len(points),'rangeP10P90Db':float(np.percentile([d for t,d in points],90)-np.percentile([d for t,d in points],10))})
joins=[{'from':a['id'],'to':b['id'],'changeDb':b['medianSpeechWindowDbfs']-a['medianSpeechWindowDbfs']} for a,b in zip(records,records[1:])]
report={'method':'Decoded current AAC;400ms RMS/100ms hop; word timestamps require250ms speech overlap; flag6dB below paragraph median for>=0.5s. Pauses are not labeled weak speech. No waveform trimming.','audioSha256':hashlib.file_digest((L/'final-mix.m4a').open('rb'),'sha256').hexdigest(),'scenes':records,'joins':joins,'joinsAbove3Db':[j for j in joins if abs(j['changeDb'])>=3],'flaggedRanges':flags,'humanListening':'pending','doesNotCertifyNaturalness':True}
(P/'production/level-continuity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Level continuity:',len(flags),'context ranges;',len(report['joinsAbove3Db']),'joins over3dB')
