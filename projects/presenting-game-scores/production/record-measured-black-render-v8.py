"""Record actual UI-initiated encoder identity; never start/stop a job."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,psutil
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
stamp=datetime.now(timezone.utc).isoformat()
path=BASE/'measured-black-render-execution-v8.json'; assert not path.exists()
p=psutil.Process(6124);cmd=p.cmdline()
assert abs(p.create_time()-1791534180.420467)<.02
assert p.ppid()==63080 and cmd[-1].endswith('presenting-game-scores-measured-black-v8.mp4')
assert '-threads' in cmd and cmd[cmd.index('-threads')+1]=='2'
prep=read(BASE/'measured-mc-frame-exact-preparation-v8.json')
for key in ('engine','renderEntry','liveEntry'):
 assert hashlib.sha256((ROOT/prep[key]).read_bytes()).hexdigest()==prep[key+'Sha256']
state=dict(schemaVersion=8,observedAt=stamp,slug='presenting-game-scores',stage='measured-black-input-render-running',actualPid=p.pid,createTime=p.create_time(),command=cmd,cwd=p.cwd(),parentPid=63080,viteSessionId=31622,encoderSessionId=None,encoderStartedThroughCua=True,uiTabId='136',uiRenderProject='presenting-game-scores-measured-black-v8',uiPlannedDurationFrames=7333,uiRenderFps=60,width=1920,height=1080,cpuThreads=2,filterThreads=1,ffmpegHardwareEncoder=False,exitCode=None,exitDirectlyObserved=False,alive=True,output='shared/output/presenting-game-scores/black-structural-preview-v1/presenting-game-scores-measured-black-v8.mp4',resourceProof='projects/presenting-game-scores/production/measured-black-render-resource-v8.json',preparation='projects/presenting-game-scores/production/measured-mc-frame-exact-preparation-v8.json',priorMeasuredV7SourcesPreserved=True,staleTab135ObservationTimeout=True,newTabUsesExisting9251Server=True,serverRestarted=False,rawCuaRenderAction='RENDER became ABORT with elapsed/ETA at17:23KST',logSource='existing Vite session31622 and CUA UI; separate encoder exit remains unobserved',finalTimingApproved=False,allFinalPixels=False,finalMixedAsrApproved=False,qaApproved=False,collected=False,private=False,nextAction='Observe actual encoder/output/UI. After finished verify frames/PTS/decode and every measured caption/motion pixel; no repeated source/native/TTS/ASR.')
path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=stamp,stage=state['stage'],ownedJob=state,nextAction=state['nextAction'])
(BASE/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
 item.update(stage=state['stage'],currentExecution=path.relative_to(ROOT).as_posix(),currentJob=state,nextAction=state['nextAction'])
 q.update(updatedAt=stamp,lastProgressAt=stamp)
 if qp.read_text('utf-8-sig')==raw:
  qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8');break
else:raise RuntimeError('Concurrent queue change preserved')
print(json.dumps(dict(actualPid=p.pid,createTime=p.create_time(),alive=p.is_running(),plannedFrames=7333,cpuThreads=2)))
