"""Short look-development scenes; never confused with a finished video."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];M=R/'motion-canvas/src/projects/player-customization/revision-v2'
rows=[('overview',3),('effects',5),('tradeoffs',5),('find',5),('auto',4),('test',5),('appearance',4),('conclusion',4)]
for kind,count in rows:
 cues=[i*3.2/count for i in range(count)]
 spec=dict(duration=(240-.75)/60,cues=cues,credit='설명 화면 내부 시안 · 실제 출처는 제작 설계표')
 (M/('preflight-'+kind+'.tsx')).write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {lesson} from './visuals';\nexport default makeScene2D(function*(view){yield* lesson(view,"+json.dumps(kind)+','+json.dumps(spec,ensure_ascii=False)+');});\n',encoding='utf-8')
imports='\n'.join(f"import s{i} from './preflight-{kind}?scene';" for i,(kind,_) in enumerate(rows))
(M/'preflight-project.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+imports+"\nexport default makeProject({scenes:["+','.join('s'+str(i) for i in range(len(rows)))+']});\n',encoding='utf-8')
print('Prepared8 look-development scenes,1920 frames; final speech timing/captions remain a separate current-output check.')
