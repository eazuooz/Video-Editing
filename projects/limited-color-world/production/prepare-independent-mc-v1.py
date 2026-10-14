"""Prepare independent structural scenes, without changing voice inputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas';P=MC/'src/projects/limited-color-world'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def write(p,s):
 assert not p.exists(),f'Preserve existing prepared file: {p}'
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
request=read(BASE/'narration-tts-request-v1.json')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
ids=[s['id'] for s in request['scenes']]
assert len(ids)==8 and sum(s['paragraphs'] for s in request['scenes'])==24
files=[]
def add(p,s):write(p,s);files.append(p)
timings={i:dict(durationSeconds=12,paragraphStarts=[0,4,8],measured=False) for i in ids}
add(P/'prototype-timing-v1.ts',"// Structural prototype only: not measured narration or final allocation.\nimport type {ColorTiming} from './spatial-color-explanation';\nexport const PROTOTYPE_TIMING:Record<string,ColorTiming>="+json.dumps(timings,indent=2)+';\n')
for num,i in enumerate(ids):
 add(P/'scenes'/f'{i}.tsx',"import {makeScene2D} from '@motion-canvas/2d';\nimport {colorExplanation} from '../spatial-color-explanation';\nimport {PROTOTYPE_TIMING} from '../prototype-timing-v1';\nexport default makeScene2D(function* (view) {\n  yield* colorExplanation(view,'"+i+"',PROTOTYPE_TIMING['"+i+"']);\n});\n")
 add(P/'scenes'/f'{i}.meta',json.dumps(dict(version=0,timeEvents=[],seed=681710+num),indent=2)+'\n')
entry="import {makeProject} from '@motion-canvas/core';\n"+''.join(f"import scene{n} from './scenes/{i}?scene';\n" for n,i in enumerate(ids))
entry+="export default makeProject({name:'limited-color-world-black-structural-preflight-v1',scenes:["+','.join(f'scene{n}' for n in range(8))+']});\n'
add(P/'black-structural-preflight-v1.ts',entry)
meta=dict(version=0,shared=dict(background=None,range=[0,None],size=dict(x=1920,y=1080),audioOffset=0),
 preview=dict(fps=60,resolutionScale=1),rendering=dict(fps=60,resolutionScale=1,colorSpace='srgb',
 exporter=dict(name='@motion-canvas/ffmpeg',options=dict(fastStart=True,includeAudio=False))))
add(P/'black-structural-preflight-v1.meta',json.dumps(meta,indent=2)+'\n')
add(MC/'tsconfig.limited-color-world.json',json.dumps({'extends':'./tsconfig.json','include':['src/projects/limited-color-world','src/env.d.ts']},indent=2)+'\n')
config=(MC/'vite.character-parameters.black-preflight-v1.config.ts').read_text('utf-8-sig')
config=config.replace('characterPreflightThreadsCapped','limitedColorPreflightThreadsCapped').replace('character-parameters','limited-color-world').replace('port:9252','port:9253')
add(MC/'vite.limited-color-world.black-preflight-v1.config.ts',config)
files.append(P/'spatial-color-explanation.tsx')
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
audit=dict(schemaVersion=1,slug='limited-color-world',preparedAt=datetime.now(timezone.utc).isoformat(),
 independentScenes=8,pairedParagraphs=24,prototypeSecondsPerScene=12,prototypeOnly=True,measuredNarrationTiming=False,
 projection='XYZ floor and height, yaw, perspective, real front/side/top faces, depth sorting and occlusion. Roof slopes, height changes and restricted cave light are spatial comparisons.',
 sourceGameRenderingCreated=False,membershipRenderingCreated=False,renderStarted=False,serverStarted=False,
 currentVoiceRequestInputsUnchanged=True,prototypeStructuralPixelReviewApproved=False,continuousAnimationReview=False,
 allFinalPixelsApproved=False,finalTimingApproved=False,files=[dict(path=rel(p),sha256=sha(p)) for p in files],
 nextAction='Run scoped TypeScript check. Start one structural preview only after fresh resources and port availability; review actual animated pixels. Prototype12s is never measured narration/final60:40.')
write(BASE/'prepared-independent-mc-v1.json',json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print('Prepared8 independent spatial scenes and one scoped prototype entry; voice10inputs preserved. Rendering/server/pixel approval0.')
