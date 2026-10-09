from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
M=ROOT/'motion-canvas/src/projects/presenting-game-scores'
ko=json.loads((BASE.parent/'script/narration.ko.json').read_text('utf-8-sig'))
if (BASE/'narration-tts-measured-v1.json').exists():
 raise RuntimeError('Structural timing preparation cannot replace measured narration timing')
for scene in ko['scenes']:
 (M/'scenes'/f"{scene['id']}.tsx").write_text('''import {makeScene2D} from '@motion-canvas/2d';
import {scoreExplanation} from '../spatial-score-explanation';
import {EXPLANATION_TIMING} from '../explanation-timing';
export default makeScene2D(function* (view) {
  yield* scoreExplanation(view,'ID',EXPLANATION_TIMING['ID']);
});
'''.replace('ID',scene['id']),'utf-8')
timing={s['id']:dict(durationSeconds=12,paragraphStarts=[0,4,8],measured=False) for s in ko['scenes']}
(M/'explanation-timing.ts').write_text("// Twelve-second structural previews only. Not measured narration or final allocation.\nimport type {ExplanationTiming} from './spatial-score-explanation';\nexport const EXPLANATION_TIMING:Record<string,ExplanationTiming>="+json.dumps(timing,ensure_ascii=False,indent=2)+";\n",'utf-8')
imports="\n".join(f"import scene{i:02} from './scenes/{s['id']}?scene';" for i,s in enumerate(ko['scenes'],1))
project="import {makeProject} from '@motion-canvas/core';\n"+imports+"\nexport default makeProject({name:'presenting-game-scores-structural-preview',scenes:["+','.join(f'scene{i:02}' for i in range(1,11))+"]});\n"
(M/'black-explanation-preflight-v1.ts').write_text(project,'utf-8')
# Keep the previous starter main file as creation history; the prepared main
# points to independent black scenes and has no placeholder audio as narration.
(M/'project.ts').write_text("// Black independent explanation authoring entry; final media gates remain false.\nexport {default} from './black-explanation-preflight-v1';\n",'utf-8')
files=[M/'spatial-score-explanation.tsx',M/'black-explanation-preflight-v1.ts',M/'explanation-timing.ts',*[M/'scenes'/f"{s['id']}.tsx" for s in ko['scenes']]]
(BASE/'prepared-independent-mc-v1.json').write_text(json.dumps(dict(schemaVersion=1,slug='presenting-game-scores',
 preparedAt=datetime.now(timezone.utc).isoformat(),independentScenes=10,style='research-black-v1',
 files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files],
 geometry='Projected XY floor/Z height; camera yaw, depth perspective, separate top/front/right faces and camera-space ordering',
 structuralPreviewSecondsPerScene=12,measuredNarrationTimed=False,actualAnimatedPixelsReviewed=False,
 finalCaptionCuePixelsReviewed=False,finalMediaApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print('Prepared10 independent black spatial MC scenes. No render or pixel approval.')
