"""Seal the explicitly read input samples and adopt their measured timeline.

Input approval does not imply final mixed speech, encoded pixels or delivery.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
FINAL = BASE / 'final-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()
def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf-8')

assert not (FINAL / 'plan.json').exists(), 'Read the actual adopted checkpoint; do not repeat.'
subprocess.run(['node', 'scripts/review-video-duplicates.cjs', 'presenting-game-scores', '--check'], cwd=ROOT, check=True)
progress_path = BASE / 'selected-input-direct-progress-v8.json'
progress = read(progress_path)
assert progress['directlyReadBoardNumbers'] == list(range(1, 110))
assert progress['directlyReadSampleCount'] == progress['totalSamples'] == 651
assert not progress['unresolvedIssues']
preflight_path = BASE / 'selected-input-preflight-v8.json'
assert sha(preflight_path) == progress['sourceSha256']
preflight = read(preflight_path)
assert preflight['allBodyPtsVerified'] and preflight['allSamplePtsVerified']
assert preflight['wholeBodyDecodeExitCode'] == preflight['extractionExitCode'] == 0
for item in [*preflight['boards'], *preflight['samples'], *preflight['segments']]:
    assert sha(ROOT / item['path']) == item['sha256'], item['path']
assert sha(ROOT / preflight['bodyPath']) == preflight['bodySha256']
candidate_path = ROOT / preflight['plan']
caption_path = ROOT / preflight['captionCandidate']
assert sha(candidate_path) == progress['planSha256'] == preflight['planSha256']
assert sha(caption_path) == progress['captionCandidateSha256'] == preflight['captionCandidateSha256']
plan = read(candidate_path); captions = read(caption_path)
voice_path = ROOT / plan['currentVoiceSelection']; voice = read(voice_path)
assert sha(voice_path) == plan['currentVoiceSelectionSha256'] and voice['currentVoiceApproved']
assert (plan['actualFrames'], plan['explanationFrames'], plan['bodyFrames'], plan['finalFrames']) == (10999, 7333, 18332, 19052)
assert abs(plan['bodyRatioFrameError']) <= 1 and plan['narrationSamples'] == 6388323
assert captions['allLiteralKoEn39ParagraphsPreserved'] and captions['original30ParagraphsRetained']
assert (len(captions['ko']), len(captions['en'])) == (168, 68)
assert sum(p['samples'] for p in plan['voicePlacements']) == 6388323
assert all(p['exactCoverage'] and not p['removedSamples'] and not p['repeatedSamples'] for p in plan['exactPcmCoverage'])
for item in voice['scenes']: assert sha(ROOT / item['path']) == item['sha256']

review_path = BASE / 'selected-input-direct-review-v8.json'
review = dict(schemaVersion=8, reviewedAt=now(), preflight=rel(preflight_path), preflightSha256=sha(preflight_path),
    progress=rel(progress_path), progressSha256=sha(progress_path), planSha256=sha(candidate_path),
    captionCandidateSha256=sha(caption_path), bodySha256=preflight['bodySha256'],
    directlyReadBoardNumbers=list(range(1,110)), boards=preflight['boards'], sampleCount=651,
    koCueCount=168, enCueCount=68, cuts=24, blackMotionSegments=12, logicalParagraphs=39,
    allBoardsDirectlyRead=True, allInputCaptionPixelsReviewed=True, sourceAllocationApproved=True,
    allCurrentCueTextsDirectlyRead=True, unresolvedDefects=[],
    observations=progress['observations'] + [
        'Boards105–109: sequential token/arrow moves through three projected audit towers; all labels, coaching footer and captions have clear spacing through the last body frame.',
        'Exact observed2920 and later141 snapshots are separate from changing live play and final victory; equal-count coarse samples do not substitute for sealed native equality frame2057.',
        'Balatro hand and count-up shots are separate press-montage excerpts. Independent2x3=6 diagram is not presented as the recorded final score.',
        'Korean one-line cues and all changed English cues were read in full before these pixel boards; full39 bilingual paragraphs are retained.'],
    scope='All planned input cue/cut/clause-onset/spatial-motion samples. Not every continuous native frame, final encoded pair or human listening.',
    allFinalPixels=False, finalMixedAsrApproved=False, qa=False, collected=False, private=False,
    humanListening='pending', humanPronunciation='pending', localOnlyImages=True, imagesGitAdded=0)
save(review_path, review)
FINAL.mkdir(exist_ok=True)
plan.update(schemaVersion=1, adoptedAt=now(), candidatePlan=rel(candidate_path), candidatePlanSha256=sha(candidate_path),
    selectedInputReview=rel(review_path), selectedInputReviewSha256=sha(review_path),
    selectedInputPreflight=rel(preflight_path), selectedInputPreflightSha256=sha(preflight_path),
    bodySilent=preflight['bodyPath'], bodySilentSha256=preflight['bodySha256'],
    selectedInputSegments=preflight['segments'], captionCandidate=rel(caption_path), captionCandidateSha256=sha(caption_path),
    captions='projects/presenting-game-scores/production/final-v1/captions.json',
    body60_40ErrorFrames=abs(plan['bodyRatioFrameError']), bodyRatioApproved=True, finalTimingApproved=True,
    allInputSegmentCaptionPixelsReviewed=True, finalPlanAdopted=True, preparedOnly=False,
    membershipStartFrame=18452, style='research-black-v1')
save(FINAL / 'plan.json', plan)
captions.update(adoptedAt=now(), candidatePath=rel(caption_path), candidateSha256=sha(caption_path),
    allCurrentCueTextsDirectlyRead=True, allInputCuePixelsReviewed=True, inputReview=rel(review_path),
    finalTimingApproved=True, timingApprovalScope='Current ASR word alignment, complete clause placement and all planned input pixel samples; human pronunciation/listening remain pending.',
    allCuePixelsReviewed=False, allFinalPixels=False)
save(FINAL / 'captions.json', captions)
for src, dst in [('candidate.ko.srt','presenting-game-scores.ko.srt'), ('candidate.en.srt','presenting-game-scores.en.srt')]:
    (FINAL / dst).write_bytes((caption_path.parent / src).read_bytes())
manifest_path = BASE.parent / 'project.json'; m = read(manifest_path)
m['status'] = 'reviewed-inputs-final-mix-pending'
m['video']['durationSeconds'] = plan['durationSeconds']
m['editing'].update(timingStatus='measured-final-inputs-adopted', actualGameplaySeconds=10999/60,
    actualExplanationSeconds=7333/60, actualGameplayShare=10999/18332, actualCommercialGameplaySeconds=10999/60,
    finalPlan=rel(FINAL/'plan.json'), finalPlanSha256=sha(FINAL/'plan.json'), actualFrames=10999,
    explanationFrames=7333, bodyFrames=18332, finalFrames=19052, bodyRatioFrameError=plan['bodyRatioFrameError'],
    currentScriptParagraphs=39, originalScriptParagraphsPreserved=30, inputPixelReview=rel(review_path))
m['audio'].update(mixStatus='current39-PCM-final-mix-pending', currentNarrationSamples=6388323,
    currentNarrationSeconds=266.180125)
m['paths'].update(narration=rel(FINAL/'narration-timed.wav'), audioMix=rel(FINAL/'final-mix.m4a'),
    captionsKo=rel(FINAL/'presenting-game-scores.ko.srt'), captionsEn=rel(FINAL/'presenting-game-scores.en.srt'),
    videoClean=rel(FINAL/'presenting-game-scores.clean.mp4'),
    videoBurnedCaptions=rel(FINAL/'presenting-game-scores.captioned.mp4'))
m['approvals'].update(finalTiming=True, bodyRatio=True, inputCaptionPixels=True,
    finalMixedAsr=False, allFinalPixels=False)
save(manifest_path,m)
job=dict(status='closed-input-review-approved',pid=41112,createTime=1791534826.0488207,
    sessionId=38215,state=rel(BASE/'selected-input-preflight-execution-v8.json'),exitCode=0,
    outerExitDirectlyObserved=True,workerExpectedRunning=False,cpuThreads=2,gpu=0)
cp_path=BASE/'latest-checkpoint.json'; cp=read(cp_path)
cp.update(recordedAt=now(),stage='reviewed-final-inputs-Nimbus-mix-pending',ownedJob=job,
    finalTimingApproved=True,allInputSegmentCaptionPixelsReviewed=True,finalPlan=rel(FINAL/'plan.json'),
    selectedInputReview=rel(review_path),scenes=19,paragraphs=39,
    nextAction='SingleCPU2 current PCM/Nimbus mix and full silent visual; current mixed10 whole chapters plus independent complete contexts, then guarded pair/final pixels/QA/collection/private/Git.')
save(cp_path,cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp)
i=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
i.update(stage=cp['stage'],currentExecution=job,currentJob=job,ownedJob=job,finalPlan=rel(FINAL/'plan.json'),
    selectedInputReview=rel(review_path),nextAction=cp['nextAction'])
i['checkpoints'].update(narration=True,footage=True,scenes=True,mix=False,render=False,qa=False,collected=False)
q['updatedAt']=now();save(qp,q)
session_path=BASE/'selected-input-preflight-execution-v8.session.json';session=read(session_path)
session.update(exitCode=0,actualExitObserved=True,sessionClosed=True,closedObservation=now())
save(session_path,session)
save(BASE/'final-input-adoption-v1.json',dict(adoptedAt=now(),plan=rel(FINAL/'plan.json'),planSha256=sha(FINAL/'plan.json'),
    review=rel(review_path),reviewSha256=sha(review_path),captionsSha256=sha(FINAL/'captions.json'),
    frames=19052,seconds=19052/60,koCues=168,enCues=68,allInputPixelsReviewed=True,
    finalMixedAsrApproved=False,allFinalPixels=False,qa=False,collected=False,private=False,actualId=None,
    newMedia=0,newImagesGitAdded=0,newTts=0,researchControlChanges=0))
print(json.dumps(dict(finalFrames=19052,seconds=19052/60,inputBoardsReviewed=109,finalMixedAsrApproved=False)))
