"""Update only this motion queue entry using current actual evidence."""
from pathlib import Path
import json,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
qpath=B/'queue.json';raw=qpath.read_bytes();q=json.loads(raw.decode('utf-8-sig'));cp=json.loads((R/'latest-checkpoint.json').read_text('utf-8-sig'))
v=q['currentMotionReview'];assert v['baselineVideoId']=='mBDd9VzSTkA'
v.update(currentHandoff='projects/motion-sickness-games/production/revision-cross-game-four-v1/resource-and-annotation-handoff-v18.json',stage=cp['stage'],status=cp['stage'],next=cp['next'],currentStudioScheduleVerified=False,currentStudioVisibility='Private',historicalScheduledAt=v['scheduledAt'],currentStudioScheduleInterpretation='Latest actual CUA98 Private selected; historical scheduledAt is retained history only. Recheck live Studio/ledger after reviewed replacement.',activeOwnedWorkers=cp['activeOwnedWorkers'],currentMixedAsrExecution='projects/motion-sickness-games/production/revision-cross-game-four-v1/current17-mixed-whole-asr-execution-v3.json',remainingActionSampledReview='projects/motion-sickness-games/production/revision-cross-game-four-v1/remaining-action-roles-sampled-direct-review-v4.json',currentMixedAudioApproved=False)
assert qpath.read_bytes()==raw;t=qpath.with_name(qpath.name+'.writing');t.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,qpath)
print(json.dumps(dict(ownEntryOnly=True,baselinePrivate=True,currentScheduleVerified=False,active=cp['activeOwnedWorkers'])))
