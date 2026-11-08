"""Measure local added-voice continuity; unchanged body evidence is reused."""
from pathlib import Path
import json, sys, hashlib, math
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent;L=H/'local'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
selected={x for x in sys.argv[1:] if x.startswith('A')}
target=L/'added-audio-level-review.json';prior=read(target) if target.exists() else {'episodes':[]}
rows={e['id']:e for e in prior['episodes']}
def levels(signal,sr):
 n=round(sr*.1);x=signal[:len(signal)//n*n].reshape(-1,n)
 return 20*np.log10(np.maximum(1e-12,np.sqrt(np.mean(x*x,axis=1))))
for e in read(L/'timing.json')['episodes']:
 if selected and e['id'] not in selected:continue
 raw=L/'voice/chunks'/(e['id']+'-scene.wav');voice=Path(e['voice']);mix=Path(e['audio'])
 assert sha(raw)==e['rawAudioSha256'] and sha(voice)==e['voiceSha256'] and sha(mix)==e['audioSha256']
 r,rs=sf.read(raw,always_2d=True,dtype='float64');v,vs=sf.read(voice,always_2d=True,dtype='float64');m,ms=sf.read(mix,always_2d=True,dtype='float64')
 assert vs==ms==48000
 rd,vd,md=levels(r.mean(axis=1),rs),levels(v.mean(axis=1),vs),levels(m.mean(axis=1),ms)
 n=min(len(rd),len(vd),len(md));rd,vd,md=rd[:n],vd[:n],md[:n]
 active=rd>max(-47,float(np.max(rd))-29)
 gain=vd[active]-rd[active]
 sentences=[]
 for s in e['sentences']:
  lo=max(0,int(s['start']/.1));hi=min(n,math.ceil(s['end']/.1));mask=active[lo:hi]
  if not np.any(mask):continue
  sentences.append({'id':s['id'],'start':s['start'],'end':s['end'],'activeVoiceRmsDb':float(np.median(vd[lo:hi][mask])),'activeMixRmsDb':float(np.median(md[lo:hi][mask]))})
 flags=[]
 for a,b in zip(sentences,sentences[1:]):
  delta=b['activeVoiceRmsDb']-a['activeVoiceRmsDb']
  if abs(delta)>6:flags.append({'before':a['id'],'after':b['id'],'deltaDb':delta})
 row={'id':e['id'],'rawSha256':sha(raw),'voiceSha256':sha(voice),'additionSha256':sha(mix),'rawSampleRate':rs,'mixSampleRate':ms,'speechWindowSeconds':.1,'activeWindows':int(active.sum()),'measuredProcessingGainDb':{'median':float(np.median(gain)),'p05':float(np.percentile(gain,5)),'p95':float(np.percentile(gain,95))},'constantFinalMixGainDb':20*math.log10(e['newMixAttenuation']),'sentenceLevels':sentences,'sentenceStepFlagsAbove6dB':flags,'peakDbfs':20*math.log10(max(1e-12,float(abs(m).max()))),'bodyAudio':'Retained PCM equality is verified independently by opening_edit reconstruct_pcm; no global remix or body gain adjustment.','humanListeningPerformed':False,'pronunciationReview':'Independent full text comparison; human final listening pending.'}
 rows[e['id']]=row
 print(e['id'],'sentence flags',len(flags),'processing median',round(row['measuredProcessingGainDb']['median'],2),'mixgain',round(row['constantFinalMixGainDb'],2),flush=True)
target.write_text(json.dumps({'method':'Speech-active100ms RMS before/after added-voice processing, sentence-level continuity and preserved PCM provenance. This is measurement, not a listening claim.','episodes':sorted(rows.values(),key=lambda e:e['id'])},ensure_ascii=False,indent=2)+'\n','utf-8')
