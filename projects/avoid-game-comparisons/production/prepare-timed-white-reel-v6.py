"""Prepare an independent measured silent reel for pixel review, without opening final gates."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas/src/projects/avoid-game-comparisons';WORK=BASE/'measured-edit-v6'
plan=json.loads((WORK/'plan.json').read_text(encoding='utf-8-sig'))
out=MC/'timed-white-reel-plan-v6.json';assert not out.exists()
rows=[];cursor=0
for scene in plan['scenes']:
 for segment in scene['segments']:
  if segment['classification']!='explanation':continue
  original='original-white-explanation' in segment['id']
  ends=[p['pcmToSample']/24000 for p in scene['speechEvidence']] if original else [segment['frames']/60]
  ends[-1]=segment['frames']/60
  rows.append(dict(id=segment['id'],sceneId=scene['id'],diagramId=segment['diagramId'],frames=segment['frames'],seconds=segment['frames']/60,
   finalStartFrame=segment['startFrame'],reelStartFrame=cursor,paragraphEnds=ends,concept=original or scene['id'] in ['13','14'],
   finalCaptionPixelsApproved=False))
  cursor+=segment['frames']
assert len(rows)==14 and cursor==12552
out.write_text(json.dumps(dict(status='independent-timed-silent-pixel-review',fps=60,totalFrames=cursor,rows=rows,
 measuredPlanSha256=hashlib.sha256((WORK/'plan.json').read_bytes()).hexdigest(),finalVideoApproved=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
imports=[];names=[]
for i,row in enumerate(rows):
 name=f'whitev6_{i:02d}';names.append(name);imports.append(f"import {name} from './scenes/{name}?scene';")
 diagramId=row['sceneId'] if row['concept'] else row['diagramId']
 body=f"yield*conceptDiagram(view,'{diagramId}',s.seconds,s.paragraphEnds);" if row['concept'] else f"yield*cueDiagram(view,'{diagramId}',s.seconds);"
 (MC/'scenes'/f'{name}.tsx').write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {conceptDiagram} from './concept-diagrams';\nimport {cueDiagram} from './cue-diagrams';\nimport plan from '../timed-white-reel-plan-v6.json';\n"+
  f"export default makeScene2D(function*(view){{const s=plan.rows[{i}];{body}}});\n",encoding='utf-8')
(MC/'timed-white-reel-project-v6.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(imports)+
 "\n// Independent timed pixel review; production scene gates are retained.\n"+f"export default makeProject({{name:'avoid-game-comparisons-timed-white-v6',scenes:[{','.join(names)}]}});\n",encoding='utf-8')
print(json.dumps(dict(whiteScenes=len(rows),frames=cursor,newImages=0,productionGatesOpened=False)))
