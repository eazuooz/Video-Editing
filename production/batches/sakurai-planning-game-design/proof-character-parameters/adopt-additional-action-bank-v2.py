"""After clarity execution closes, adopt the separately reviewed unused action.

This preserves the original bank. It grants source-candidate planning scope,
never measured timing, continuous-frame review or final cue approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4];PROOF=Path(__file__).resolve().parent
BASE=ROOT/'projects/character-parameters/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
asr=read(BASE/'voice-clarity-v2/asr-execution.json')
assert asr['exitCode']==0 and asr['actualExitObserved'] and asr['all25ProtectedInputsUnchanged']
voiceReview=read(BASE/'voice-clarity-v2/current-direct-review.json')
assert voiceReview['allFourCompleteTextsDirectlyCompared'] and voiceReview['changedVoiceReadyForMeasuredPlanning']
old=PROOF/'source-action-bank-v1.json';bank=read(old)
reviewPath=PROOF/'additional-role-action-direct-review-v2.json';review=read(reviewPath)
playbackPath=PROOF/'additional-role-playback-observation-v2.json';playback=read(playbackPath)
assert review['sparseBoundaryAndFramingApproved'] and review['all38NativeAnd38FramedSamplesDirectlyRead']
assert playback['normalSpeedPlaybackStartAndEndObserved'] and playback['directDomFinalVideoState']['paused']
assert review['candidate']['startFrame']==8040 and review['candidate']['endFrameExclusive']==8400
assert len(bank['windows'])==19 and bank['sourceAdoptionApproved']
assert sha(old)=='dbccd0c66b0d5f80ac74a2cf7a185b14d825d221dbd09cc2a28f4b63343dff6f'
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
                'scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
request=read(BASE/'voice-clarity-v2/request.json')
for r in request['protectedInputs']: assert sha(ROOT/r['path'])==r['sha256'],r['path']
source=next(s for s in bank['sources'] if s['sourceKey']=='gBbKFYZYvbc')
assert sha(ROOT/source['sourcePath'])==source['sourceSha256']==review['sourceSha256']
for row in bank['windows']:
    if row['sourceKey']=='gBbKFYZYvbc':
        assert max(8040,row['startFrame'])>=min(8400,row['endFrameExclusive'])
new={**review['candidate'], 'durationSeconds':12, 'stepSeconds':.5,
     'sourceSha256':review['sourceSha256'], 'boundaryDirectReviewApproved':True,
     'provisionalInsertion':'12-conclusion',
     'visibleAction':'Ground/air choices, projectiles and close exchanges with changing current damage state.',
     'viewerFocus':'Observe different positions and available responses; damage percentages are current match state.',
     'diagramConnection':'A role is remembered through situation, choice and response rather than one base-stat number.',
     'normalPlaybackRate':1,'sourceAudioUse':False,'loop':False,'slowdown':False,
     'observation':'268–280s half-open active exchange; distinct from earlier window07 ending268. No respawn, result, idle or victory inference in reviewed samples.',
     'selectedForNarrationPlanning':True,'finalUseDurationSeconds':None,'allFinalCueUiApproved':False,
     'directReview':rel(reviewPath),'directReviewSha256':sha(reviewPath),
     'playbackObservation':rel(playbackPath),'playbackObservationSha256':sha(playbackPath)}
bank['windows'].append(new)
bank.update(schemaVersion=2, recordedAt=datetime.now(timezone.utc).isoformat(),
            status='twenty-reviewed-unique-action-candidates-ready-for-measured-allocation',
            sourceAdoptionApproved=True,
            adoptionScope='Reviewed source-candidate planning only; normal-speed native intervals, sparse boundary/framing and UI playback. All continuous native/final cues and actual60:explanation40 timing remain pending.',
            maximumUniqueSeconds=sum(w['durationSeconds'] for w in bank['windows']),
            priorBank=rel(old),priorBankSha256=sha(old),
            additionalReview=rel(reviewPath),additionalReviewSha256=sha(reviewPath),
            additionalPlayback=rel(playbackPath),additionalPlaybackSha256=sha(playbackPath),
            newlyAcquiredMedia=0,sourceAudioUse=False,rasterGitAdditions=0)
target=PROOF/'source-action-bank-v2.json';assert not target.exists()
target.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n','utf-8')
candidates=ROOT/'projects/character-parameters/sources/game-candidates.json'
assert sha(candidates)==sha(old)
candidates.write_bytes(target.read_bytes())
print(json.dumps(dict(bank=rel(target),sha256=sha(target),uniqueWindows=20,
                     maximumUniqueSeconds=bank['maximumUniqueSeconds'],finalTimingApproved=False)))
