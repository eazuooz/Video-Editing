"""Record completed voice review and unfinished measured source selection."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/hierarchical-game-outlines'
PROD = BASE / 'production'
def read(p):
    return json.loads((ROOT / p).read_text(encoding='utf-8-sig'))
def write(p, value):
    (ROOT / p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

now = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
stamp = now.replace('-', '').replace(':', '').replace('.', '')
rel = f'projects/hierarchical-game-outlines/production/checkpoint-{stamp}.json'
cp = read('projects/hierarchical-game-outlines/production/latest-checkpoint.json')
voice = read('projects/hierarchical-game-outlines/production/voice-approval-v2.json')
plan = read('projects/hierarchical-game-outlines/production/final-v1/plan.json')
assert voice['allCurrentScenesTechnicallyReviewed'] and voice['unchangedPcmVerified']
cp['previousCheckpoint'] = cp.get('checkpointPath', 'projects/hierarchical-game-outlines/production/checkpoint-20261003T111703283Z.json')
cp.update(observedAt=now, checkpointPath=rel, status='voice-v2-technically-reviewed-source-cut-selection-pending')
cp['repair1'] = read('projects/hierarchical-game-outlines/production/repair-phrases1.json')
cp['repair1'].update(toolSessionId=20620, alive=False, doNotRestart=True, directReview='projects/hierarchical-game-outlines/production/repair1/direct-review.json')
cp['runner'] = {'status': 'no-active-production-worker', 'pid': None, 'children': []}
cp['v2Asr'] = read('projects/hierarchical-game-outlines/production/v2-cpu-asr.json')
cp['v2Asr'].update(toolSessionId=34149, alive=False, doNotRestart=True, exitCode=0, directReview='projects/hierarchical-game-outlines/production/voice-approval-v2.json')
cp['v2Context'] = {'status': 'finished-directly-reviewed', 'toolSessionId': 23204, 'wrapperPid': 42672, 'pid': 43124, 'exitCode': 0, 'windows': 7, 'report': 'projects/hierarchical-game-outlines/production/repair1/v2-context/asr.json', 'doNotRestart': True}
cp['preparedCompositeCompiler'].update(executed=True, exitCode=0, doNotRerun=True, proof='projects/hierarchical-game-outlines/production/repair1/v2-composite-proof.json')
cp['script'].update(speechApproved=True, approvalKind='technical-content-and-current-hash-PCM-review', voiceReview='projects/hierarchical-game-outlines/production/voice-approval-v2.json', humanListening='pending', unchangedParagraphs=54)
cp['voiceReview'] = {k: voice[k] for k in ['status','reviewedAt','currentHashChecked','all60ParagraphsDirectlyCompared','unchangedParagraphs','unchangedPcmVerified','explanationLengthsPreserved','humanListening','timestampAlignmentExclusions']}
cp['draftTimeline'] = {'plan': 'projects/hierarchical-game-outlines/production/final-v1/plan.json', 'seconds': plan['seconds'], 'totalFrames': plan['totalFrames'], 'actualTargetSeconds': plan['gameplaySeconds'], 'explanationTargetSeconds': plan['explanationSeconds'], 'targetRatioErrorFrames': plan['ratioErrorFrames'], 'provisionalBilingualCues': 162, 'measuredSourceCutsApproved': False, 'final60_40Passed': False, 'allFixedCaptionPixelsApproved': False, 'notFinalMedia': True}
cp['sourceFitFollowup'] = read('projects/hierarchical-game-outlines/production/source-fit-followup/direct-review.json')
cp['sourceFitFollowup']['historicalFailedAttempt'] = read('projects/hierarchical-game-outlines/production/source-fit-followup/failed-output-limit.json')
cp['sourceFitFollowup']['finishedRecoverySessions'] = [{'toolSessionId':22960,'exitCode':0,'status':'finished'}, {'version':'native-reserve-v3','exitCode':0,'status':'finished'}, {'version':'native-remaining-v4','exitCode':0,'status':'finished'}]
cp['vite']['alive'] = True
cp['vite']['observedAt'] = '2026-10-03T11:54:42Z'
cp['finalVideo'] = {k: False for k in cp['finalVideo']}
cp['pending'] = ['exclusive source cuts and all fixed-caption/crop/boundary review', 'measured actual-footage60:40', 'final mix and aligned MC/KOEN/chapters/outro', 'final render/QA/collection/private full settings', 'per-video commit/normal push', 'human full listening', 'final public rights', 'original Nimbus bytes', 'truncated member handles', 'external backup']
cp['nextAction'] = 'Do not rerun completed synthesis/composition/ASR. Allocate all current paragraphs to exclusive normal-speed actual actions; split HireStaff4629–4631 and track catalog3278–3279, avoid unrelated3188–3191 camera and decoration catalog. Inspect exact native boundaries and all162 fixed Korean cue pixels. Draft586.75/344.85/229.9 is a target only. Approve measured60:40/cuts/captions before mix/MC/final render/QA/collection/private/Git.'
write(rel, cp)
write('projects/hierarchical-game-outlines/production/latest-checkpoint.json', cp)

qpath = 'production/batches/sakurai-planning-game-design/queue.json'
q = read(qpath)
item = next(x for x in q['items'] if x['slug'] == 'hierarchical-game-outlines')
item.update(stage='measured-source-cuts-and-fixed-caption-planning', updatedAt=now, nextAction=cp['nextAction'])
item['checkpoints']['narration'] = True
ex = item['execution']
ex.update(phase='voice-v2-reviewed-source-cut-selection', status=cp['status'], updatedAt=now, activeTasks=[], pid=None, workerPid=None, sessionId=None, toolSessionId=None, runnerAlive=False, runnerAliveObservedAt=now, runtimeCheckpoint=rel, latestCheckpoint=rel, speechApproved=True)
ex['completedRepairRunner'] = ex.get('repair1', {})
ex['repair1'] = cp['repair1']
ex['v2Asr'] = cp['v2Asr']
ex['v2Context'] = cp['v2Context']
ex['voiceReview'] = cp['voiceReview']
ex['v2Composition'].update(status='composed-all-current-ASR-and-joins-technically-reviewed', proof='projects/hierarchical-game-outlines/production/repair1/v2-composite-proof.json', unchangedParagraphs=54, explanationLengthPreserved=True)
ex['sourceFitFollowup'] = cp['sourceFitFollowup']
ex['draftTimeline'] = cp['draftTimeline']
ex['vite'] = cp['vite']
ex['state'] = 'projects/hierarchical-game-outlines/production/latest-checkpoint.json'
ex['runner'] = None
ex['children'] = []
item['preflight'].update(checkedAt=now, currentCheckPassed=True)
q['updatedAt'] = now
write(qpath, q)
print(json.dumps({'checkpoint':rel,'stage':item['stage'],'finalMediaComplete':False,'activeWorkers':0}, ensure_ascii=False))
