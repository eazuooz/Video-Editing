"""Adopt only the four directly reviewed clarity recognitions and exact PCM.

Run after the separately reviewed additional source bank is adopted. Historical
requests, original scripts, original twelve WAVs and earlier reviews stay intact.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
FOLDER = BASE/'voice-clarity-v2'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.resolve().relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

def save(p, o):
    t = p.with_name(p.name+f'.{os.getpid()}.writing')
    t.write_text(json.dumps(o, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(t, p)

request = read(FOLDER/'request.json')
state = read(FOLDER/'asr-execution.json')
review_path = FOLDER/'current-direct-review.json'
review = read(review_path)
assert state['exitCode'] == 0 and state['actualExitObserved']
assert review['allFourCompleteTextsDirectlyCompared']
assert review['changedVoiceReadyForMeasuredPlanning']
assert sha(FOLDER/'asr-execution.json') == review['executionSha256']
assert read(FOLDER/'research-resume-verification.json')['restorationVerified']
assert len(state['candidateScenes']) == 12
assert not (BASE/'current-voice-selection-v2.json').exists(), 'Read current adoption; never repeat it'
bank_path = ROOT/'production/batches/sakurai-planning-game-design/proof-character-parameters/source-action-bank-v2.json'
bank = read(bank_path)
assert len(bank['windows']) == 20 and bank['sourceAdoptionApproved']
assert sha(ROOT/'projects/character-parameters/sources/game-candidates.json') == sha(bank_path)
for row in request['protectedInputs']:
    if row['path'] != 'projects/character-parameters/sources/game-candidates.json':
        assert sha(ROOT/row['path']) == row['sha256'], row['path']
for row in state['candidateScenes']:
    assert sha(ROOT/row['path']) == row['sha256']
assert sum(bool(r['unchangedOriginalPcm']) for r in state['candidateScenes']) == 10
candidate_ko, candidate_en = read(FOLDER/'narration.ko.json'), read(FOLDER/'narration.en.json')
old_ko = read(ROOT/'projects/character-parameters/script/narration.ko.json')
old_en = read(ROOT/'projects/character-parameters/script/narration.en.json')
changed = {'08-resources-and-actions', '09-condition-and-time'}
for before, after in [(old_ko, candidate_ko), (old_en, candidate_en)]:
    assert len(before['scenes']) == len(after['scenes']) == 12
    for a, b in zip(before['scenes'], after['scenes']):
        assert a['id'] == b['id'] and a['title'] == b['title']
        assert len(a['lines']) == len(b['lines'])
        if a['id'] in changed:
            assert a['lines'][:2] == b['lines'][:2]
        else:
            assert a == b
for language in ['ko', 'en']:
    destination = ROOT/f'projects/character-parameters/script/narration.{language}.json'
    snapshot = FOLDER/f'pre-adoption-main-narration.{language}.json'
    assert not snapshot.exists()
    snapshot.write_bytes(destination.read_bytes())
    destination.write_bytes((FOLDER/f'narration.{language}.json').read_bytes())
selection = dict(schemaVersion=2, adoptedAt=now(), slug='character-parameters',
                 currentKoScript=rel(ROOT/'projects/character-parameters/script/narration.ko.json'),
                 currentKoScriptSha256=sha(ROOT/'projects/character-parameters/script/narration.ko.json'),
                 currentEnScript=rel(ROOT/'projects/character-parameters/script/narration.en.json'),
                 currentEnScriptSha256=sha(ROOT/'projects/character-parameters/script/narration.en.json'),
                 scenes=state['candidateScenes'],
                 totalPcmSeconds=sum(s['samples']/24000 for s in state['candidateScenes']),
                 changedCompleteParagraphs=2, unchangedParagraphs=35,
                 unchangedOriginalScenes=10, originalTwelvePcmPreserved=True,
                 directReview=rel(review_path), directReviewSha256=sha(review_path),
                 originalWholeReview=rel(BASE/'current-whole-direct-review-v1.json'),
                 originalIndependentReview=rel(BASE/'current-context-direct-review-v1.json'),
                 currentCompleteVoiceReadyForMeasuredPlanning=True,
                 approvalScope='Full current texts and independent contexts compared; exact retained-prefix/whole replacement PCM bytes verified. Human listening/pronunciation and final mixed-ASR remain pending.',
                 finalTimingApproved=False, finalMixedAsrApproved=False,
                 humanListening='pending', humanPronunciation='pending')
save(BASE/'current-voice-selection-v2.json', selection)
manifest_path = ROOT/'projects/character-parameters/project.json'
manifest = read(manifest_path)
snapshot = FOLDER/'pre-adoption-project.json'
assert not snapshot.exists()
snapshot.write_bytes(manifest_path.read_bytes())
manifest.update(status='current-voice-directly-reviewed-measured-edit-planning')
manifest['tts']['currentVoiceSelection'] = rel(BASE/'current-voice-selection-v2.json')
manifest['tts']['currentPcmSeconds'] = selection['totalPcmSeconds']
manifest['editing'].update(sourceActionBank=rel(bank_path), sourceActionBankSha256=sha(bank_path),
                           maximumUniqueSourceSeconds=bank['maximumUniqueSeconds'],
                           timingStatus='current-PCM-measured-final-allocation-pending')
manifest['review'].update(narration=True, humanListening=False, publicRights=False,
                         narrationApprovalScope=selection['approvalScope'])
save(manifest_path, manifest)
cp = read(BASE/'latest-checkpoint.json')
cp.update(recordedAt=now(), stage='current-voice-ready-for-measured-native-and-black-allocation',
          voiceMeasured=True, asrApproved=True, narrationApproved=True,
          currentVoiceSelection=rel(BASE/'current-voice-selection-v2.json'),
          sourceBank=rel(bank_path), ownedJob=None,
          nextAction='Allocate unique normal-speed sources and preserve complete current narration/essential black explanations at body60:40. Create measured independent MC/KOEN cues; all mix/final-pixel/QA/publishing/Git gates remain pending.')
save(BASE/'latest-checkpoint.json', cp)
qp = ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for _ in range(10):
    raw = qp.read_text('utf-8-sig'); q = json.loads(raw)
    item = next(i for i in q['items'] if i['slug'] == 'character-parameters')
    item.update(stage=cp['stage'], currentExecution=None,
                currentVoiceSelection=cp['currentVoiceSelection'], nextAction=cp['nextAction'])
    item['checkpoints']['narration'] = True
    q['updatedAt'] = now()
    if qp.read_text('utf-8-sig') == raw:
        save(qp, q); break
    time.sleep(.15)
else:
    raise RuntimeError('Concurrent queue write; inspect preserved current state')
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
                'scripts/review-video-duplicates.cjs', 'character-parameters', '--check'], cwd=ROOT, check=True)
print(json.dumps(dict(currentScenes=12, preservedOriginalScenes=10,
                      currentPcmSeconds=selection['totalPcmSeconds'], finalTimingApproved=False)))
