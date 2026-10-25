from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.signal import fftconvolve
R=Path('D:/Github/VideoEditing');D=R/'shared/output/private-math-gameplay-20261024/m14-v5'
ref=np.array(Image.open(D/'cc-1117.png').convert('L'),dtype=float)
template=ref[430:620,400:590];template-=template.mean();ones=np.ones(template.shape);N=template.size
rows=[]
for i,p in enumerate(sorted(D.glob('track-*.png'))):
 a=np.array(Image.open(p),dtype=float)[330:850,330:690]
 corr=fftconvolve(a,template[::-1,::-1],mode='valid')
 su=fftconvolve(a,ones,mode='valid');ss=fftconvolve(a*a,ones,mode='valid')
 score=corr/np.sqrt(np.maximum(1,ss-su*su/N)*(template*template).sum())
 y,x=np.unravel_index(score.argmax(),score.shape)
 rows.append(dict(t=round(i/4+.125,3),dx=int(x+330-400),dy=int(y+330-430),correlation=float(score[y,x])))
out=R/'projects/game-math-polygon-partition-v2/production/gameplay-abstract-v5/annotation-track.json';out.write_text(json.dumps(dict(method='Offline editorial template tracking, not game detection output; reviewed against source images.',rows=rows),indent=2)+'\n',encoding='utf8')
print(json.dumps(rows))
