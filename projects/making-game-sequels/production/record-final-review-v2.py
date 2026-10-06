"""Close revised pixel QA after exact adoption and five actual changed-board reads."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
W = BASE / 'final-v2'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def write(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
now = datetime.now(timezone.utc).isoformat()
ledger = read(W/'encoded-pixel-direct-review.json')
adoption = read(W/'encoded-pixel-exact-adoption.json')
extraction = read(W/'encoded-caption-qa-local-v1/execution.json')
pair = read(W/'review-pair-build.json')
plan = read(W/'plan.json')
mix = read(W/'mix-settings.json')
asr = read(W/'full-mix-asr-review.json')
assert ledger['reviewedSheets'] == list(range(1,125)) and ledger['reviewedImageCount'] == 744
assert len(ledger['reviewedRecords']) == 124 and len(adoption['comparisons']) == 744
changed = [79,80,81,83,84]
assert ledger['changedSheetsRequiringDirectRead'] == adoption['changedSheets'] == changed
assert adoption['adoptedSheetCount'] == len(ledger['byteIdenticalAdoptedSheets']) == 119
assert any(f['sheets'] == changed and 'All30 tiles' in f['observation'] for f in ledger['findings'])
prior = read(ROOT/ledger['priorDirectReview'])
assert prior['reviewedSheets'] == list(range(1,125))
previous = {r['sheetNumber']: r for r in prior['reviewedRecords']}
for record in ledger['reviewedRecords']:
    assert sha(ROOT/record['path']) == record['sha256']
    for image in record['images']: assert sha(ROOT/image['path']) == image['sha256']
    if record['sheetNumber'] in ledger['byteIdenticalAdoptedSheets']:
        old = previous[record['sheetNumber']]
        assert old['sha256'] == record['sha256'] and sha(ROOT/old['path']) == old['sha256']
        assert [r['sha256'] for r in old['images']] == [r['sha256'] for r in record['images']]
for c in adoption['comparisons']:
    assert sha(ROOT/c['currentPath']) == c['currentSha256']
    if c['oldSheetNumber'] in ledger['byteIdenticalAdoptedSheets']:
        assert c['encodedPngByteIdentical'] and c['oldSha256'] == c['currentSha256'] == sha(ROOT/c['oldPath'])
assert extraction['exitCode'] == 0 and len(extraction['images']) == 744
assert extraction['request']['cueCount'] == 308 and extraction['request']['all60ParagraphOnsetsCovered']
assert extraction['request']['nativeCutCount'] == 85 and extraction['request']['whiteCount'] == 7
assert pair['planSha256'] == sha(W/'plan.json') == mix['planSha256'] == asr['adoptedPlanSha256']
assert pair['identicalAacPayload'] and pair['frames'] == plan['finalFrames'] == 35583
for r in pair['records']:
    assert sha(ROOT/r['path']) == r['sha256'] and r['wholeDecodeExitCode'] == 0
    clock = r['exactPresentationClock']
    assert clock['allPacketPtsExact'] and clock['timeBase'] == '1/90000' and clock['count'] == 35583 and clock['step'] == 1500
assert asr['technicallyApproved'] and asr['all26WindowsDirectlyCompared'] and asr['currentParagraphs'] == 60
assert sha(BASE/'final-v1/final-mix.wav') == mix['wavSha256'] == asr['currentMixedAudioSha256']
assert sha(BASE/'final-v1/final-mix.m4a') == mix['aacSha256'] == asr['currentMixAacSha256'] == pair['sourceMixAacSha256']
assert plan['actualFrames'] == 20918 and plan['explanationFrames'] == 13945 and abs(plan['body60_40ErrorFrames']) <= 1
alignment = read(BASE/'final-v1/caption-alignment-review.json')
assert alignment['approved'] and len(alignment['paragraphs']) == 60
for r in alignment['inputScripts']: assert sha(ROOT/r['path']) == r['sha256']
for r in alignment['captions']:
    assert sha(ROOT/r['path']) == r['sha256'] == sha(W/f"captions.{r['language']}.srt")
    r['path'] = rel(W/f"captions.{r['language']}.srt")
for issue in ledger['unresolvedIssues']:
    assert issue['segment'] in [r['id'] for r in plan['revision']['changedSegments']]
    issue.update(resolved=True, resolvedAt=now, resolution='Revised crop [0,100,1472,828] removes the central hotbar; the actual live lower-left counter and narrated trap focus remain readable above fixed captions. All changed boards79/80/81/83/84 directly read.', revisionPairSha256=pair['records'][1]['sha256'])
ledger['resolvedIssues'] = ledger.pop('unresolvedIssues')
ledger.update(unresolvedIssues=[], allFinalPixelsApproved=True, status='all744-covered-119-exact-byte-adoptions-5-changed-boards-directly-reread', approvedAt=now)
write(W/'encoded-pixel-direct-review.json',ledger)
adoption.update(changedPixelsDirectlyRead=True, changedPixelDirectReview=rel(W/'encoded-pixel-direct-review.json'), approvedAt=now)
write(W/'encoded-pixel-exact-adoption.json',adoption)
alignment.update(finalRenderedPixelsApproved=True, finalRenderedPixelReview=rel(W/'encoded-pixel-direct-review.json'), exactTrackAdoptionFrom=rel(BASE/'final-v1/caption-alignment-review.json'))
write(W/'caption-alignment-review.json',alignment)
qa = dict(schemaVersion=1, status='technical-approved-human-listening-pronunciation-public-rights-pending', reviewedAt=now, technicalApproved=True,
    frames=35583,seconds=593.05,actualFrames=20918,explanationFrames=13945,bodyActualRatioErrorFrames=plan['body60_40ErrorFrames'],
    actualExistingGameCuts=85,whiteSegments=7,agentCreatedGameCuts=0,sourceAudioStreams=0,loops=0,slowdown=0,
    allCurrentPcmSamplesPreserved=True,currentPcmSeconds=554.584,all60PcmParagraphsPreserved=True,originalSixExplanationPcmAndDurationPreserved=True,
    allCurrentFinalMixAsrDirectlyCompared=True,mixedWindows=26,allRenderedCaptionPixelsReviewed=True,uniqueEncodedFrames=744,
    pixelCoverageMethod=dict(previousActualDirectlyReadBoards=124,exactByteIdenticalWholeBoardsAdopted=119,changedBoardsDirectlyReread=changed,currentChangedTilesDirectlyRead=30),
    koCues=308,enCues=173,allBilingualParagraphs=60,captionCenter=[960,970],captionStyle='boxed-white-forest-v1',
    wholeVideoOverview=dict(afterOriginalBrandingSeconds=2,measuredSeconds=24.14,classification='explanation',promisesPresentInBodyAndConclusion=True),
    membershipOutroFrames=600,memberIdentities='original12-profile-name-badge-rows-preserved',
    loudness=dict(integratedLufs=-16.04,truePeakDbtp=-1.98,sameAacPayload=True),
    evidence=dict(technical=rel(W/'review-pair-build.json'),pixels=rel(W/'encoded-pixel-direct-review.json'),exactAdoption=rel(W/'encoded-pixel-exact-adoption.json'),mixedAsr=rel(W/'full-mix-asr-review.json'),captionAlignment=rel(W/'caption-alignment-review.json')),
    cleanSha256=pair['records'][0]['sha256'],captionedSha256=pair['records'][1]['sha256'],planSha256=sha(W/'plan.json'),
    humanWholeListening='pending',pronunciationApproval='pending',uncertainPronunciationWords=['Knight 나이드/나이트','옥스/오크스','조사 의/에','13guide 적이/자쩍이'],
    finalPublicRights='pending',originalNimbus='pending',truncatedMemberHandles='pending',externalBackup='pending',privateUpload='pending',platformAutomaticDubbing='pending',newGitQaImages=0)
write(W/'qa.json',qa)
pair.update(qaApproved=True,allFinalFixedCaptionPixelsReviewed=True,technicalQa=rel(W/'qa.json'),status='technical-approved-awaiting-collection-and-private-save')
write(W/'review-pair-build.json',pair)
manifestPath=ROOT/'projects/making-game-sequels/project.json'; manifest=read(manifestPath)
for key,fn in [('videoClean','making-game-sequels.clean.review.mp4'),('videoBurnedCaptions','making-game-sequels.captioned.review.mp4'),('captionsKo','captions.ko.srt'),('captionsEn','captions.en.srt'),('timeline','plan.json'),('mixSettings','mix-settings.json'),('visualBuild','visual-build.json'),('captionAlignmentReview','caption-alignment-review.json'),('renderReport','review-pair-build.json'),('qaReport','qa.json')]: manifest['paths'][key]=rel(W/fn)
manifest['paths'].update(audioMix=rel(BASE/'final-v1/final-mix.m4a'),audioReport=rel(W/'mix-settings.json'),narration=rel(BASE/'final-v1/narration-timed.wav'))
manifest.update(status='technical-QA-approved-awaiting-output-collection-and-private-save',publishReady=False)
manifest['membershipOutro']['appliedToFinal']=True
manifest['editing'].update(finalDiagramPixelsReviewed=True,timingStatus='Actual35583frames593.05s;85unique cuts/7white;60:40 error0.2frame. Two source crops repaired with unchanged PCM/timing; both full decodes/exact90000clock and744encoded frames approved.',finalPixelReview=rel(W/'encoded-pixel-direct-review.json'))
manifest['editing']['additiveExample']['finalPixelsApproved']=True
manifest['audio']['mixStatus']='Actual unchanged554.584s current PCM/continuousNimbus;593.05s sameAAC -16.04LUFS/-1.98dBTP;all26 mixed windows directly compared. Human listening/pronunciation pending.'
manifest['finalProduction']=dict(revision='final-v2',plan=rel(W/'plan.json'),qa=rel(W/'qa.json'),technicalApproved=True,collected=False,privateUploaded=False,humanWholeListening='pending',humanPronunciation='pending')
write(manifestPath,manifest)
print(json.dumps(dict(technicalApproved=True,frames=35583,encodedFrames=744,exactAdoptedBoards=119,changedBoardsDirectlyReread=changed,collectPending=True,privatePending=True)))
