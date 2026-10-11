"""Save the explicit full-text review and current-PCM corroboration, not a score gate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = lambda: datetime.now(timezone.utc).isoformat()
def save(p, d):
    temp = p.with_name(p.name + '.writing-' + str(os.getpid()))
    temp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, p)
def ref(p): return {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}

progressPath = P / 'part3-final-mixed-asr-direct-progress-v147.json'
progress = read(progressPath)
execution = read(P / 'part3-final-mixed-asr-execution-v147.json')
extra = read(P / 'part3-artifact-context-execution-v152.json')
pcmPath = P / 'part3-current-mix-pcm-corroboration-v147.json'
pcm = read(pcmPath)
assert execution['status'] == extra['status'] == 'complete'
assert execution['exitCode'] == extra['exitCode'] == 0
assert len(progress['records']) == len(execution['results']) == 23
assert len(extra['results']) == 5
assert pcm['all23RecognitionWindowsCurrentMixExact'] and pcm['allAdditionalArtifactContextsCurrentMixExact']
assert pcm['allSelectedPcmValuesExact'] and pcm['allOriginalChapterSamplesPartitionedOnce']
assert execution['mixSha256'] == extra['mixSha256'] == pcm['currentMixSha256']
assert execution['planSha256'] == extra['planSha256'] == pcm['planSha256']
for r in progress['records']:
    assert r['directFullExpectedAndActualTextRead'] and r['allWordTimestampsRead']
    assert sha(ROOT / r['resultPath']) == r['resultSha256']

observations = {
 'color-reference': [
  'Both complete tone-highlight-reference and tone-material-distinction paragraphs and every word clock directly compared. Expected 구분해 보세요 is recognized correctly at17.36–18.32; the replacement character at41.60–42.62 in whole05 is not a missing PCM syllable.',
  'No extra greeting, missing/repeated sentence or backward restart. Small28.10 versus28.30 neighboring-word overlap retained. Whisper ending-timestamp warning does not remove any printed ending word.'
 ],
 'focus-blur': [
  'Complete lookup-endpoint and original22p4 paragraphs and all clocks directly compared through35.20. No appended farewell, 20s restart or repeated focus sentence occurs; the whole06 zero-duration chunk-edge farewell is absent.',
  '색띠/색디, 피사계/피삭의 and spoken LUT recognizer spelling retained as human-pronunciation questions, without asserting an audible syllable correction.'
 ],
 'depth-and-gbuffer': [
  'Both complete original22r5/6 paragraphs and every clock directly compared through28.76. Projected depth, reversed-Z caveat, G-buffer role and encoded-normal limitation occur once, without extra greeting or missing sentence.',
  '가까움과 멂의 값/가까움과 머데갑 and reversed지/G recognition variants persist in an independent result. This does not prove corrupt source PCM; literal captions and the depth versus G-buffer distinction remain correct. Human pronunciation pending.'
 ],
 'resource-upload': [
  'Complete resource-upload and resource-budget-conditions paragraphs and all word clocks directly compared through41.16. Expected 안 됩니다 is recognized at8.46–9.14, resolving the whole10 replacement character at84.44–85.12.',
  'No extra greeting, missing/repeated sentence or backward restart. 뒤의/뒤에, 한순간의/에 variants and extended 달라집니다 clock retained. Ending-timestamp warning is preserved; printed full ending and sample binding are verified.'
 ],
 'conclusion-inspection': [
  'Full original-conclusion2/3/4 expected and actual text and every word clock directly compared. Complete conclusion3 starts15.14 and ends29.94, including where-to-inspect, screen depth versus simplified space versus triangles and off-screen/occluded/thin-structure limits.',
  'All three conclusions occur once through47.10. No repeated 화면에 남겨주시기 바랍니다, backward restart, added greeting or omitted first half appears. Whole11 zero-duration repetitions at49.98 are recognizer artifacts; original sample-placement proof and this exact-current-mix independent window corroborate the complete passage.',
  '얇은/얄은 spelling variant remains a human-pronunciation question. This content review is not whole-video human listening.'
 ]
}
artifactPath = P / 'part3-artifact-context-direct-review-v152.json'
approvalPath = P / 'part3-final-mixed-asr-direct-review-v147.json'
assert not artifactPath.exists() and not approvalPath.exists(), 'Preserve prior review'
records = []
for r in extra['results']:
    source = ROOT / r['path']; d = read(source)
    assert sha(source) == r['sha256']
    assert d['mixSha256'] == pcm['currentMixSha256'] and not d['expectedTextUsedAsPrompt']
    records.append({'label': r['label'], 'resultPath': r['path'], 'resultSha256': r['sha256'],
      'reviewedAt': stamp(), 'paragraphIds': d['window']['paragraphIds'],
      'directFullExpectedAndActualTextRead': True, 'allWordTimestampsRead': True,
      'notes': observations[r['label']], 'humanPronunciation': 'pending'})
artifact = {'reviewedAt': stamp(), 'currentMixSha256': pcm['currentMixSha256'],
 'planSha256': pcm['planSha256'], 'execution': ref(P / 'part3-artifact-context-execution-v152.json'),
 'records': records, 'allFullTextsAndTimestampsDirectlyCompared': True,
 'observedChunkArtifactsResolved': True, 'resolutionBasis': 'Explicit full-context comparison plus sample-exact current-mix windows and preserved original PCM partition; no expected-text prompting or ending heuristic approval.',
 'pcmCorroboration': ref(pcmPath), 'humanWholeListening': 'pending', 'humanPronunciation': 'pending',
 'rawRecognitionFilesChanged': False, 'automaticApproval': False}
save(artifactPath, artifact)
resolutionMap = {
 'whole-01': ['context-part3-overview', 'context-original-22-3'],
 'whole-03': ['context-21-guide-post-exposure'],
 'whole-05': ['color-reference'], 'whole-06': ['focus-blur'],
 'whole-07': ['context-focus-later-settings'],
 'whole-08': ['context-23-pre-capture-dataflow'],
 'whole-09': ['depth-and-gbuffer', 'context-original-22r-7'],
 'whole-10': ['resource-upload'], 'whole-11': ['conclusion-inspection', 'context-original-conclusion-5']}
for r in progress['records']:
    r['independentCorroborationPending'] = False
    r['finalContentApproval'] = True
    if r['label'] in resolutionMap:
        r['resolvedAt'] = stamp(); r['independentCurrentMixCorroboration'] = resolutionMap[r['label']]
progress.update(updatedAt=stamp(), allWholeAndIndependentTextsDirectlyCompared=True,
 finalMixedAsrApproved=True, pcmCorroboration=ref(pcmPath), artifactContextReview=ref(artifactPath),
 approvalScope='Current mixed narration content/order/completeness for the review-pair gate; human listening and pronunciation remain pending.')
save(progressPath, progress)
approval = {'reviewedAt': stamp(), 'allWholeAndIndependentTextsDirectlyCompared': True,
 'finalMixedAsrApproved': True, 'currentMixSha256': pcm['currentMixSha256'], 'planSha256': pcm['planSha256'],
 'directProgress': ref(progressPath), 'pcmCorroboration': ref(pcmPath), 'artifactContextReview': ref(artifactPath),
 'directWholeWindows': 11, 'directBaseIndependentWindows': 12, 'directArtifactWindows': 5,
 'all85NarratedParagraphsRetained': True, 'observedChunkArtifactsResolved': True,
 'noConfirmedPcmOmissionRepetitionOrUnrequestedGreeting': True,
 'recognizerSpellingVariantsRetainedForHumanListening': ['맡는/맞는','피사계/피삭의','렌더독 시연/랜더독션','reversed-Z/G','G-buffer/Z버퍼','가까움과 멂/머데갑','얇은/얄은'],
 'humanWholeListening': 'pending', 'humanPronunciation': 'pending', 'automaticApproval': False,
 'allFinalPixelsReviewed': False, 'qaApproved': False, 'collected': False, 'uploaded': False}
save(approvalPath, approval)
print(json.dumps({'baseFullTextWindows': 23, 'additionalFullTextWindows': 5, 'currentPcmExactWindows': 28,
 'reviewPairAudioGate': True, 'humanListening': 'pending', 'finalPixels': False}))
