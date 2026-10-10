from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def save(p,v):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def normalized(x,key):return json.loads(x[key]) if isinstance(x[key],str) else x[key]
pair=read(R/'final-pair-execution-v2.json');session=read(R/'final-pair-execution-v2.session.json')
pix=read(R/'final-pixel-direct-review-v2.json');audio=read(R/'current-mixed-complete-direct-review-v1.json')
assert pair['exitCode']==session['actualOuterExitCode']==0 and not session['workerCurrentlyAlive']
assert pix['allFinalCueCutPixelsApproved'] and not pix['unresolved'] and audio['currentMixedContentReviewPassed']
end=read(R/'final-flow-ended-observation-v2.json');status=normalized(end,'status');events=normalized(end,'events')
assert status['ended'] and status['paused'] and status['muted'] and status['playbackRate']==1
assert abs(status['currentTime']-669.883333)<.0001 and abs(status['duration']-669.883333)<.0001
assert [x['event'] for x in events]==['play','seeked','pause','ended']
assert events[1]['currentTime']<.02 and events[-1]['currentTime']==669.883333
assert all(x['muted'] and x['rate']==1 for x in events)
selected=read(R/'final-flow-targets-selected-observation-v2.json')
assert selected['sourceSha256']==pix['sourceSha256']==pair['pair'][1]['sha256']
assert selected['scene02LateComparisonObservedAtNormalSpeed'] and selected['scene06bTo07ObservedAtNormalSpeed']
assert not selected['unresolved'] and not selected['allIntermediateFramesViewed']
now=datetime.now(timezone.utc).isoformat()
out=R/'final-flow-playback-direct-review-v2.json';assert not out.exists()
save(out,dict(schemaVersion=1,recordedAt=now,status='current-normal1x-playback-ended-and-selected-causal-flow-reviewed',
 source=pair['pair'][1]['path'],sourceSha256=pair['pair'][1]['sha256'],wholeNormalSpeedPlaybackReachedEnd=True,
 sampledContinuousFlowApproved=True,wholeEndedObservation='final-flow-ended-observation-v2.json',
 selectedTargetsObservation='final-flow-targets-selected-observation-v2.json',
 selectedProgressObservations=[p.name for p in sorted(R.glob('final-flow-progress-observation-v2-*.json'))],
 protectedCurrentScriptReview='paired-script-direct-review-v1.json',currentMixed80Contexts='current-mixed-complete-direct-review-v1.json',
 causalFlow='Task-first cleaning target → visual/body distinction → required aim/view versus added effects → changing position and surface → separate, reversible options → recognize target again after turning → puzzle orientation cues → readability and restored settings → roles, choices and feedback conclusion.',
 primaryReferenceFlow='OS4CZkBBbW4: individual responses, observable screen motion and fixed reference, developer choice, options and feedback; original60 paragraphs retained with overview/bridge.',
 limits='Normal1x muted playback reached the actual end, with selected moving observations and decoded cue/cut samples. This is not a claim that every intermediate frame was directly watched or that human whole listening/pronunciation/medical outcomes were approved.',
 allIntermediateFramesViewed=False,humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 unresolved=[],originalIntroMemberPreserved=True,newGitImages=0))
cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now,stage='current-local-final-v2-reviewed; adoption-collection-platform-Git-schedule-pending',
 ownedJob=None,measuredTimingApproved=True,finalRatioApproved=True,currentMixedContentReviewPassed=True,allFinalPixelsApproved=True,
 qaApproved=True,wholeFlowReview=out.relative_to(ROOT).as_posix(),next='Adopt guarded reviewed v2 pair, collect four files, verify exact hashes; prepare and upload current captioned source once privately with all settings. Baseline Oct12 schedule unchanged until new private/Git review.')
save(R/'latest-checkpoint.json',cp)
qp=B/'queue.json';before=qp.read_text('utf-8-sig');q=json.loads(before)
q['execution'].update(stage=cp['stage'],ownedJob=None,next=cp['next']);q['updatedAt']=now
item=next(v for v in q['items'] if v['slug']=='motion-sickness-games');item.update(status=cp['stage'],currentExecution=None)
item['review'].update(allFinalPixelsPassed=True,causalFlowPassed=True)
assert qp.read_text('utf-8-sig')==before;save(qp,q)
print(json.dumps(dict(wholeNormal1xEnded=True,selectedFlowApproved=True,currentLocalQaPassed=True,actualId=None)))
