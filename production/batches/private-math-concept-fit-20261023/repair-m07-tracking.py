"""Correct two marks after actual output inspection; preserve28 unchanged composites."""
from common import *
import shutil,ast,runpy
P=R/'projects/game-math-interpolation-paths-v2';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';D=R/f'output/{P.name}-concept-fit-v2'
authorized('M07');backup=O/'before-tracking-fix';backup.mkdir(exist_ok=False)
for name in ['composition.json','outputs.json','qa.json','caption-pixel-coverage.json']:
 if (H/name).exists():shutil.copy2(H/name,backup/name)
for p in D.glob('*.mp4'):shutil.copy2(p,backup/p.name)
source=B/'compose-m07.py';s=source.read_text(encoding='utf8');a=s.index('SHOTS=');z=s.index('\nENC=',a);shots=ast.literal_eval(s[a+6:z])
shots['02']['track']=[(.4,.46,.66,58),(1.4,.46,.60,58),(2.3,.34,.53,58),(3.4,.34,.48,58)]
shots['02']['track2']=[(.4,.54,.66,58),(1.4,.54,.60,58),(2.3,.66,.53,58),(3.4,.66,.48,58)]
shots['08']['track']=[(.3,.51,.46,95),(1.0,.54,.46,95),(1.5,.64,.47,95),(2.1,.75,.47,95),(2.55,.76,.45,95)]
source.write_text(s[:a]+'SHOTS='+repr(shots)+s[z:],encoding='utf8')
d=read(H/'composition.json');d['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(source)).encode()).hexdigest();d['scenes']=[x for x in d['scenes'] if x['id'] not in shots];d['completed']=False;save(H/'composition.json',d)
save(H/'tracking-correction.json',dict(at=now(),reason='Output inspection found a cabinet mark drifting onto the floor and exit-door mark remaining in the doorway. Track each cabinet door separately and the moving exit door.',affectedScenes=list(shots),before=rel(backup),unchangedSceneCount=28,all7QaSheetsDirectlyViewed=True,finalReview='pending corrected encode',actualListening=False,correctedShots=shots))
runpy.run_path(str(source),run_name='__main__')
