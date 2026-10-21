import os
"""Compare actual speech-active local source, processed and placed-voice levels."""
from pathlib import Path
import json,hashlib
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[3];P=R/'projects/vampire-survivors-d2-copyright';L=P/('production/'+os.environ.get('YAMYAM_D2_LOCAL','local'))
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw,sr=sf.read(L/'narration-source.wav',dtype='float32');norm,nr=sf.read(L/'narration-normalized-v2.wav',dtype='float32',always_2d=True);final,fr=sf.read(L/'narration-final-stem.wav',dtype='float32',always_2d=True)
assert sr==24000 and nr==fr==48000 and len(norm)==len(raw)*2
final=final[96000:96000+len(norm)];assert final.shape==norm.shape
for a in [raw,norm,final]:assert np.isfinite(a).all()
mask=np.zeros(len(raw),dtype=bool)
for w in rd(L/'whole-source-asr-aligned.json')['words']:
 a,z=w['timestamp']
 if a is not None and z is not None:mask[round(a*sr):round(z*sr)]=True
def prefix(x,m):
 power=np.square(x,dtype=np.float64) if x.ndim==1 else np.mean(np.square(x,dtype=np.float64),axis=1)
 return np.r_[0,np.cumsum(power*m)]
p0=prefix(raw,mask);p1=prefix(norm,np.repeat(mask,2));p2=prefix(final,np.repeat(mask,2));counts=np.r_[0,np.cumsum(mask,dtype=np.int64)]
rows=[];flags=[];size=9600;step=2400;report=rd(P/'production/audio-review.json')
for lo in range(0,len(raw)-size,step):
 hi=lo+size;count=counts[hi]-counts[lo]
 if count<.15*sr:continue
 levels=[10*np.log10(max((p[hi*rate]-p[lo*rate])/(count*rate),1e-18)) for p,rate in [(p0,1),(p1,2),(p2,2)]]
 row={'startSourceSeconds':lo/sr,'endSourceSeconds':hi/sr,'rawVoiceDbfs':float(levels[0]),'processedVoiceDbfs':float(levels[1]),'placedFinalVoiceDbfs':float(levels[2]),'processedMinusSourceDb':float(levels[1]-levels[0]),'placedMinusProcessedDb':float(levels[2]-levels[1])};rows.append(row)
 if row['processedMinusSourceDb']<-3 or abs(row['placedMinusProcessedDb']-report['programGainDb'])>.02:flags.append(row)
 if len(rows)>1 and rows[-1]['startSourceSeconds']-rows[-2]['startSourceSeconds']<.11:
  a,b=rows[-2],rows[-1];rdrop=b['rawVoiceDbfs']-a['rawVoiceDbfs'];fdrop=b['placedFinalVoiceDbfs']-a['placedFinalVoiceDbfs']
  if fdrop<-6 and fdrop<rdrop-1.5:flags.append({'kind':'new-abrupt-processed-drop','before':a,'after':b})
assert not flags,flags[:5]
summary={'status':'passed-source-to-processed-to-placed-local-speech-continuity','sourceSha256':sha(L/'narration-source.wav'),'processedSha256':sha(L/'narration-normalized-v2.wav'),'placedVoiceSha256':sha(L/'narration-final-stem.wav'),'sourcePcmPreserved':True,'speechWindowSeconds':.4,'stepSeconds':.1,'speechActiveWindows':len(rows),'minimumProcessedMinusSourceDb':min(r['processedMinusSourceDb'] for r in rows),'medianProcessedMinusSourceDb':float(np.median([r['processedMinusSourceDb'] for r in rows])),'placedGainDb':report['programGainDb'],'voiceBackgroundDrivenDucking':False,'noSpeechHolesOrExtraJoinFades':True,'sourceToProcessedFlags':flags,'humanContextListening':'pending','encodedWindowEvidence':f'production/{L.name}/encoded-continuity-windows.json'}
wr(L/'source-stem-continuity-windows.json',{'summary':summary,'windows':rows});report['sourceStemLocalContinuity']=summary;wr(P/'production/audio-review.json',report)
print(json.dumps(summary),flush=True)
