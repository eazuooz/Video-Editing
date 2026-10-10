"""Prepare frame stepping without creating measured scene timings or rendering."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas/src/projects/character-parameters'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=read(BASE/'black-structural-direct-review-v3.json');old=MC/'spatial-character-explanation.tsx'
assert review['prototypeStructuralPixelReviewApproved'] and sha(old)==review['sourceSha256']
path=MC/'spatial-character-explanation-frame-exact-v1.tsx';assert not path.exists()
text=old.read_text('utf-8-sig').replace("import {createSignal,linear} from '@motion-canvas/core';","import {createSignal,usePlayback} from '@motion-canvas/core';").replace('export function* characterExplanation(', 'export function* characterExplanationFrameExact(')
target=' yield* t(timing.durationSeconds,timing.durationSeconds,linear);'
assert text.count(target)==1
text=text.replace(target," if(!timing.measured)throw Error('Frame-exact input requires reviewed measured timing');\n const fps=usePlayback().fps;\n const frames=Math.round(timing.durationSeconds*fps);\n if(fps!==60||Math.abs(frames/fps-timing.durationSeconds)>1e-7)throw Error('Measured input must use an integer 60fps duration');\n for(let frame=0;frame<frames;frame++){t(frame/fps);yield;}\n t(timing.durationSeconds);")
path.write_text(text,'utf-8')
proof=dict(preparedAt=datetime.now(timezone.utc).isoformat(),source=old.relative_to(ROOT).as_posix(),sourceSha256=sha(old),structuralReview=(BASE/'black-structural-direct-review-v3.json').relative_to(ROOT).as_posix(),frameExactEngine=path.relative_to(ROOT).as_posix(),frameExactEngineSha256=sha(path),purpose='Preserve directly reviewed geometry and replace float tween duration with integer 60fps generator stepping after actual narration alignment.',preparedOnly=True,voiceTimingApproved=False,measuredSceneWrappersCreated=False,registeredInLiveEntry=False,newRenderStarted=False,finalPixelsApproved=False)
(BASE/'prepared-frame-exact-engine-v1.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Prepared frame-exact geometry helper only. No measured scene timing, live entry switch or render.')
