from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
mc=ROOT/'motion-canvas/src/projects/picking-sides'
p=json.loads((mc/'depth-reel-plan-v1.json').read_text('utf-8'));names=[]
for r in p['rows']:
 n='depth'+r['id'];names.append(n)
 (mc/'scenes'/(n+'.tsx')).write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {depthExplanation} from '../depth-explanations-v1';\nexport default makeScene2D(function*(view){yield*depthExplanation(view,'"+r['id']+"',"+str(r['frames'])+");});\n",'utf-8')
(mc/'depth-reel-v1.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join("import "+n+" from './scenes/"+n+"?scene';" for n in names)+"\nexport default makeProject({name:'picking-sides-depth-v1',scenes:["+','.join(names)+"]});\n",'utf-8')
html=(ROOT/'motion-canvas/src/projects/familiar-game-rules/timed-white-review-v1.html').read_text('utf-8').replace('timed-white-reel-project-v1','depth-reel-v1').replace('timed-white-reel-plan-v1','depth-reel-plan-v1').replace('familiar-game-rules-timed-white-v1','picking-sides-depth-v1').replace('측정 설명','입체 설명')
(mc/'depth-review-v1.html').write_text(html,'utf-8')
(ROOT/'motion-canvas/tsconfig.visual-depth.json').write_text(json.dumps({'extends':'./tsconfig.json','include':['src/env.d.ts','src/shared/depth-diagrams.tsx','src/projects/picking-sides/depth-explanations-v1.tsx','src/projects/picking-sides/depth-reel-v1.ts','src/projects/picking-sides/scenes/depth*.tsx']}),'utf-8')
print('6 independent retained-duration Motion Canvas scenes prepared')
