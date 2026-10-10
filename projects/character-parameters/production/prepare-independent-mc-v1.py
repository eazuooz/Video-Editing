"""Create twelve independent explanation entries; twelve-second structural only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas/src/projects/character-parameters'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=read(BASE/'paired-script-direct-review-v1.json');assert review['contentReadyForApprovedVoiceMeasurement']
script=read(BASE.parent/'script/narration.ko.json');intents=read(BASE.parent/'planning/scene-intents-v1.json')
assert [x['id'] for x in script['scenes']]==[x['id'] for x in intents['scenes']]
entry=MC/'black-structural-preflight-v1.ts';assert not entry.exists()
scene_dir=MC/'scenes';scene_dir.mkdir(parents=True,exist_ok=True)
timings={}
for scene in script['scenes']:
    sid=scene['id'];n=len(scene['lines']);timings[sid]=dict(durationSeconds=12,paragraphStarts=[i*12/n for i in range(n)],measured=False)
    (scene_dir/(sid+'.tsx')).write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {characterExplanation} from '../spatial-character-explanation';\nimport {PROTOTYPE_TIMING} from '../prototype-timing-v1';\nexport default makeScene2D(function* (view) {\n  yield* characterExplanation(view,'"+sid+"',PROTOTYPE_TIMING['"+sid+"']);\n});\n",'utf-8')
(MC/'prototype-timing-v1.ts').write_text("// Structural prototype only; every scene12s is not measured voice or final allocation.\nimport type {CharacterTiming} from './spatial-character-explanation';\nexport const PROTOTYPE_TIMING:Record<string,CharacterTiming>="+json.dumps(timings,ensure_ascii=False,indent=2)+';\n','utf-8')
imports='\n'.join("import s"+str(i)+" from './scenes/"+s['id']+"?scene';" for i,s in enumerate(script['scenes']))
entry.write_text("import {makeProject} from '@motion-canvas/core';\n"+imports+"\n// Silent structural prototype: no final narration, branding or membership output.\nexport default makeProject({name:'character-parameters-black-structural-v1',scenes:["+','.join('s'+str(i) for i in range(12))+"]});\n",'utf-8')
config=ROOT/'motion-canvas/vite.character-parameters.black-preflight-v1.config.ts';assert not config.exists()
template=(ROOT/'motion-canvas/vite.presenting-game-scores.black-preflight-v1.config.ts').read_text('utf-8-sig')
template=template.replace('scorePreflightThreadsCapped','characterPreflightThreadsCapped').replace('port:9251','port:9252').replace('./src/projects/presenting-game-scores/black-explanation-preflight-v1.ts','./src/projects/character-parameters/black-structural-preflight-v1.ts').replace('../shared/output/presenting-game-scores/black-structural-preview-v1','../shared/output/character-parameters/black-structural-preview-v1')
config.write_text(template,'utf-8')
tsconfig=ROOT/'motion-canvas/tsconfig.character-parameters.json';assert not tsconfig.exists()
tsconfig.write_text(json.dumps(dict(extends='./tsconfig.json',include=['src/projects/character-parameters','src/env.d.ts']),indent=2)+'\n','utf-8')
paths=[entry,MC/'spatial-character-explanation.tsx',MC/'prototype-timing-v1.ts',*scene_dir.glob('*.tsx'),config,tsconfig]
audit=dict(preparedAt=datetime.now(timezone.utc).isoformat(),independentScenes=12,pairedParagraphs=37,style='research-black-v1',
    prototypeSceneSeconds=12,voiceMeasured=False,fullAnimationDirectlyReviewed=False,finalPixelsApproved=False,
    narrationFilesModified=False,protectedRequestInputsModified=False,ownMemberRendered=False,
    paths=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths])
(BASE/'prepared-independent-mc-v1.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Twelve independent spatial prototype scenes prepared; voice/final timing/pixel approval remain pending.')
