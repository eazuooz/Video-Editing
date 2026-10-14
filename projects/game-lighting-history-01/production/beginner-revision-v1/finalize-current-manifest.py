"""Select the verified continuity-v2 delivery without overwriting prior deliveries."""
import copy, datetime, hashlib, json, pathlib, runpy

R = pathlib.Path(__file__).resolve().parents[4]
P = R / 'projects/game-lighting-history-01'
O = P / 'production/local/continuity-v2'
F = O / 'pair-exact-v2'

def rd(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def wr(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def rel(p):
    return p.relative_to(R).as_posix()

def main():
    runpy.run_path(str(pathlib.Path(__file__).with_name('production-authority.py')))['require_selected_production']()
    review = rd(F / 'final-review.json')
    execution = rd(F / 'execution.json')
    plan = rd(O / 'plan.json')
    assert review['internalReviewPassed'] and not review['humanListeningApproved']
    assert execution['status'] == 'complete-awaiting-encoded-pixels'
    assert review['outputHashes'] == {k: v['sha256'] for k, v in execution['outputs'].items()}
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest = rd(P / 'project.json')
    manifest.setdefault('baselineDeliveryBeforeContinuity', copy.deepcopy({
        k: manifest.get(k) for k in ['status', 'paths', 'finalRender', 'publishing', 'productionGates', 'productionState']
    }))
    manifest.update(status='awaiting-drive-final-review-upload', publishReady=False)
    manifest['video'].update(width=1920, height=1080, fps=60, durationSeconds=plan['seconds'])
    manifest['paths'].update(
        videoBurnedCaptions=rel(F / 'captioned.mp4'), videoClean=rel(F / 'clean.mp4'),
        captionsKo=rel(O / 'captions.ko.srt'), captionsEn=rel(O / 'captions.en.srt'),
        captionAlignmentReview=rel(O / 'caption-alignment-review.json'),
        audioReport=rel(O / 'mix-execution.json'), audioMix=rel(O / 'final-mix.m4a'),
        narration=rel(O / 'narration-current.wav'), timeline=rel(P / 'production/current-rebuild-timeline.json'))
    manifest['editing'].update(actualGameplaySeconds=plan['actualFrames']/60,
        actualExplanationSeconds=plan['explanationFrames']/60,
        plannedActualSeconds=plan['actualFrames']/60, plannedExplanationSeconds=plan['explanationFrames']/60,
        actualGameplayShare=plan['actualFrames']/plan['bodyFrames'], timingStatus='continuity-v2-exact-frame-verified')
    manifest['finalRender'] = dict(status='internally-reviewed-awaiting-human-drive-review',
        frames=plan['frames'], durationSeconds=plan['seconds'], outputs=execution['outputs'],
        technicalEvidence=rel(F / 'execution.json'), pixelEvidence=rel(F / 'final-review.json'),
        knownIssues=['Human final listening/pronunciation pending', 'Public rights review pending',
                     'Existing truncated member handle preserved'])
    manifest['activeRevision'].update(id='continuity-v2', parentRevision='beginner-revision-v1',
        status='awaiting-drive-final-review-upload', plan=rel(O / 'plan.json'), planSha256=execution['planSha256'],
        newFinalRenderComplete=True, baselineDeliveryPathsIntentionallyPreserved=False,
        baselineDeliveryPreservedIn='baselineDeliveryBeforeContinuity', finalReviewApproved=False,
        newYouTubeUploadAuthorized=False)
    manifest['productionGates'].update(finalMixedAsrApproved=True, final60to40Measured=True,
        finalRendered=True, allEncodedPixelsReviewed=True, outputCollected=False, uploaded=False,
        humanListeningApproved=False, driveFinalUserReview=False)
    manifest['productionState'].update(updatedAt=now, ownedGpuJobs=0, ownedCpuAsrJobs=0,
        currentParagraphPairs=150, currentFinalPlan=rel(O / 'plan.json'),
        currentVoiceReview='150 current paragraphs directly compared; human listening/pronunciation pending.',
        currentVoiceDirectReview=rel(O / 'source-review.json'), currentVoiceAsrSessionId=None,
        currentVoiceAsrExecution=rel(O / 'source-review.json'),
        currentMixedReview=rel(O / 'mixed-asr-direct-review.json'),
        currentCaptionAlignment=rel(O / 'caption-alignment-review.json'),
        currentEncodedReview=rel(F / 'final-review.json'), currentPairEvidence=rel(F / 'execution.json'))
    music = manifest['audio']['backgroundMusic']
    original = R / music['originalFile']
    assert hashlib.sha256(original.read_bytes()).hexdigest() == '06ddb8d0f2aa82e499ab2cb398b8a241c626d9d3da82bbaf274d1178435f8c08'
    music.update(file=music['originalFile'], originalFileVerified=True, originalFileVerification='Local original MP3 matches the existing LICENSE.md SHA-256; current background is reused from the measured prior premix, not reconstructed.', approvalScope='Existing user-approved Nimbus track. Original library MP3 is available and hash-verified; this revision preserves the prior background premix.')
    wr(P / 'project.json', manifest)
    wr(P / 'production/current-rebuild-timeline.json', dict(schemaVersion=1,
        canonicalPlan=rel(O / 'plan.json'), canonicalPlanSha256=execution['planSha256'], fps=60,
        scenes=plan['nodes'], voice=plan['voice'],
        finalNoteRemoval=[rel(F / 'weight-note-removal.json'),rel(F / 'ending-caption-safe-repair.json')],
        introNoteRemoval='Global frames120..437: black box x800 y819 w320 h45 before clean/captioned split.'))
    checkpoint = rd(P / 'production/checkpoint.json')
    checkpoint.update(updatedAt=now, stage='continuity-v2-collect-and-drive-upload', activeOwnedHeavyJob=None,
        nextAction='Collect four verified outputs and upload the captioned master to the private Drive review folder. Await current-version human review before YouTube.')
    checkpoint['gates'].update(finalTimelineApproved=True, bodyRatioApproved=True,
        allFinalCaptionPixelsReviewed=True, finalRenderComplete=True, finalMixedAsrApproved=True,
        collected=False, uploaded=False, driveUserReview=False)
    checkpoint['beginnerRevision'].update(status='internally-reviewed-awaiting-drive-upload',
        newRender='145768 frames,1080p60,complete decode and source/caption mapping verified',
        next=checkpoint['nextAction'])
    checkpoint['unresolved']=[x for x in checkpoint['unresolved'] if x not in ['original-Nimbus-file','external-media-backup']]
    wr(P / 'production/checkpoint.json', checkpoint)
    ledger = rd(P / 'production/review-ledger.json')
    ledger['currentPolicyRevision'].update(newEncodedOutputApproved=True, allCurrentOutputPixelsApproved=True,
        finalReview=rel(F / 'final-review.json'), driveUserReview='pending', humanListening='pending')
    wr(P / 'production/review-ledger.json', ledger)
    print('Current verified delivery selected; prior delivery and YouTube identifiers preserved.')

if __name__ == '__main__':
    main()
