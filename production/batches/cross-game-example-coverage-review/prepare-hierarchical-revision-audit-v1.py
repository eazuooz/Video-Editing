"""Preserve the current completed baseline and record the new teaching audit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import psutil

ROOT = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
H = ROOT / 'projects/hierarchical-game-outlines'
V = H / 'revision-teaching-clarity-v1'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
rel = lambda p: p.relative_to(ROOT).as_posix()


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def save(p, value):
    temp = p.with_name(p.name + '.audit-v1.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(temp, p)


assert not (V / 'baseline-preservation-v1.json').exists(), 'Continue existing audit; do not repeat'
now = datetime.now(timezone.utc).isoformat()
main = read(H / 'project.json')
plan = read(H / 'production/final-v1/plan.json')
assembly = read(H / 'production/visual-depth-v1/assembly-inputs.json')
ko = read(H / 'script/narration.ko.json')
en = read(H / 'script/narration.en.json')
assert [s['id'] for s in ko['scenes']] == [s['id'] for s in en['scenes']]
assert len(ko['scenes']) == 12 and sum(len(s['lines']) for s in ko['scenes']) == 60
assert all(len(k['lines']) == len(e['lines']) for k, e in zip(ko['scenes'], en['scenes']))
assert plan['totalFrames'] == 35205 and plan['bodyFrames'] == 34485
assert plan['actualFrames'] == 20691 and plan['explanationFrames'] == 13794
assert plan['actualFrames'] / plan['bodyFrames'] == .6
assert len(assembly['segments']) == 14 and len(plan['cuts']) == 46
assert {c['sourceId'] for c in plan['cuts']} == {'I-ccSZ5J1Bo'}
assert len(plan['paragraphs']) == 60
current_details = (V / 'ui-proof-v1/current-baseline-details-v1.ax.txt').read_text('utf8')
current_schedule = (V / 'ui-proof-v1/current-baseline-schedule-v1.ax.txt').read_text('utf8')
assert 'jBRt3xatdPk' in current_details and 'text 예약됨' in current_details
assert 'button (disabled) 저장' in current_details and '고화질 완료' in current_details
assert 'jBRt3xatdPk' in current_schedule and '2026. 10. 14.' in current_schedule
assert '오전 9:00' in current_schedule and 'GMT+0900' in current_schedule
assert 'button (disabled) 완료' in current_schedule
active = []
for process in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    try:
        command = ' '.join(process.info['cmdline'] or [])
        if ((process.info['name'] or '').lower() in ['python.exe', 'node.exe', 'ffmpeg.exe']
                and process.pid != os.getpid() and 'hierarchical' in command
                and any(t in command for t in ['render-', 'extract-', 'acquire-', 'assemble-', 'generate-'])):
            active.append(dict(pid=process.pid, command=command, createTime=process.info['create_time']))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
assert not active, active
git_bin = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
index = ROOT / subprocess.check_output([git_bin, 'rev-parse', '--git-path', 'index'], cwd=ROOT, text=True).strip()
index_before = sha(index)
index_entries = subprocess.check_output([git_bin, 'ls-files', '--stage', '-z'], cwd=ROOT)
resource = dict(observedAt=now, processPid=os.getpid(), createTime=psutil.Process().create_time(),
    command=psutil.Process().cmdline(), cwd=psutil.Process().cwd(), cpuPercent=psutil.cpu_percent(interval=.25),
    availableRamBytes=psutil.virtual_memory().available, activeOwnedMediaWorkers=active,
    phase='read-only baseline hash and audit metadata;no media render or model')
inputs = {}


def keep(f, role, expected=None):
    p = ROOT / f
    digest = sha(p)
    if expected:
        assert digest == expected, f
    inputs[f] = dict(path=f, role=role, bytes=p.stat().st_size, sha256=digest)


for f, role in [
        ('project.json', 'historical-current-root'), ('script/narration.ko.json', 'all60-original-KO-paragraphs'),
        ('script/narration.en.json', 'all60-original-EN-paragraphs'), ('production/final-v1/plan.json', 'current-measured-plan'),
        ('production/visual-depth-v1/assembly-inputs.json', 'verified14-piece-bindings'),
        ('production/visual-depth-v1/pair-technical-qa.json', 'historical-completed-technical-QA'),
        ('production/visual-depth-v1/encoded-pixel-direct-review.json', 'historical-completed-visual-QA'),
        ('publishing/youtube-upload-depth-v1.json', 'historical-completed-private-settings'),
        ('sources/source-action-bank.json', 'reviewed-source-action-bank'), ('sources/SOURCES.md', 'source-rights-history')]:
    keep(rel(H / f), role)
for scene in plan['scenes']:
    keep(scene['voice'], 'approved-original-PCM-' + scene['id'], scene['audioSha256'])
for segment in assembly['segments']:
    keep(segment['file'], 'verified-baseline-silent-piece', segment['sha256'])
for key in ['videoClean', 'videoBurnedCaptions', 'audioMix', 'editorAudioMix', 'captionsKo', 'captionsEn']:
    keep(main['paths'][key], 'completed-baseline-' + key)
keep(plan['timedBodyNarration'], 'original-current-distributed-PCM', plan['timedBodyNarrationSha256'])
for f in [main['membershipOutro']['rosterPath'], main['membershipOutro']['screenshot'],
          main['membershipOutro']['cornerLogo'], main['audio']['backgroundMusic']['file']]:
    keep(f, 'approved-original-branding-member-or-music')
bank = read(H / 'sources/source-action-bank.json')
keep(bank['source']['localMediaPath'], 'original-acquired-source-no-redownload', bank['source']['fileSha256'])
orientation = ROOT / 'projects/game-math-orientation-matrices/project.json'
keep(rel(orientation), 'completed-orientation-intentional-schedule-state',
    '08bc7bdd71de66956ce145aeeba1fe7d301275d4ab637f8b13e4c79f9a04a278')
backup = V / 'baseline-project-before-teaching-revision-v1.json'
assert not backup.exists()
backup.write_bytes((H / 'project.json').read_bytes())
preservation = dict(schemaVersion=1, recordedAt=now, slug='hierarchical-game-outlines',
    baselineVideoId='jBRt3xatdPk', currentActualVisibility='scheduled',
    actualScheduledAt='2026-10-14T09:00:00+09:00', baselineUploadChanged=False,
    currentFrames=35205, currentSeconds=586.75, bodyFrames=34485,
    actualFrames=20691, explanationFrames=13794, ratioContract='actual60:explanation40;one-frame tolerance',
    original12PcmVerified=True, original60KoEnParagraphsPreserved=True, verified14PiecesPreserved=True,
    palette='research-paper-white-v1', continuousApprovedNimbusPreserved=True, sourceAudioExcluded=True,
    introFrames=120, outroFrames=600, original12MemberIdentitiesPreserved=True,
    exactRootBackup=rel(backup), exactRootBackupSha256=sha(backup), protectedInputs=list(inputs.values()),
    completedRenderDecodeAsrTtsAndSourceWorkRepeated=False, sourceRedownloaded=False,
    activeOwnedMediaWorkers=0, resourceAtReadOnlyAudit=resource,
    externalIndexBytesUnchanged=sha(index) == index_before,
    externalIndexEntriesUnchanged=subprocess.check_output([git_bin, 'ls-files', '--stage', '-z'], cwd=ROOT) == index_entries,
    externalIndexSha256=index_before, humanListeningApproved=False, humanPronunciationApproved=False,
    publicRightsApproved=False, newGitImages=0, newGitMedia=0)
assert preservation['externalIndexBytesUnchanged'] and preservation['externalIndexEntriesUnchanged']
save(V / 'baseline-preservation-v1.json', preservation)
audit = dict(schemaVersion=1, reviewedAt=now, actualStudioTab='119', actualVideoId='jBRt3xatdPk',
    fullCurrentKoEnScriptsDirectlyRead=True, scenes=12, paragraphPairs=60,
    allOriginalClaimOrderRead=True, currentStudioTitleAndFullKoDescriptionRead=True,
    currentStudioScheduleDirectlyRead=True, currentActualScheduledAt='2026-10-14T09:00:00+09:00',
    historicalQaPreserved=True, currentFinalFootageSourceIds=['I-ccSZ5J1Bo'],
    distinctNarratedExistingGames=1, requiredMinimumGames=4, fourGameCoverageApproved=False,
    missingGameCount=3, openingOverviewApproved=False,
    openingFinding='Original01 begins with a detailed Museum demonstration and introduces its viewer question in paragraph4; add a separate natural whole-video overview after the original cat intro.',
    retainedConcepts=['goal/features/detail hierarchy', 'comparable sibling scale', 'collapse without deleting',
        'move a heading with children', 'meaning after move', 'containment versus cross-reference', 'readers can find unanswered checks'],
    referenceFlow=dict(videoId='ZzCfzwe23kw', fullLocalJapaneseResearchTranscriptRead=True,
        copiedScriptOrMedia=False, matches=['parent/child levels', 'fold/expand', 'reorder/change depth', 'prepare a readable document for other people'],
        additionsRequired=['viewer question and ordered overview before first specific case', 'transfer through at least3 additional actual games', 'narrated cross-game comparisons at relevant original explanations']),
    movingGameplayAnnotationsNeedCurrentAudit=True, newMixedAudioApproved=False, newFinalPixelsApproved=False,
    usefulOriginalExplanationAndAllPcmRetained=True, minimumNewNarrationDependentOnActualSourceReview=True,
    baselineModified=False, platformSettingsChanged=False,
    boundFiles=[dict(path=rel(H / f), sha256=sha(H / f)) for f in
        ['project.json', 'script/narration.ko.json', 'script/narration.en.json', 'production/final-v1/plan.json']],
    studioEvidence=[dict(path=rel(V / 'ui-proof-v1' / f), sha256=sha(V / 'ui-proof-v1' / f)) for f in
        ['current-baseline-details-v1.ax.txt', 'current-baseline-schedule-v1.ax.txt']])
save(V / 'current-content-and-studio-direct-review-v1.json', audit)
next_step = ('Read current duplicate inventory and compare changed/likely-overlapping full content; current --check '
    'must pass before dependent narration/scenes/TTS. Review new official rights/recent-use and normal1x native '
    'candidates for three other existing games, then write independent causal KOEN additions beside retained '
    '12scenes/60paragraphs. Preserve baseline jBR Oct14 09Seoul/12PCM/14pieces/white palette/Nimbus/branding '
    'and all completed orientation/motion work. Do not repeat either pending obsolete-delete question.')
save(V / 'latest-checkpoint.json', dict(recordedAt=now,
    stage='current-baseline-audited;one-game-and-opening-gap;source-and-duplicate-review-next',
    baselinePreservation=rel(V / 'baseline-preservation-v1.json'),
    currentContentReview=rel(V / 'current-content-and-studio-direct-review-v1.json'),
    actualStudioTab='119', baselineVideoId='jBRt3xatdPk', currentScheduledAt='2026-10-14T09:00:00+09:00',
    activeOwnedWorkers=0, newNarrationWritten=False, newTtsStarted=False, newRenderStarted=False,
    finalReplacementApproved=False, newActualVideoId=None, scheduleReplacementVerified=False, next=next_step))
q_path = B / 'queue.json'
raw = q_path.read_bytes()
queue = read(q_path)
queue.update(updatedAt=now, status='active-hierarchical-teaching-audit', next=next_step)
queue['currentHierarchicalReview'] = dict(stage='baseline-direct-content-and-Studio-audit-complete;source-preflight-next',
    baselineVideoId='jBRt3xatdPk', actualStudioTab='119', actualScheduledAt='2026-10-14T09:00:00+09:00',
    currentContentReview=rel(V / 'current-content-and-studio-direct-review-v1.json'),
    baselinePreservation=rel(V / 'baseline-preservation-v1.json'), minimumDistinctGames=4,
    currentDistinctNarratedGames=1, fourGameCoverageApproved=False, original12PcmPreserved=True,
    original60KoEnParagraphsPreserved=True, newTtsStarted=False, newRenderStarted=False,
    ownedJob=None, newActualVideoId=None, scheduleReplacementVerified=False, next=next_step)
assert q_path.read_bytes() == raw
save(q_path, queue)
print(json.dumps(dict(currentVideoId='jBRt3xatdPk', scheduledAt='2026-10-14T09:00:00+09:00',
    original12PcmVerified=True, original14PiecesVerified=True, preservedInputs=len(inputs),
    original60KoEnParagraphsRead=True, currentDistinctGames=1, requiredGames=4,
    openingNeedsAddition=True, newTtsStarted=False, baselineChanged=False)))
