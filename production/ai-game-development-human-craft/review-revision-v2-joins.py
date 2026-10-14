"""Diagnose current raw speech edges and word-internal silence; never auto-trim speech."""
from pathlib import Path
import json,hashlib
import numpy as np
import soundfile as sf
from revision_paths import workroot
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ROOT/f'projects/{SLUG}/project.json');out=ROOT/m['tts']['outputDir'];script=read(ROOT/m['paths']['script'])
rows=[];flags=[]
for s in script['scenes']:
 sid=s['id'];path=out/'chunks'/f'{sid}-scene.wav';y,sr=sf.read(path,dtype='float32');a=read(out/'asr'/f'{sid}.json');assert a['audio_sha256']==sha(path)
 n=round(.01*sr);rms=np.sqrt(np.mean(y[:len(y)//n*n].reshape(-1,n)**2,axis=1));db=20*np.log10(np.maximum(rms,1e-9))
 active=np.flatnonzero(db>max(-48,float(np.percentile(db,90))-30));assert len(active)
 row={'scene':sid,'pcmSha256':sha(path),'duration':len(y)/sr,'firstWords':' '.join(w['text'] for w in a['words'][:4]),'lastWords':' '.join(w['text'] for w in a['words'][-4:]),'leadingLowEnergySeconds':float(active[0]*.01),'trailingLowEnergySeconds':float((len(db)-active[-1]-1)*.01),'firstSample':float(y[0]),'lastSample':float(y[-1])}
 rows.append(row)
 quiet=np.flatnonzero(db<-48)
 for group in np.split(quiet,np.where(np.diff(quiet)>1)[0]+1) if len(quiet) else []:
  if len(group)<30:continue
  start,end=group[0]*.01,(group[-1]+1)*.01
  # A complete low-energy interval inside a single recognized word needs
  # contextual review. Inter-word/phrase breathing is deliberately retained.
  word=next((w for w in a['words'] if w['timestamp'][0]+.08<start and end<w['timestamp'][1]-.08),None)
  if word:flags.append({'scene':sid,'start':start,'end':end,'word':word['text'],'kind':'word-internal-low-energy-review','status':'pending-contextual-listening'})
joins=[]
for left,right in zip(rows,rows[1:]):
 pause=left['trailingLowEnergySeconds']+m['tts']['sceneGapSeconds']+right['leadingLowEnergySeconds']
 joins.append({'from':left['scene'],'to':right['scene'],'estimatedLowEnergyPauseSeconds':pause,'insertedGapSeconds':m['tts']['sceneGapSeconds'],'reviewNeeded':pause>1.2,'method':'10ms RMS, threshold=max(-48dBFS,scene90th-percentile minus30dB); diagnostic only'})
result={'status':'measured-not-a-listening-approval','scenes':rows,'joins':joins,'wordInternalFlags':flags,'speechTrimmingApplied':False,'timeStretchApplied':False,'previousInsertedGapSeconds':.72,'currentInsertedGapSeconds':m['tts']['sceneGapSeconds'],'humanListening':'pending'}
(workroot(ROOT)/'speech-joins.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sceneCount':len(rows),'joinCount':len(joins),'wordInternalFlags':len(flags),'longJoins':[j for j in joins if j['reviewNeeded']],'listening':'pending'},ensure_ascii=False))
