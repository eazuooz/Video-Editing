"""Second-pass positions read from full-size frames, including camera tilt."""
from common import *
import shutil,ast,runpy
P=R/'projects/game-math-interpolation-paths-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';D=R/f'output/{P.name}-concept-fit-v2'
authorized('M07');backup=O/'before-cabinet-tracking-fix';backup.mkdir(exist_ok=False)
for name in ['composition.json','outputs.json','qa.json','caption-pixel-coverage.json']:shutil.copy2(H/name,backup/name)
source=B/'compose-m07.py';s=source.read_text(encoding='utf8');a=s.index('SHOTS=');z=s.index('\nENC=',a);shots=ast.literal_eval(s[a+6:z])
left=[(.4,.46,.69,58),(.7,.46,.69,58),(1.2,.455,.745,58),(1.7,.45,.745,58),(1.9,.40,.80,58),(2.2,.35,.82,58),(2.7,.34,.76,58),(3.,.34,.56,58),(3.2,.34,.486,58),(3.4,.34,.48,58)]
shots['02']['track']=left;shots['02']['track2']=[(t,1-x,y,r) for t,x,y,r in left]
source.write_text(s[:a]+'SHOTS='+repr(shots)+s[z:],encoding='utf8')
d=read(H/'composition.json');d['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(source)).encode()).hexdigest();d['scenes']=[x for x in d['scenes'] if x['id']!='02'];d['completed']=False;save(H/'composition.json',d)
r=read(H/'tracking-correction.json');r['cabinetSecondPass']=dict(at=now(),reason='Full-size frames show the camera tilts down after the doors open. Track the actual door panels, not the cabinet top.',sourceFrameTimes=[33.783,34.783,35.283,35.783,36.283],corrected=left,review='pending corrected moving output');save(H/'tracking-correction.json',r)
runpy.run_path(str(source),run_name='__main__')
