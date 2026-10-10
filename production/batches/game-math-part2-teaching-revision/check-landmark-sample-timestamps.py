"""Compare authored reference pixels to native source frames; do not approve motion."""
from pathlib import Path
import subprocess,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision';rows=[]
for ident in ['GA05old','O02','GB03','GA04']:
 D=O/'landmark-authoring'/ident
 if not (D/'frames.json').exists():continue
 m=json.loads((D/'frames.json').read_text());t=m['interval'][0];source=ROOT/(('shared/output/game-math-part2-teaching-revision/sources/' if m['source']=='_dw9jjRpanA' else 'shared/output/game-math-part2-full-series/sources/')+m['source']+'.mp4')
 raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(source),'-frames:v','61','-vf','scale=800:450','-fps_mode','passthrough','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
 a=np.frombuffer(raw,dtype=np.uint8).reshape(-1,450,800,3);ref=np.asarray(Image.open(D/f'{t:.2f}.png').convert('RGB'));errors=np.mean(np.abs(a.astype(np.int16)-ref.astype(np.int16)),axis=(1,2,3));i=int(errors.argmin())
 rows.append({'id':ident,'labelledTime':t,'nativeMatchingFrameOffset':i,'offsetSeconds':i/60,'meanAbsolutePixelError':float(errors[i]),'step':m['step']})
(O/'landmark-sample-timestamp-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows))
