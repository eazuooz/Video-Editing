"""Prepare exact-duration independent white inputs; leave final gates closed."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas/src/projects/familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=BASE/'word-action-source-candidate-v2.json';plan=read(source)
assert not (MC/'timed-white-reel-plan-v1.json').exists()
rows=[];cursor=0
for piece in plan['pieces']:
    for segment in piece['roleSegments']:
        if segment['role']!='explanation':continue
        row=dict(id=piece['logicalScene'],pieceId=piece['id'],frames=segment['frames'],reelStartFrame=cursor,
                 finalStartFrame=segment['startFrame'],finalEndFrame=segment['endFrame'],finalPixelsApproved=False)
        rows.append(row);cursor+=row['frames']
assert len(rows)==8 and cursor==9140
assert sum(r['frames'] for r in rows if r['id'] not in ['14','17'])==8835
factory=(MC/'scene-factory.tsx').read_text('utf-8')
start=factory.index('      view.fill(PAPER.background);');end=factory.index('      if (lookdev) view.add(',start)
drawing=factory[start:end]
helper="import {Circle,Line,Rect,Txt,View2D} from '@motion-canvas/2d';\nimport {all,createRef,waitFor} from '@motion-canvas/core';\nimport {PAPER} from '../../styles/research-paper';\nimport plan from './scene-plan.json';\n"+"// Exact existing drawing primitives; these silent inputs do not bypass production gates.\nexport function* timedWhiteInput(view:View2D,id:string,frames:number){\nconst scene=plan.scenes.find(s=>s.id===id);if(!scene?.diagram)throw new Error('Independent explanation required');\nconst d=scene.diagram;view.removeChildren();\n"+drawing+"\nyield*waitFor(Math.max(0,frames/60-used));\n}\n"
helper=helper.replace('\nyield*waitFor(Math.max(0,frames/60-used));\n}', '\nyield*waitFor(Math.max(0,frames/60-used));\n// UI recalculation returned1262 for the1263-frame conclusion; preserve its last frame.\nif(id===\'11\'&&frames===1263)yield;\n}')
(MC/'timed-white-diagram-v1.tsx').write_text(helper,'utf-8')
data=dict(schemaVersion=1,slug='familiar-game-rules',createdAt=datetime.now(timezone.utc).isoformat(),
          status='independent-measured-silent-white-input-review',fps=60,totalFrames=cursor,rows=rows,
          timingCandidate=str(source.relative_to(ROOT)).replace('\\','/'),timingCandidateSha256=sha(source),
          factorySha256=sha(MC/'scene-factory.tsx'),drawingBlockSha256=hashlib.sha256(drawing.encode()).hexdigest(),
          guideDrawingSha256=sha(MC/'guide-explanation.tsx'),originalWhiteSecondsPreserved=147.2,
          originalWhiteFrames=8835,extraWhiteFrames=305,allDiagramPixelsReviewed=False,
          productionGatesOpened=False,finalTimingApproved=False,finalVideoApproved=False,newGitImages=0)
(MC/'timed-white-reel-plan-v1.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
names=[];imports=[]
for i,row in enumerate(rows):
    name=f'whitev1_{i:02d}';names.append(name);imports.append(f"import {name} from './scenes/{name}?scene';")
    kind='guideExplanation' if row['id'] in ['14','17'] else 'timedWhiteInput'
    imp='../guide-explanation' if kind=='guideExplanation' else '../timed-white-diagram-v1'
    text=f"import {{makeScene2D}} from '@motion-canvas/2d';\nimport {{{kind}}} from '{imp}';\nexport default makeScene2D(function*(view){{yield*{kind}(view,'{row['id']}',{row['frames']});}});\n"
    (MC/'scenes'/f'{name}.tsx').write_text(text,'utf-8')
(MC/'timed-white-reel-project-v1.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(imports)+f"\nexport default makeProject({{name:'familiar-game-rules-timed-white-v1',scenes:[{','.join(names)}]}});\n",'utf-8')
html=(ROOT/'motion-canvas/src/projects/making-game-sequels/timed-white-review-v4.html').read_text('utf-8')
html=html.replace('timed-white-reel-project-v4','timed-white-reel-project-v1').replace('timed-white-reel-plan-v4','timed-white-reel-plan-v1').replace('making-game-sequels-timed-white-v4','familiar-game-rules-timed-white-v1')
html=html.replace('if(busy)return;busy=true;',"if(busy)return;if(rows.length!==plan.rows.length||rows.some((r,i)=>r.duration!==plan.rows[i].frames))throw new Error('Exact independent frame recalculation required before rendering');busy=true;")
html=html.replace('pre{margin:8px;white-space:pre-wrap}', 'pre{margin:8px;white-space:pre-wrap;max-height:90px;overflow:auto}')
(MC/'timed-white-review-v1.html').write_text(html,'utf-8')
print(json.dumps(dict(whiteScenes=8,frames=cursor,originalWhiteFrames=8835,extraWhiteFrames=305,productionGatesOpened=False)))
