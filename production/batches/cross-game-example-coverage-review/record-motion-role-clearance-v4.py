"""Seal83 encoded samples; prepare eight-piece normal1x review only."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil,os
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
s=read(R/'remaining-action-roles-execution-v4.json');assert s['exitCode']==0 and s['encodedSampleCount']==83 and s['boardCount']==22 and not psutil.pid_exists(s['pid'])
stamp=datetime.now(timezone.utc).isoformat();bound=[]
for p in s['pieces']:
 for row in [dict(path=p['path'],sha256=p['sha256'])]+p['samples']+p['boards']:
  assert sha(ROOT/row['path'])==row['sha256'];bound.append(dict(path=row['path'],sha256=row['sha256']))
proof=R/'remaining-action-roles-sampled-direct-review-v4.json';assert not proof.exists()
save(proof,dict(schemaVersion=1,recordedAt=stamp,actualSession=15420,actualCompletion='7770a9',actualOuterExitCode=0,actualWorkerAbsent=True,encodedSamplesDirectlyRead=83,boardsDirectlyRead=22,shaBoundFiles=bound,
 observations=['Laser red label moved below object at720..777, preserving original blue-X/yellow-check display.','Cyan mark native2352..2382 follows visible connection/status. Encoded509/510 blue;524..570 yellow;571 onward hidden before fast view change.','Alyx red plank mark encoded129..181 follows visible foreground plank;182 onward hidden including255/285 uncertain view; hand removal and destination remains original unmarked action.','Credit/sourceHUD preserved and bottom900..1080 reserved for final fixed captions.'],
 selectedMovingSampleAlignmentPassed=True,normalSpeedPlaybackApproved=False,allIntermediateFramesApproved=False,continuousListeningApproved=False,allNarrationTimedMovingPixelsApproved=False,finalVideoApproved=False,localOnly=True))
s.update(actualSession=15420,actualOuterExitCode=0,actualCompletion='7770a9',actualWorkerAbsent=True,status='sampled-clear-awaiting-normal1x-and-final-timed-cues',directReview=proof.name);save(R/'remaining-action-roles-execution-v4.json',s)
base=read(R/'remaining-action-roles-execution-v1.json');replacement={p['id']:p for p in s['pieces']};pieces=[replacement.get(p['id'],p) for p in base['pieces']];assert len(pieces)==8
helper=psutil.Process(27140);assert 'serve-native-review-v1.py' in ' '.join(helper.cmdline())
webroot=ROOT/'shared/assets/presenting-game-scores/raw';items=[]
for i,p in enumerate(pieces):
 assert sha(ROOT/p['path'])==p['sha256'];name=f'motion-role-current-{i:02d}-v4.mp4';target=webroot/name
 assert not target.exists();os.link(ROOT/p['path'],target);assert os.path.samefile(ROOT/p['path'],target)
 items.append(dict(id=p['id'],path=p['path'],sha256=p['sha256'],url='http://127.0.0.1:9250/'+name,frames=p['frames']))
html='''<!doctype html><meta charset="utf-8"><title>Motion remaining role review V4</title><style>body{background:#111;color:white;font:20px sans-serif}video{width:960px;display:block}button{font:18px sans-serif;margin:8px}</style><h1>Eight source windows · normal1× · silent roles</h1><select id="choice"></select><button id="load">Load selected</button><button id="play">Play1×</button><button id="pause">Pause</button><video id="video" controls muted></video><pre id="status"></pre><script>const items=ITEMS;const choice=document.querySelector('#choice'),v=document.querySelector('video'),st=document.querySelector('#status');items.forEach((x,i)=>choice.add(new Option(x.id,i)));document.querySelector('#load').onclick=()=>{v.pause();v.src=items[choice.value].url;v.load()};document.querySelector('#play').onclick=()=>{v.muted=true;v.playbackRate=1;v.play()};document.querySelector('#pause').onclick=()=>v.pause();setInterval(()=>st.textContent=JSON.stringify({id:items[choice.value].id,currentTime:v.currentTime,duration:v.duration,paused:v.paused,ended:v.ended,rate:v.playbackRate,muted:v.muted}),100);v.src=items[0].url;</script>'''.replace('ITEMS',json.dumps(items,ensure_ascii=False))
hp=webroot/'motion-remaining-role-normal-review-v4.html';assert not hp.exists();hp.write_text(html,'utf-8')
save(R/'remaining-action-normal-playback-plan-v4.json',dict(preparedAt=stamp,items=items,html=hp.relative_to(ROOT).as_posix(),helperPid=helper.pid,helperCreateTime=helper.create_time(),serverStarted=False,localOnly=True,normalPlaybackObserved=False))
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=stamp,activeOwnedWorkers=0,ownedJob=dict(active=False,sessionId=15420,exitCode=0,completion='7770a9'),remainingActionSampledReview=proof.name,stage='remaining-role-sampled-clear-normal-playback-pending',currentDuplicateCheckPassed=False,next='Normal1x eight current pieces then refresh changed duplicate inputs and Studio before current17 mix. Preserve completed83/22 and prior source/audio/QA; no duplicate renders.');save(R/'latest-checkpoint.json',cp)
print(json.dumps(dict(exitCode=0,samples=83,boards=22,shaBoundFiles=len(bound),helperReused=True,eightReviewItems=8,finalApproved=False)))
