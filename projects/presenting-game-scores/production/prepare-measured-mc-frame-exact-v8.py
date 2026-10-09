"""Preserve v7; replace float tween duration with integer frame stepping."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
MC=ROOT/'motion-canvas/src/projects/presenting-game-scores'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
planp=BASE/'measured-timeline-candidate-v7.json'
plan=read(planp)
prior=read(BASE/'measured-mc-preparation-v7.json')
assert sha(planp)==prior['planSha256']
engine_old=ROOT/prior['engine']
assert sha(engine_old)==prior['engineSha256']
engine=MC/'measured-score-explanation-frame-exact-v8.tsx'
assert not engine.exists()
text=engine_old.read_text('utf-8').replace("import {createSignal,linear} from '@motion-canvas/core';", "import {createSignal,usePlayback} from '@motion-canvas/core';")
text=text.replace('scoreExplanationMeasuredV7','scoreExplanationMeasuredV8')
target=' yield* t(timing.durationSeconds,timing.durationSeconds,linear);'
assert text.count(target)==1
text=text.replace(target," // Integer steps avoid float thread end-time comparisons adding a frame.\n const fps=usePlayback().fps;\n const frames=Math.round(timing.durationSeconds*fps);\n for(let frame=0;frame<frames;frame++){t(frame/fps);yield;}\n t(timing.durationSeconds);")
engine.write_text(text,'utf-8')
folder=MC/'measured-black-scenes-v8';assert not folder.exists();folder.mkdir()
files=[];imports=[]
black=[s for s in plan['segments'] if s['role']=='explanation']
for i,s in enumerate(black):
 p=folder/(s['id']+'.tsx')
 timing=dict(durationSeconds=s['frames']/60,paragraphStarts=s['paragraphMotionStarts'],measured=True)
 p.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {scoreExplanationMeasuredV8} from '../measured-score-explanation-frame-exact-v8';\n"+f"export default makeScene2D(function* (view) {{yield* scoreExplanationMeasuredV8(view,{json.dumps(s['diagram'])},{json.dumps(timing)});}});\n",'utf-8')
 files.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),id=s['id'],frames=s['frames']))
 imports.append(f"import s{i:02} from './measured-black-scenes-v8/{s['id']}?scene';")
entry=MC/'measured-black-v8.ts';assert not entry.exists()
entry.write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(imports)+"\nexport default makeProject({name:'presenting-game-scores-measured-black-v8',scenes:["+','.join(f's{i:02}' for i in range(len(black)))+"]});\n",'utf-8')
live=MC/'black-explanation-preflight-v1.ts'
assert sha(live)==prior['liveRegisteredEntrySha256']
live.write_text("// Integer-frame measured input. All v7 scenes and render entry remain preserved.\nexport {default} from './measured-black-v8';\n",'utf-8')
proof=dict(schemaVersion=8,preparedAt=datetime.now(timezone.utc).isoformat(),plan=planp.relative_to(ROOT).as_posix(),planSha256=sha(planp),reason='UI v7 preview at60fps reported7339 versus planned7333; source tween uses endTime>thread.fixed float comparison. Integer generator stepping preserves exact planned frame durations.',priorEngine=prior['engine'],priorEngineSha256=sha(engine_old),priorMeasuredSceneFilesPreserved=True,engine=engine.relative_to(ROOT).as_posix(),engineSha256=sha(engine),renderEntry=entry.relative_to(ROOT).as_posix(),renderEntrySha256=sha(entry),liveEntry=live.relative_to(ROOT).as_posix(),liveEntrySha256=sha(live),blackSegments=files,totalBlackFrames=sum(s['frames'] for s in black),uiDurationVerified=False,newRenderStarted=False,serverRestarted=False,allFinalPixels=False,finalMixedAsrApproved=False,finalTimingApproved=False,newImagesGitAdded=0)
out=BASE/'measured-mc-frame-exact-preparation-v8.json';assert not out.exists()
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(blackSegments=len(files),frames=proof['totalBlackFrames'],priorPreserved=True,preparedOnly=True)))
