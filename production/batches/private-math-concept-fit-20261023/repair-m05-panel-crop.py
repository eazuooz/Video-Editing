"""Fix only three split-screen model viewports found clipped in final-file QA."""
from common import *
import shutil,runpy
P=R/'projects/game-math-quaternion-foundations-v3';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';D=R/'output'/f'{P.name}-concept-fit-v2';authorized('M05')
backup=O/'before-panel-crop-fix';backup.mkdir(exist_ok=True)
for name in ['composition.json','outputs.json','qa.json','caption-pixel-coverage.json']:
 src=H/name;dst=backup/name
 if src.exists() and not dst.exists():shutil.copy2(src,dst)
for kind in ['clean','captioned']:
 src=D/f'{P.name}.{kind}.mp4';dst=backup/src.name
 if not dst.exists():shutil.copy2(src,dst)
source=B/'compose-m05.py';s=source.read_text(encoding='utf8')
old='crop=850:650:80:210,scale=620:474';new='crop=850:540:80:210,scale=620:394'
assert old in s or new in s
if old in s:source.write_text(s.replace(old,new),encoding='utf8')
d=read(H/'composition.json');d['identity']=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(source)).encode()).hexdigest()
d['scenes']=[x for x in d['scenes'] if x['id'] not in ['02','GA01','QF30']];d['completed']=False;save(H/'composition.json',d)
save(H/'panel-crop-correction.json',dict(at=now(),reason='Direct review of173 current-master frames found the model axis-legend baseline partially included in the side panel. Exclude that bottom legend from the model crop; preserve the separate full side-panel axis label, object size, source pixels, narration and timing.',affectedScenes=['02','GA01','QF30'],oldCrop=old,newCrop=new,before=rel(backup),all15QaSheetsDirectlyViewed=True,unchangedSceneCount=47,nativeBeforeCorrection=dict(start=0,end=121.209,rate=1,wholePlayback=False),finalReview='pending corrected encode',actualListening=False))
runpy.run_path(str(source),run_name='__main__')
