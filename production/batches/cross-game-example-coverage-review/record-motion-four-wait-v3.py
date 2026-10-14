from pathlib import Path
from datetime import datetime,timezone
import json,psutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
w=read(R/'narration-tts-waiting-v3.json');p=psutil.Process(w['actualPid']);assert abs(p.create_time()-w['createTime'])<.01
assert p.cmdline()==w['commandLine'] and p.cwd()==w['cwd']
s=dict(sessionId=58747,actualCommand='D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe -X utf8 production/batches/cross-game-example-coverage-review/render-motion-four-additions-v3.py',
 cwd=w['cwd'],actualOuterExitCode=None,retryOfActualSession=46624,newVoiceScenes=3,newPairedParagraphs=15,original14PcmRegeneration=0,
 actualPid=p.pid,createTime=p.create_time(),foreignLeaseAtWait=w['foreignLease'])
save(R/'narration-tts-session-v3.json',s)
c=read(R/'latest-checkpoint.json');c.update(recordedAt=datetime.now(timezone.utc).isoformat(),
 stage='single-v3-voice-request-waiting-for-foreign-handoff-before-model',actualOuterSession=58747,actualOuterExitCode=None,
 ownedJob=dict(sessionId=58747,pid=p.pid,createTime=p.create_time(),state='waiting-before-model',gpuJobs=0),
 next='Reuse actual58747 and latest V3 state; no second request. After actual exit verify own lease/research restoration, then current whole3 and independent15 ASR.')
save(R/'latest-checkpoint.json',c)
qp=ROOT/'production/batches/cross-game-example-coverage-review/queue.json';q=read(qp)
q['currentMotionReview']['ownedJob']=c['ownedJob'];q['currentMotionReview']['structuralReview']=str((R/'structural-prototype-direct-review-v1.json').relative_to(ROOT));save(qp,q)
src=Path(__file__).with_name('review-motion-four-additive-voice-v1.py');target=src.with_name('review-motion-four-additive-voice-v2.py')
assert not target.exists();body=src.read_text('utf-8-sig').replace('narration-tts-execution-v2.json','narration-tts-execution-v3.json').replace('research-handoff-verification-v2.json','research-handoff-verification-v3.json').replace('narration-tts-session-v2.json','narration-tts-session-v3.json')
target.write_text(body,'utf-8')
print('Actual58747 single waiting request recorded; CPU ASR V2 prepared only, model/state0.')
