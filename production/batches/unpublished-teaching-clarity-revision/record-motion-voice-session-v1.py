"""Record actual single waiting wrapper; never restart it or touch a foreign lease."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,psutil
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
ap=argparse.ArgumentParser();ap.add_argument('--session-id',type=int,required=True);a=ap.parse_args()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
wait=read(R/'narration-tts-waiting-v1.json')
p=psutil.Process(wait['actualPid']);assert abs(p.create_time()-wait['createTime'])<.01
assert p.cwd().lower()==str(ROOT).lower()
assert 'render-motion-additions-v1.py' in ' '.join(p.cmdline())
for x in wait['protectedInputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
now=datetime.now(timezone.utc).isoformat()
data=dict(schemaVersion=1,recordedAt=now,sessionId=a.session_id,pid=p.pid,createTime=p.create_time(),
    commandLine=p.cmdline(),cwd=p.cwd(),stage='serialized-wait-before-model',
    actualOuterExitCode=None,workerAlive=True,modelLoaded=False,ownGpuJobs=0,
    externalLeaseSnapshot=wait['foreignLease'],ownResearchPauseOrProcessChanges=0,
    protectedInputsUnchanged=True,protectedInputCount=len(wait['protectedInputs']),
    next='Inspect actual followup/exit before waiting again; preserve external lighting handoff, then verify own TTS and original research resume.')
path=R/'narration-tts-session-v1.json';assert not path.exists();path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
c=read(R/'latest-checkpoint.json');c.update(recordedAt=now,stage=data['stage'],ownedJob=data,ttsStarted=False)
(R/'latest-checkpoint.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8')
qpath=B/'queue.json';q=read(qpath);q['execution'].update(stage=data['stage'],ownedJob=data,next=data['next']);q['updatedAt']=now
next(x for x in q['items'] if x['slug']=='motion-sickness-games').update(status='single-serialized-additive-voice-request-before-model',currentExecution=data)
qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(sessionId=a.session_id,pid=p.pid,workerAlive=True,modelLoaded=False,ownGpuJobs=0,protectedInputsUnchanged=True)))
