"""Sparse PCM correlation checks, reading bounded chunks rather than full WAVs."""
from pathlib import Path
import json,numpy as np,soundfile as sf
from scipy.signal import correlate,resample_poly
P=Path(__file__).resolve().parents[1]/'production/local';rows=[]
with sf.SoundFile(P/'audio-v1/narration.wav') as src,sf.SoundFile(P/'render-v3/composite/narration-normalized.wav') as ref:
 sr=src.samplerate;rr=ref.samplerate
 for sec in [1,30,300,900,1500,1895]:
  ref.seek(int(sec*rr));x=ref.read(rr,dtype='float32').mean(axis=1);src.seek(int((sec-.2)*sr));y=resample_poly(src.read(int(1.4*sr),dtype='float32'),2,1)
  c=correlate(y,x,mode='valid',method='fft');i=int(np.argmax(np.abs(c)));a=y[i:i+len(x)]
  ac=a.astype(np.float64)-float(a.mean());xc=x.astype(np.float64)-float(x.mean())
  correlation=float(np.sum(ac*xc)/np.sqrt(np.sum(ac*ac)*np.sum(xc*xc)+1e-30))
  rows.append(dict(time=sec,sourceLeadSeconds=(i-.2*rr)/rr,correlation=correlation,normalizedGain=float(np.sum(a*x)/(np.sum(a*a)+1e-12))))
 src.seek(len(src)-2400);ref.seek(len(ref)-4800)
 r=dict(sourceSamples=len(src),sourceRate=sr,referenceSamples=len(ref),referenceRate=rr,tailSourcePeak=float(np.max(np.abs(src.read()))),tailReferencePeak=float(np.max(np.abs(ref.read()))),sampledCorrelations=rows)
(P/'render-v3/final-qa/normalization-timing-audit.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
