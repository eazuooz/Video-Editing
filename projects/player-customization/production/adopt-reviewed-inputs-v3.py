"""Record completed direct pixel reviews, then adopt only the current inputs.

No media render, TTS, ASR, upload or Git action. Historical rejected plans remain.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, re, subprocess, time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
FINAL = BASE / 'final-v1'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
now = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()
def save(p, j):
    t = p.with_name(p.name + f'.{os.getpid()}.writing')
    for n in range(60):
        try:
            t.write_text(json.dumps(j, ensure_ascii=False, indent=2)+'\n', 'utf-8')
            os.replace(t, p)
            return
        except OSError:
            if n == 59: raise
            time.sleep(.15)

assert not FINAL.exists(), 'Read any existing final checkpoint before adopting.'
target = BASE/'selected-input-review-v3.json'
focused = BASE/'nearby-repaired-pixels-direct-review-v3.json'
assert not target.exists() and not focused.exists()
duplicate = subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'player-customization', '--check'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
assert duplicate.returncode == 0, duplicate.stdout + duplicate.stderr
prior = read(BASE/'selected-pixels-direct-review-v1.json')
repair = read(BASE/'action-repaired-pixels-direct-review-v2.json')
e = read(BASE/'nearby-repaired-pixels-execution-v3.json')
build = read(BASE/'selected-inputs-execution-v3.json')
assert prior['allBoardsDirectlyRead'] and prior['readBoardCount'] == 355
assert repair['allBoardsDirectlyRead'] and repair['boardCount'] == 46 and len(repair['resolvedIssues']) == 4
assert len(repair['unresolvedIssues']) == 1
assert e['exitCode'] == 0 and len(e['boards']) == 7 and len(e['samples']) == 40
assert build['exitCode'] == 0 and build['completedCuts'] == 139 and build['frames'] == 35321
assert build['reusedBaselineSegments'] == 138 and build['newNativeEncodes'] == 1
assert build['exact90000Pts'] and build['wholeDecodesExitCode'] == 0
for x in [*e['boards'], *e['samples']]: assert sha(ROOT/x['path']) == x['sha256'], x['path']
assert sha(ROOT/build['silentVideo']) == build['silentSha256']
assert sha(ROOT/build['captionedSilentVideo']) == build['captionedSilentSha256']
assert sha(ROOT/build['captionPath']) == build['captionSha256']
assert sha(ROOT/build['captionAss']) == build['captionAssSha256']
for seg in build['segments']: assert sha(ROOT/seg['video']) == seg['videoSha256'], seg['video']
planPath = ROOT/build['allocationPath']
assert sha(planPath) == build['allocationSha256'] == e['allocationSha256']
candidate = read(planPath)
for x in candidate['inputs']: assert sha(ROOT/x['path']) == x['sha256']
assert candidate['wholePcmSamples'] == 14125441
assert candidate['actualFramesCandidate'] == 21193 and candidate['explanationFramesCandidate'] == 14128
assert candidate['bodyFrames'] == 35321 and candidate['finalFramesCandidate'] == 36041
assert candidate['bodyRatioErrorFrames'] <= 1
assert not candidate['issues'] and candidate['allNativeSourceFramesUnique']
cuts = candidate['cuts']; cursor = 120; intervals = {}
for c in cuts:
    assert c['outputStartFrame'] == cursor and c['sourceOutFrame']-c['sourceInFrame'] == c['frames']
    cursor += c['frames']
    if c['role'] == 'actual-game-candidate':
        a, b = c['sourceInFrame'], c['sourceOutFrame']
        used = intervals.setdefault(c['sourcePath'], [])
        assert all(max(a, x) >= min(b, y) for x, y in used)
        used.append((a, b))
assert cursor == 35441
timingPath = ROOT/candidate['inputs'][0]['path']; timing = read(timingPath)
assert timing['wholePcmSamples'] == 14125441 and len(timing['rows']) == 16
for row in timing['rows']: assert sha(ROOT/row['audioPath']) == row['audioSha256']
observations = [
    dict(boards='001–002', observation='Preserved2024 caster and rotating ring remain through cue171. Output245.883333 first profile frame3990 matches cue172; overhead view establishes caster at the centre with three armored nearby foes.'),
    dict(boards='003', observation='Overhead66.5–67.0 establishes caster/foe positions, then the official source visibly cuts to rotating blades and target close-up. Source camera edits are retained; simultaneous caster visibility throughout the clause is not claimed.'),
    dict(boards='004–005', observation='Cue173 from247.133333 appears over an identifiable armored target reacting beside the cyan Aquablades arc. Head and action remain visible above fixed bottom captions; target bends through248.816667. New native ends248.833333, then preserved2024 footage begins248.85.'),
    dict(boards='006–007', observation='Preserved following caster/ring/target action and cues174–175 show differing relative positions. All fixed captions readable; no presenter/hotbar collision, clipping or damage/superiority assertion.'),
]
fr = dict(schemaVersion=1, slug='player-customization', reviewedAt=now(), execution=rel(BASE/'nearby-repaired-pixels-execution-v3.json'),
    allocationPath=rel(planPath), allocationSha256=sha(planPath), encodedWindowSha256=build['captionedSilentSha256'],
    allBoardsDirectlyRead=True, allSamplesDirectlyRead=True, boardCount=7, sampleCount=40, hashVerifiedFiles=47, hashMismatches=0,
    boards=[{**x, 'directlyRead':True} for x in e['boards']], samples=[{**x, 'directlyRead':True} for x in e['samples']], observations=observations,
    resolvedIssue='12p1 unclear nearby target replaced with current official profile overhead-centre/armored-target sequence; original source edits explicit',
    unresolvedDefects=[], allSelectedPixelsApproved=True, sourceAllocationApproved=True, allFinalPixels=False,
    finalMixedAsrApproved=False, imagesLocalOnly=True, newGitImages=0, humanWholeListening='pending', humanPronunciation='pending')
save(focused, fr)
review = dict(schemaVersion=1, slug='player-customization', reviewedAt=now(), allocationPath=rel(planPath), allocationSha256=sha(planPath),
    allBoardsDirectlyRead=True, sourceAllocationApproved=True, allInputSegmentCaptionPixelsReviewed=True, unresolvedDefects=[],
    evidence=[dict(path=rel(p), sha256=sha(p)) for p in [BASE/'selected-pixels-direct-review-v1.json', BASE/'action-repaired-pixels-direct-review-v2.json', focused]],
    baselineBoards=355, baselineSamples=2128, repairedBoards=46, repairedSamples=272, finalNearbyBoards=7, finalNearbySamples=40,
    reviewedScope='Full baseline355 boards, four passed repairs from46 focused boards, and all7 latest nearby repair boards. Unchanged inputs reused byte-identically; historical five defects retained in prior evidence and all resolved in current139 cuts.',
    currentBuild=rel(BASE/'selected-inputs-execution-v3.json'), currentBuildSha256=sha(BASE/'selected-inputs-execution-v3.json'),
    silentVideo=build['silentVideo'], silentSha256=build['silentSha256'], segmentHashCount=139, reusedSegments=138, newNativeEncodes=1,
    koCueCount=415, enCueCount=162, sceneCount=16, paragraphCount=64, originalPcmSamples=14125441,
    finalTimingApproved=True, bodyRatioApproved=True, bodyFrames=35321, actualFrames=21193, explanationFrames=14128, bodyRatioErrorFrames=.4,
    finalMixedAsrApproved=False, allFinalPixels=False, qaApproved=False, collected=False, uploaded=False,
    preparationGuardFailures=[dict(worker='compiler-v3', reason='Derived worker retained v2 state name; refused before state/media creation; corrected to v3'), dict(worker='extractor-v3', reason='Derived worker retained v2 state name; refused before state/image creation; corrected to v3')],
    imagesLocalOnly=True, newGitImages=0, humanWholeListening='pending', humanPronunciation='pending', currentDuplicateCheck=dict(exitCode=0, output=duplicate.stdout+duplicate.stderr))
save(target, review)
plan = copy.deepcopy(candidate)
plan.update(status='reviewed-current-inputs-awaiting-final-mix', adoptedAt=now(), adoptedFromCandidate=rel(planPath), adoptedFromCandidateSha256=sha(planPath),
    selectedInputReview=rel(target), selectedInputReviewSha256=sha(target), sourceAllocationApproved=True,
    finalTimingApproved=True, bodyRatioApproved=True, allInputSegmentCaptionPixelsReviewed=True,
    actualFrames=21193, explanationFrames=14128, finalFrames=36041, body60_40ErrorFrames=.4, durationSeconds=36041/60,
    voiceTiming=rel(timingPath), voiceTimingSha256=sha(timingPath), sceneStarts=[dict(id=x['id'], startFrame=x['startFrame'], endFrame=x['endFrame']) for x in timing['rows']],
    inputBuild=rel(BASE/'selected-inputs-execution-v3.json'), bodySilentVideo=build['silentVideo'], bodySilentSha256=build['silentSha256'],
    captionSource=build['captionPath'], captionSourceSha256=build['captionSha256'],
    intro=dict(path='projects/game-reward-planning/production/final-v1/white-segments/branding.mp4', frames=120, sha256='706a0738dcd160b80ace24e54e16c09604c0173aba095fcd221a227c541fffb2'),
    membership=dict(path='projects/game-reward-planning/production/final-v1/white-segments/membership.mp4', frames=600, sha256='181e5c5dd37672349542aa590629fe2f2d00a83f4cd3c811a29a21c029612123'),
    allFinalPixels=False, finalMixedAsrApproved=False, renderPairApproved=False, qaApproved=False, collected=False, uploaded=False)
for x in [plan['intro'], plan['membership']]: assert sha(ROOT/x['path']) == x['sha256']
for c in plan['cuts']:
    c.update(inputPixelsReviewed=True, fixedCaptionPixelsReviewed=True, finalPixelsReviewed=False)
    if c['role'] == 'actual-game-candidate': c.update(role='actual-game', sourceActionAligned=True)
for p in plan['paragraphs']:
    p.update(sourceActionAligned=True, cropAndCaptionPixelsReviewed=True)
    for span in p['spans']: span['sourceMatched'] = True
FINAL.mkdir()
save(FINAL/'plan.json', plan)
# Global caption timestamps are already measured with original two-second intro.
for lang in ['ko', 'en']:
    src = BASE/f'caption-candidate-v1/candidate.{lang}.srt'
    (FINAL/f'captions.{lang}.srt').write_bytes(src.read_bytes())
def shift_ass(match):
    h, m, sec = match.group(0).split(':'); total = round((int(h)*3600+int(m)*60+float(sec)+2)*100)
    return f'{total//360000}:{total//6000%60:02d}:{total//100%60:02d}.{total%100:02d}'
ass = (ROOT/build['captionAss']).read_text('utf-8-sig')
lines = []
for line in ass.splitlines():
    if line.startswith('Dialogue:'): line = re.sub(r'\d+:\d{2}:\d{2}\.\d{2}', shift_ass, line, count=2)
    lines.append(line)
(FINAL/'captions.ko.ass').write_text('\n'.join(lines)+'\n', 'utf-8')
save(FINAL/'caption-clock-adoption.json', dict(createdAt=now(), sourceCaptionSha256=build['captionSha256'], sourceBodyAssSha256=build['captionAssSha256'],
    finalAssSha256=sha(FINAL/'captions.ko.ass'), bodyToGlobalShiftSeconds=2, koCueCount=415, enCueCount=162,
    koSrtByteIdentical=True, enSrtByteIdentical=True, captionCenter=[960,970], style='boxed-white-forest-v1', allFinalPixels=False))
manifestPath = BASE.parent/'project.json'; manifest = read(manifestPath)
manifest['audio']['backgroundMusic'] = copy.deepcopy(read(ROOT/'projects/familiar-game-rules/project.json')['audio']['backgroundMusic'])
assert sha(ROOT/manifest['audio']['backgroundMusic']['file']) == manifest['audio']['backgroundMusic']['restoration']['sha256']
manifest['status'] = 'reviewed-current-inputs-awaiting-final-mix'
manifest['editing'].update(measuredTotals=dict(bodyFrames=35321, actualFrames=21193, explanationFrames=14128, finalFrames=36041, durationSeconds=36041/60, bodyRatioErrorFrames=.4),
    bodyRatioApproved=True, finalTimingApproved=True, sourceAllocationApproved=True, allInputSegmentCaptionPixelsReviewed=True, measuredPlan=rel(FINAL/'plan.json'))
manifest['approvals'].update(footage=True, finalTiming=True)
manifest['paths'].update(finalPlan=rel(FINAL/'plan.json'), selectedInputReview=rel(target), subtitlesKo=rel(FINAL/'captions.ko.srt'), subtitlesEn=rel(FINAL/'captions.en.srt'))
manifest['updatedAt'] = now(); save(manifestPath, manifest)
cpPath=BASE/'latest-checkpoint.json'; cp=read(cpPath)
cp.update(stage=manifest['status'], recordedAt=now(), selectedInputReview=rel(target), currentIntegerAllocationCandidate=rel(planPath), finalPlan=rel(FINAL/'plan.json'),
    sourceAllocationApproved=True, finalTimingApproved=True, bodyRatioApproved=True, allInputSegmentCaptionPixelsReviewed=True,
    allFinalPixels=False, finalMixedAsrApproved=False, qaApproved=False, collected=False, uploaded=False,
    nextAction='Fresh resource check, single CPU2 reviewed Nimbus mix, then32 current mixed whole/context windows directly compared. Guarded pair/final pixels/QA/collection/private/Git remain pending.')
save(cpPath, cp)
qPath=ROOT/'production/batches/sakurai-planning-game-design/queue.json'; q=read(qPath)
item=next(x for x in q['items'] if x['slug']=='player-customization')
item.update(stage=cp['stage'], currentIntegerAllocationCandidate=rel(planPath), selectedInputReview=rel(target), finalPlan=rel(FINAL/'plan.json'),
    sourceAllocationApproved=True, finalTimingApproved=True, bodyRatioApproved=True, allInputSegmentCaptionPixelsReviewed=True,
    finalMixedAsrApproved=False, allFinalPixels=False, qaApproved=False, collected=False, uploaded=False, nextAction=cp['nextAction'])
q['updatedAt']=now(); save(qPath,q)
print(json.dumps(dict(adopted=True, cuts=139, actualFrames=21193, explanationFrames=14128, bodyFrames=35321, finalFrames=36041,
    planSha256=sha(FINAL/'plan.json'), allInputSegmentCaptionPixelsReviewed=True, allFinalPixels=False, uploaded=False)))
