"""Locate quiet paragraph edit boundaries without changing original v1 audio."""
from pathlib import Path
import hashlib, json
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v1/chunks'
windows={
    '03':[(7.90,8.24),(26.92,27.28),(35.24,35.40)],
    '05':[(8.50,8.72),(16.66,16.90),(34.62,34.80),(42.80,43.08)],
    '11':[(45.28,45.52),(54.84,55.06)],
    '12':[(28.30,29.00)],
}
dest=ROOT/'projects/hierarchical-game-outlines/production/repair1/boundaries-refined.json'
if dest.exists():raise RuntimeError('Boundary evidence exists; inspect it.')
results=[]
for sid, ranges in windows.items():
    source=BASE/f'{sid}-scene.wav';x,rate=sf.read(source,dtype='float64')
    points=[]
    for a,b in ranges:
        candidates=np.arange(round(a*rate),round(b*rate),24)
        rms=[np.sqrt(np.mean(x[c-360:c+360]**2)) for c in candidates]
        i=int(np.argmin(rms));c=int(candidates[i])
        assert rms[i]<.003, (sid,a,b,rms[i])
        points.append({'searchRange':[a,b],'sample':c,'seconds':c/rate,
            'rms30ms':float(rms[i]),'peak30ms':float(np.max(np.abs(x[c-360:c+360]))),
            'asrParagraphBoundaryReviewed':True})
    results.append({'scene':sid,'source':source.relative_to(ROOT).as_posix(),
        'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'rate':rate,'seconds':len(x)/rate,'quietPoints':points})
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps({'scenes':results,'status':'quiet-boundaries-proposed-awaiting-current-composite-ASR'},indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2))
