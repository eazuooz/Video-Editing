"""Find quiet edit points between complete paragraphs, without editing audio."""
from pathlib import Path
import hashlib, json
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1/chunks'
ranges={
 '03':[(27.24,27.54),(36.60,36.84)],
 '04':[(10.26,10.52),(19.64,19.84),(28.98,29.52)],
 '05':[(26.72,27.16),(35.34,35.76)],
 '06':[(31.20,31.60)],
 '07':[(26.32,26.58),(35.76,36.06)],
 '10':[(10.10,10.36),(19.70,19.92)],
}
results=[]
for sid, windows in ranges.items():
 source=BASE/f'{sid}-scene.wav';x,rate=sf.read(source,dtype='float64')
 points=[]
 for a,b in windows:
  candidates=np.arange(round(a*rate),round(b*rate),120)
  rms=[np.sqrt(np.mean(x[c-480:c+480]**2)) for c in candidates]
  i=int(np.argmin(rms));c=int(candidates[i])
  points.append({'searchRange':[a,b],'sample':c,'seconds':c/rate,'rms40ms':float(rms[i])})
 results.append({'scene':sid,'source':source.relative_to(ROOT).as_posix(),
  'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rate':rate,'seconds':len(x)/rate,'quietPoints':points})
dest=ROOT/'projects/motion-sickness-games/production/repair1/boundaries.json'
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists():raise RuntimeError('Edit evidence already exists; inspect it.')
dest.write_text(json.dumps({'scenes':results,'status':'quiet-boundaries-proposed-awaiting-composite-ASR'},indent=2)+'\n')
print(json.dumps(results,indent=2))
