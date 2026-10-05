"""Prepare seven independent measured white scenes without opening production gates."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas/src/projects/making-game-sequels';WORK=BASE/'measured-edit-v4'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
plan=read(WORK/'plan.json');output=MC/'timed-white-reel-plan-v4.json'
assert not output.exists()
factory=(MC/'scene-factory.tsx').read_text(encoding='utf-8')
start=factory.index('      view.fill(PAPER.background);')
end=factory.index('      if(lookdev) captionLookdevGuide(view);',start)
drawing=factory[start:end]
helper="import {Line,Rect,Txt,View2D} from '@motion-canvas/2d';\nimport {all,createRef,waitFor} from '@motion-canvas/core';\nimport {PAPER} from '../../styles/research-paper';\nimport plan from './scene-plan.json';\n"+"// Exact drawing block extracted from the reviewed factory; production approval gates remain locked.\nexport function* measuredWhiteDiagram(view:View2D,id:string,frames:number){\nconst scene=plan.scenes.find(s=>s.id===id);if(!scene?.diagram)throw new Error('Reviewed white diagram required');\nconst diagram=scene.diagram;\n"+drawing+"\nyield*waitFor(Math.max(0,frames/60-diagram.labels.length*.58));\n// Actual UI recalculation returned594 for the595-frame two-card04 tail. Preserve its final frame explicitly.\nif(id==='04'&&frames===595)yield;\n}\n"
(MC/'timed-white-diagram-v4.tsx').write_text(helper,encoding='utf-8')
rows=[];cursor=0
for scene in plan['scenes']:
 for segment in scene['segments']:
  if segment['classification']!='explanation':continue
  ends=[p['outputSpeechToSample']/24000-segment['localFromFrame']/60 for p in scene['speechEvidence'] if segment['localFromFrame']/60<p['outputSpeechToSample']/24000<=segment['localFromFrame']/60+segment['frames']/60]
  rows.append(dict(id=segment['id'],sceneId=scene['id'],frames=segment['frames'],seconds=segment['frames']/60,finalStartFrame=segment['startFrame'],reelStartFrame=cursor,paragraphEnds=ends,finalPixelsApproved=False))
  cursor+=segment['frames']
assert len(rows)==7 and cursor==13945
data=dict(schemaVersion=1,status='independent-measured-silent-white-pixel-review',fps=60,totalFrames=cursor,rows=rows,planSha256=hashlib.sha256((WORK/'plan.json').read_bytes()).hexdigest(),factorySha256=hashlib.sha256(factory.encode()).hexdigest(),drawingBlockSha256=hashlib.sha256(drawing.encode()).hexdigest(),productionGatesOpened=False,finalVideoApproved=False)
output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=[];imports=[]
for i,row in enumerate(rows):
 name=f'whitev4_{i:02d}';names.append(name);imports.append(f"import {name} from './scenes/{name}?scene';")
 (MC/'scenes'/f'{name}.tsx').write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {measuredWhiteDiagram} from '../timed-white-diagram-v4';\nimport plan from '../timed-white-reel-plan-v4.json';\n"+f"export default makeScene2D(function*(view){{const s=plan.rows[{i}];yield*measuredWhiteDiagram(view,s.sceneId,s.frames);}});\n",encoding='utf-8')
(MC/'timed-white-reel-project-v4.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(imports)+f"\nexport default makeProject({{name:'making-game-sequels-timed-white-v4',scenes:[{','.join(names)}]}});\n",encoding='utf-8')
html=(ROOT/'motion-canvas/src/projects/avoid-game-comparisons/timed-white-review-v6.html').read_text(encoding='utf-8').replace('timed-white-reel-project-v6','timed-white-reel-project-v4').replace('timed-white-reel-plan-v6','timed-white-reel-plan-v4').replace('avoid-game-comparisons-timed-white-v6','making-game-sequels-timed-white-v4')
(MC/'timed-white-review-v4.html').write_text(html,encoding='utf-8')
print(json.dumps(dict(whiteScenes=len(rows),frames=cursor,newImages=0,productionGatesOpened=False)))
