from pathlib import Path
import json,hashlib,numpy as np,soundfile as sf,datetime
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
new=read(B/'part1-protected-onsets-tts-execution-v211.json');old=read(B/'part1-selected-current-tts-execution-v208.json')
jobs=[('size-preface',next(x for x in new['results']if x['id']=='runtime-texture-size'),2.42,2.66),('car-preface',next(x for x in new['results']if x['id']=='geometry-car-material'),2.34,2.56),('car-first-close',next(x for x in new['results']if x['id']=='geometry-car-material'),4.42,4.56),('car-second-open',next(x for x in old['results']if x['id']=='geometry-car-material'),2.14,2.30)]
rows=[]
for label,r,a,z in jobs:
 p=ROOT/r['path'];assert sha(p)==r['sha256'];data,sr=sf.read(p,dtype='float32');assert sr==24000 and data.ndim==1
 lo=round(a*sr);hi=round(z*sr);win=round(.02*sr)
 energy=np.convolve(np.square(data[lo:hi],dtype=np.float64),np.ones(win)/win,'valid');idx=int(np.argmin(energy));center=lo+idx+win//2
 sample=data[max(0,center-240):center+240]
 rows.append(dict(label=label,source=r,searchSeconds=[a,z],minimum20msRms=float(np.sqrt(energy[idx])),boundarySample=center,boundarySeconds=center/sr,boundaryAmplitude=float(data[center]),neighbor20msPeak=float(np.max(np.abs(sample))),neighbor20msRms=float(np.sqrt(np.mean(sample**2))),quietBoundaryObserved=float(np.sqrt(energy[idx]))<.004))
out=B/'part1-protected-boundary-inspection-v218.json'
assert not out.exists();out.write_text(json.dumps(dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,sourceFullAsr=read(B/'part1-protected-onsets-asr-execution-v214.json')['completed'],literalScriptUnchanged=True,approved=False,humanListening='pending',next='Review observed boundaries before preserving complete first/second sentences; no fades or tail padding to disguise a failed end.'),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps([dict(label=x['label'],sample=x['boundarySample'],seconds=x['boundarySeconds'],rms=x['minimum20msRms'],peak=x['neighbor20msPeak'],amplitude=x['boundaryAmplitude'])for x in rows]))
