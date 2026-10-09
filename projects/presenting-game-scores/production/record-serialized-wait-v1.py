from pathlib import Path
from datetime import datetime,timezone
import json,os,psutil,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
now=lambda:datetime.now(timezone.utc).isoformat()
w=read(BASE/'narration-tts-waiting-v1.json');p=psutil.Process(w['actualPid'])
assert abs(p.create_time()-w['createTime'])<.01 and 'presenting-game-scores/production/render-voice-v1.py' in ' '.join(p.cmdline())
session=dict(schemaVersion=1,slug='presenting-game-scores',sessionId=30677,recordedAt=now(),pid=p.pid,
 createTime=p.create_time(),commandLine=p.cmdline(),log='projects/presenting-game-scores/production/narration-tts-waiting-v1.log',
 stage='serialized-request-waiting-before-model',gpuJobs=0,cpuThreads=2,ttsStarted=False,
 actualForeignLease=w['foreignLease'],ownedResearchPauseOrProcessChanges=0)
save(BASE/'narration-tts-session-v1.json',session)
c=read(BASE/'latest-checkpoint.json');c.update(recordedAt=now(),stage=session['stage'],ownedJob=session,
 nextAction='Observe actual waiting wrapper/foreign lease without starting another GPU job. Continue independent black spatial code; after lease release own coordinator handles research boundary and mandatory resume.');save(BASE/'latest-checkpoint.json',c)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(8):
 raw=qpath.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
 i.update(stage=c['stage'],currentExecution=session,ttsStarted=False,nextAction=c['nextAction'])
 i['checkpoints']['script']=True;i['preflight']['newProjectCreated']=True
 i['preflight'].update(currentChangedContentReview='production/batches/sakurai-planning-game-design/proof-presenting-game-scores/content-studio-change-review-v3.json',
  inputsDigest=read(ROOT/'production/batches/sakurai-planning-game-design/preflight/presenting-game-scores.json')['inputsDigest'],needsCurrentDuplicateCheckBeforeProjectCreation=False)
 i['scriptReview']='projects/presenting-game-scores/production/paired-script-direct-review-v1.json'
 q['updatedAt']=now()
 if qpath.read_text('utf-8-sig')==raw:save(qpath,q);break
 time.sleep(.1)
else:raise RuntimeError('Concurrent queue changed; retry after inspecting current file')
print(json.dumps(dict(pid=p.pid,sessionId=30677,alive=True,modelLoaded=False,ownPauseChanges=0)))
