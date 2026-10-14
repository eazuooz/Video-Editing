"""Record the actual outer exec session; do not mutate a live worker's state."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, psutil
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,o):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
me=psutil.Process(32256)
assert abs(me.create_time()-1791707910.108907)<.01
assert 'render-motion-four-additions-v4.py' in ' '.join(me.cmdline())
assert Path(me.cwd()).resolve()==ROOT
lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
assert lease['project']=='motion-sickness-games' and lease['token']=='a5373dcb-af59-4431-b6b9-41eb1b89f07a'
session=dict(sessionId=66238,actualCommand='D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe -X utf8 -u production/batches/cross-game-example-coverage-review/render-motion-four-additions-v4.py',
    cwd=str(ROOT),actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),recordedAt=now(),
    retryOfActualSession=58747,actualOuterExitCode=None,actualExitObserved=False,newVoiceScenes=3,newPairedParagraphs=15,
    original14PcmRegeneration=0,ownedLeaseToken=lease['token'],coordinator=lease['coordinator'],
    preflight='voice-retry-resource-verification-v5.json',foreignResearchRestorationIsOwn=False)
assert not (R/'narration-tts-session-v4.json').exists()
save(R/'narration-tts-session-v4.json',session)
cp=read(R/'latest-checkpoint.json')
cp.update(recordedAt=now(),stage='single-v4-owned-boundary-request-awaiting-stable-GPU-before-model',
    actualOuterSession=66238,actualOuterExitCode=None,currentOwnedVoiceWorkerAlive=True,currentOwnedGpuJobs=0,
    ttsStarted=False,researchResumeVerified=False,currentForeignHandoff=None,
    currentOwnedHandoff=dict(token=lease['token'],state=lease['state'],coordinator=lease['coordinator']),
    ownedJob=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=66238,
        state='projects/motion-sickness-games/production/revision-cross-game-four-v1/narration-tts-waiting-v4.json',gpuJobs=0,exitCode=None),
    next='Observe this actual session only; after its actual outer exit verify owned research restoration, then current whole3 and independent15 ASR. Preserve baseline schedule until reviewed replacement.')
save(R/'latest-checkpoint.json',cp)
qp=Path(__file__).parent/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
q['currentMotionReview'].update(status=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next']);q['updatedAt']=now()
assert qp.read_text('utf-8-sig')==raw;save(qp,q)
src=Path(__file__).parent/'review-motion-four-additive-voice-v2.py';dst=src.with_name('review-motion-four-additive-voice-v3.py')
assert not dst.exists()
code=src.read_text('utf-8-sig').replace('narration-tts-execution-v3.json','narration-tts-execution-v4.json').replace('research-handoff-verification-v3.json','research-handoff-verification-v4.json').replace('narration-tts-session-v3.json','narration-tts-session-v4.json')
compile(code,str(dst),'exec');dst.write_text(code,'utf-8')
print('Actual66238/PID32256/ownedlease recorded; ASR v3 prepared only/model0.')
