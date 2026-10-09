"""Generate independent measured black scenes only after current voice adoption."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).parent;B=P/'revision-balatro60-v2'
MC=ROOT/'motion-canvas/src/projects/presenting-game-scores'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
planp=B/'measured-editorial-candidate-v3.json';plan=read(planp)
voicep=ROOT/plan['voiceSelection'];voice=read(voicep)
assert sha(voicep)==plan['voiceSelectionSha256'] and voice['currentCompleteVoiceApproved']
assert plan['mathRatioVerified'] and plan['measuredEditorialApproved'] and plan['currentCompleteVoiceApproved']
engine=MC/'revision-spatial-score-explanation-v2.tsx';assert engine.exists()
folder=MC/'revision-black-scenes-v3';entry=MC/'revision-black-v3.ts';proof=B/'measured-mc-preparation-v3.json'
assert not folder.exists() and not entry.exists() and not proof.exists(),'Preserve existing render preparation'
black=[s for s in plan['segments'] if s['role']=='explanation'];assert len(black)==13
folder.mkdir();imports=[];files=[]
for i,s in enumerate(black):
 assert 0<=s['paragraphMotionStarts'][0] and max(s['paragraphMotionStarts'])<s['frames']/60
 p=folder/(s['id']+'.tsx');timing=dict(durationSeconds=s['frames']/60,paragraphStarts=s['paragraphMotionStarts'],measured=True)
 p.write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {scoreExplanationBalatroRevisionV2} from '../revision-spatial-score-explanation-v2';\n"+f"export default makeScene2D(function* (view) {{yield* scoreExplanationBalatroRevisionV2(view,{json.dumps(s['diagram'])},{json.dumps(timing)});}});\n",'utf-8')
 files.append(dict(id=s['id'],path=rel(p),sha256=sha(p),frames=s['frames'],paragraphMotionStarts=s['paragraphMotionStarts']))
 imports.append(f"import s{i:02} from './revision-black-scenes-v3/{s['id']}?scene';")
entry.write_text("import {makeProject} from '@motion-canvas/core';\n"+'\n'.join(imports)+"\nexport default makeProject({name:'presenting-game-scores-balatro60-black-v3',scenes:["+','.join(f's{i:02}' for i in range(len(black)))+"]});\n",'utf-8')
live=MC/'black-explanation-preflight-v1.ts';old=live.read_bytes()
live.write_text("// Approved measured revision; prior baseline entry and scenes are preserved.\nexport {default} from './revision-black-v3';\n",'utf-8')
j=dict(schemaVersion=3,preparedAt=datetime.now(timezone.utc).isoformat(),plan=rel(planp),planSha256=sha(planp),engine=rel(engine),engineSha256=sha(engine),renderEntry=rel(entry),renderEntrySha256=sha(entry),liveEntry=rel(live),liveEntrySha256=sha(live),priorLiveEntryBytesUtf8=old.decode('utf-8'),priorLiveEntrySha256=hashlib.sha256(old).hexdigest(),blackSegments=files,totalBlackFrames=sum(s['frames'] for s in black),priorScenesAndRendersPreserved=True,independentSceneCount=len(files),uiDurationVerified=False,newRenderStarted=False,allFinalPixels=False,finalTimingApproved=False,finalMixedAsrApproved=False,newImagesGitAdded=0,serverRestarted=False)
proof.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedOnly=True,segments=len(files),frames=j['totalBlackFrames'],sceneFilesCreated=True,renderStarted=False)))
