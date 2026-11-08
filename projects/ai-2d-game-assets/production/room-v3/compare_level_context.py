"""Check whether low-level flags were introduced by mixing; not a listening test."""
from pathlib import Path
import json,numpy as np,soundfile as sf
H=Path(__file__).resolve().parent;P=H.parents[1];L=P/'production/local/room-v3';O=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v3/video');report=json.loads((H/'level-continuity.json').read_text('utf8'));tm=json.loads((L/'timeline.json').read_text('utf8'))['scenes'];out=[]
with sf.SoundFile(O/'qa/encoded-mix.wav') as mixed:
 for flag in report['flaggedRanges']:
  row=next(s for s in tm if s['id']==flag['scene']);duration=flag['end']-flag['start'];start=max(0,flag['start']-row['start'])
  with sf.SoundFile(row['source']) as source:
   source.seek(round(start*source.samplerate));a=source.read(round(duration*source.samplerate),dtype='float32');sr=source.samplerate
  mixed.seek(round(flag['start']*mixed.samplerate));b=mixed.read(round(duration*mixed.samplerate),dtype='float32').mean(axis=1);msr=mixed.samplerate
  av=[];bv=[]
  for t in np.arange(0,min(len(a)/sr,len(b)/msr)-.1,.1):
   aa=a[round(t*sr):round((t+.1)*sr)];bb=b[round(t*msr):round((t+.1)*msr)];ad=20*np.log10(max(1e-8,float(np.sqrt(np.mean(aa**2)))));bd=20*np.log10(max(1e-8,float(np.sqrt(np.mean(bb**2)))))
   if ad>-55:av.append(ad);bv.append(bd)
  delta=np.array(bv)-np.array(av);spread=float(np.percentile(delta,90)-np.percentile(delta,10)) if len(delta)>2 else None
  out.append({**flag,'medianMixGainDb':float(np.median(delta)) if len(delta) else None,'gainVariationP90P10Db':spread,'mixIntroducedNewDipEvidence':bool(spread is not None and spread>2),'actualNaturalnessListening':'pending'})
report['sourceVersusMixFlagComparison']=out;report['flagsWithMixIntroducedDipEvidence']=[x for x in out if x['mixIntroducedNewDipEvidence']];report['scopeNote']='Word-timestamp/RMS flags remain listening candidates. Source-to-mix comparison can exclude a new editing dip; it does not approve TTS intonation.';(H/'level-continuity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(len(out),'flags;',len(report['flagsWithMixIntroducedDipEvidence']),'with new mixing dip evidence')
