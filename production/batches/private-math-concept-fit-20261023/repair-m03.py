"""Finite correction of five QA-flagged scenes; preserves all other rendered lessons."""
from common import *
import sys,shutil
P=R/'projects/game-math-orientation-matrices';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2'
authorized('M03-original')
revision=H/'qa-round1';revision.mkdir(exist_ok=True)
changed=['01','02','05','08','11']
for name in ['render-progress.json','composition.json','outputs.json','qa.json','audio-mix.json']:
 if not (revision/name).exists():shutil.copy2(H/name,revision/name)
receipt=H/'qa-correction.json'
if not receipt.exists():
 save(receipt,dict(status='repairing',startedAt=now(),reviewedContactSheets=11,reviewedFrames=130,mobileSamplesReviewed=['02','05','07','19'],findings=['Old flight wording in the overview','Diagrams triggered by paragraph boundaries rather than visible action; fix four action cues','Sail placed upright in diagram before observed raising; initialize it lying down','Sail focus circle at some moments outside the mast; rekey'],changedScenes=changed,actualListening=False,unchangedMathContent=True))
 d=read(H/'render-progress.json');d['identity']=hashlib.sha256((sha(B/'m03-scenes.py')+sha(R/'manim/projects/game-math-part2-full-series/lesson.py')+sha(H/'timeline.json')).encode()).hexdigest()
 for sid in changed:d['scenes'].pop(sid,None)
 d.update(state='partial-rendered',updatedAt=now(),retainedScenesReason='Only five reviewed scenes change; other scene implementation unchanged.')
 save(H/'render-progress.json',d)
def work(script,exe=None,args=[]):
 authorized('M03-original');subprocess.run([str(exe or Path(sys.executable)),'-u','-X','utf8',str(B/script),*args],cwd=R,check=True)
work('render-m03.py',args=changed)
c=read(H/'composition.json')
identity=hashlib.sha256((sha(H/'timeline.json')+sha(H/'render-progress.json')+sha(B/'compose-m03.py')).encode()).hexdigest()
if c['identity']!=identity:
 c['identity']=identity;c['scenes']=[x for x in c['scenes'] if x['id'] not in changed];c['completed']=False;save(H/'composition.json',c)
work('compose-m03.py')
work('mix-m03.py',exe=R/'qwen3-tts/.venv/Scripts/python.exe')
work('assemble-m03.py')
work('qa-m03.py')
d=read(receipt);d.update(status='encoded-direct-review-pending',finishedAt=now());save(receipt,d)
