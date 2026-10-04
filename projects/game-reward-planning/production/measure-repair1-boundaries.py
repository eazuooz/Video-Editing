import hashlib,json
from pathlib import Path
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
dest=BASE/'repair1/boundaries.json'
if dest.exists():raise RuntimeError('Preserve existing boundary measurements')
windows={'02':[(7.70,7.86)],'08':[(9.18,9.32),(17.55,17.72)]}
rows=[]
for sid,ranges in windows.items():
 file=ROOT/f'shared/output/narration/game-reward-planning/qwen3-1.7b-balanced-v1/chunks/{sid}-scene.wav';x,rate=sf.read(file,dtype='float64');points=[]
 for a,z in ranges:
  samples=np.arange(round(a*rate),round(z*rate),24);values=[np.sqrt(np.mean(x[c-360:c+360]**2)) for c in samples];i=int(np.argmin(values));c=int(samples[i]);assert values[i]<.003,(sid,values[i])
  points.append({'searchRange':[a,z],'sample':c,'seconds':c/rate,'rms30ms':float(values[i]),'peak30ms':float(np.max(np.abs(x[c-360:c+360]))),'asrBoundaryCompared':True})
 rows.append({'scene':sid,'source':file.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'rate':rate,'seconds':len(x)/rate,'quietPoints':points})
dest.write_text(json.dumps({'status':'proposed-quiet-boundaries-not-spliced','scenes':rows,'allUnaffectedPcmToBePreserved':True},indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
