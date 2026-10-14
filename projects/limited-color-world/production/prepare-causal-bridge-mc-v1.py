"""Add three independent causal bridges; preserve the prepared original8 scenes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas/src/projects/limited-color-world'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
request=read(BASE/'narration-tts-request-v1.json')
assert all(sha(ROOT/x['path'])==x['sha256'] for x in request['protectedInputs'])
old=read(BASE/'prepared-independent-mc-v1.json')
assert all(sha(ROOT/x['path'])==x['sha256'] for x in old['files'])
review=read(BASE/'causal-bridge-paired-direct-review-v1.json')
assert review['all3PairedBridgeParagraphsDirectlyRead'] and review['original24ParagraphsAndOrderPreserved']
plan=read(BASE.parent/'planning/causal-chain-additions-v1.json')
created=[MC/'spatial-causal-bridges.tsx']
for number,b in enumerate(plan['preparedAdditions']):
    path=MC/'scenes'/f"{b['id']}.tsx";meta=path.with_suffix('.meta')
    assert not path.exists() and not meta.exists()
    path.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {causalColorBridge} from '../spatial-causal-bridges';\nexport default makeScene2D(function* (view) {\n  // Structural prototype only. Replace12s after independent bridge PCM measurement.\n  yield* causalColorBridge(view,'"+b['id']+"',12);\n});\n",encoding='utf-8')
    meta.write_text(json.dumps(dict(version=0,timeEvents=[],seed=701001+number),indent=2)+'\n',encoding='utf-8')
    created.extend([path,meta])
ids=['01-overview','02-contours','03-pattern-and-erasing','03b-static-to-state','04-height-and-motion','05-state-not-hue','06-route-information','06b-outline-to-contrast','07-local-contrast','07b-cues-to-check','08-check-and-conclusion']
project=MC/'black-structural-preflight-v2.ts';meta=project.with_suffix('.meta')
assert not project.exists() and not meta.exists()
text="import {makeProject} from '@motion-canvas/core';\n"+''.join(f"import scene{i} from './scenes/{id}?scene';\n" for i,id in enumerate(ids))
text+="export default makeProject({name:'limited-color-world-black-structural-preflight-v2',scenes:["+','.join(f'scene{i}' for i in range(len(ids)))+"]});\n"
project.write_text(text,encoding='utf-8');meta.write_bytes((MC/'black-structural-preflight-v1.meta').read_bytes());created.extend([project,meta])
config=ROOT/'motion-canvas/vite.limited-color-world.black-preflight-v2.config.ts';assert not config.exists()
config.write_text((config.with_name('vite.limited-color-world.black-preflight-v1.config.ts')).read_text(encoding='utf-8').replace('black-structural-preflight-v1','black-structural-preflight-v2'),encoding='utf-8');created.append(config)
assert all(sha(ROOT/x['path'])==x['sha256'] for x in old['files'])
assert all(sha(ROOT/x['path'])==x['sha256'] for x in request['protectedInputs'])
out=BASE/'prepared-causal-bridge-mc-v1.json';assert not out.exists()
record=dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),
    independentOriginalScenes=8,independentBridgeScenes=3,orderedSceneIds=ids,
    prototypeSecondsPerScene=12,measuredBridgeTiming=False,
    original8SourceFilesPreserved=True,original10VoiceInputsPreserved=True,
    bridgeNarrationPlan=rel(BASE.parent/'planning/causal-chain-additions-v1.json'),
    bridgeNarrationRequested=False,sourceRendering=False,serverStarted=False,renderStarted=False,
    actualMovingPixelReview=False,continuousNarrationAndPixelsApproved=False,finalCausalFlowApproved=False,
    futureSinglePreviewPort=9253,files=[dict(path=rel(p),sha256=sha(p)) for p in created],
    nextAction='ScopedTypeScript check only. Finish actual8scene TTS/restoration/full voice review, then synthesize the3 preserved bridge paragraphs in one serialized protected batch. Measure all PCM and allocate unique action/explanation time before final timed animation/pixel/causal-flow approval.')
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared3 independent projected bridge scenes and11-scene causal prototype; original8/source/request preserved. Render/model/bridgeTTS0.')
