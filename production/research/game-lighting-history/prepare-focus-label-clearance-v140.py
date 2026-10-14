"""Repair only the remaining evidence-backed heading collision in the first focus scene."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'production/research/game-lighting-history/local/guided-focus-label-v140'
SRC=ROOT/'motion-canvas/src/projects/game-lighting-history-04/spatial'
read=lambda p:json.loads(p.read_text('utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
ref=lambda p:dict(path=rel(p),sha256=sha(p))
def write(p,s):
 assert not p.exists(),str(p)
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(s if isinstance(s,str)else json.dumps(s,ensure_ascii=False,indent=2)+'\n','utf-8')
prior=ROOT/'production/research/game-lighting-history/local/guided-focus-clearance-v137/plan.json';plan=read(prior)
qa=read(ROOT/'production/research/game-lighting-history/local/guided-source-qa-v139/execution.json')
assert qa['status']=='encoded-samples-ready'
proof=ROOT/'projects/game-lighting-history-04/production/focus-label-clearance-defect-v140.json'
write(proof,dict(reviewedAt=datetime.now(timezone.utc).isoformat(),scope=['focus-later-settings'],evidence=[b for b in qa['boards']if b['source']=='clean'and b['frames']==[777,794,945,1097]],observation='At actual frames945/1097 the screen summary overlaps the projected reference-plane heading. Move only the summary upward to y-255, preserving all projected geometry and narration clocks.',existingSourcePreserved=True,newTts=0,otherSourceScenesToRerender=0,finalApproved=False))
model=SRC/'focus-analysis-model-v140.tsx';code=(ROOT/plan['focusModel']['path']).read_text('utf-8')
assert "0,-165,35,P.title"in code
write(model,code.replace('0,-165,35,P.title','0,-255,35,P.title'))
runtime=SRC/'guided-source-runtime-v140.tsx';write(runtime,(ROOT/plan['runtime']['path']).read_text('utf-8').replace('focus-analysis-model-v137','focus-analysis-model-v140'))
scene=plan['scenes'][0];wrapper=SRC/'guided-focus-later-settings-v140.tsx'
write(wrapper,(ROOT/scene['wrapper']['path']).read_text('utf-8').replace('guided-source-runtime-v137','guided-source-runtime-v140'))
write(wrapper.with_suffix('.meta'),dict(version=0,timeEvents=[],seed=140000))
scene={**scene,'wrapper':ref(wrapper),'fromFrame':0,'toFrame':1100}
name='episode04-guided-focus-label-v140';audio=BASE/'audio'/f'{name}.wav';project=SRC/f'{name}.ts'
write(project,"import {makeProject} from '@motion-canvas/core';\nimport scene from './guided-focus-later-settings-v140?scene';\nexport default makeProject({scenes:[scene],audio:'/@fs/"+audio.as_posix()+"'});\n")
write(project.with_suffix('.meta'),dict(version=0,shared=dict(background=None,range=[0,1099/60],size=dict(x=1920,y=1080),audioOffset=0),preview=dict(fps=30,resolutionScale=1),rendering=dict(fps=60,resolutionScale=1,colorSpace='srgb',exporter=dict(name='@motion-canvas/ffmpeg',options=dict(fastStart=True,includeAudio=True)))))
cfg=(ROOT/'motion-canvas/vite.game-lighting-history04.guided-focus-clearance-v137.config.ts').read_text('utf-8').replace('episode04-guided-focus-clearance-v137',name).replace('guided-focus-clearance-v137','guided-focus-label-v140').replace('port:9273','port:9274')
write(ROOT/'motion-canvas/vite.game-lighting-history04.guided-focus-label-v140.config.ts',cfg)
write(BASE/'plan.json',{**plan,'prior':ref(prior),'pixelRepairReview':ref(proof),'focusModel':ref(model),'runtime':ref(runtime),'jobs':[dict(name=name,project=rel(project),frames=1100,audio=dict(path=rel(audio),samples=440000),output=rel(BASE/'renders'/f'{name}.mp4'),execution=rel(BASE/'renders'/f'{name}.execution.json'))],'scenes':[scene]})
P=ROOT/'production/research/game-lighting-history'
write(P/'assemble-guided-focus-label-audio-v140.py',(P/'assemble-guided-focus-clearance-audio-v137.py').read_text('utf-8').replace('guided-focus-clearance-v137','guided-focus-label-v140'))
review=(P/'build-guided-focus-review-v138.py').read_text('utf-8').replace('guided-focus-clearance-v137','guided-focus-label-v140').replace('v138','v142').replace('V138','V142').replace('N == 3280','N == 1100').replace('len(cues) == 18','len(cues) == 6').replace('Three repaired black','One repaired black').replace('all18','all6')
write(P/'build-guided-focus-label-review-v142.py',review)
print(json.dumps(dict(scope=[scene['id']],frames=1100,oldPixelsPreserved=True,newTts=0)))
