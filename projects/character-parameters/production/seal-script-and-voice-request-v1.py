"""Seal the directly read independent paired script; prepare one voice request.

This preparation never loads a TTS model or manipulates research controls.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
PROOF = ROOT/'production/batches/sakurai-planning-game-design/proof-character-parameters'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.resolve().relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()
def save(p, obj):
    temp = p.with_name(p.name + f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(temp, p)

review_path = BASE/'paired-script-direct-review-v1.json'
request_path = BASE/'narration-tts-request-v1.json'
assert not review_path.exists() and not request_path.exists(), 'Inspect existing preparation; do not overwrite it.'
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node, 'scripts/review-video-duplicates.cjs', 'character-parameters', '--check'], cwd=ROOT, check=True)
ko = read(PROJECT/'script/narration.ko.json'); en = read(PROJECT/'script/narration.en.json')
intents = read(PROJECT/'planning/scene-intents-v1.json')
bank = read(PROOF/'source-action-bank-v1.json')
assert bank['sourceAdoptionApproved']
assert len(ko['scenes']) == len(en['scenes']) == len(intents['scenes']) == 12
assert sum(len(s['lines']) for s in ko['scenes']) == 37
for a,b,c in zip(ko['scenes'],en['scenes'],intents['scenes']):
    assert a['id'] == b['id'] == c['id']
    assert len(a['lines']) == len(b['lines']) == c['paragraphs']
    assert all(x.strip() for x in a['lines']+b['lines'])
overview = ko['scenes'][0]
checks = [
    ('01-overview', 'Three sentences ask how values create playstyle, promise Rivals/shared action and unique rules before Dungeons resources, and connect directly to shared movement/jump/attack. 134 characters; 20–30 seconds planned, not yet measured.'),
    ('02-common-baseline', 'Shared actions and minimum usable performance precede differentiation; footage illustrates movement/platform actions rather than measured balance.'),
    ('03-rule-not-scale', 'Visible fire, water and bubbles distinguish attention to opponent state from location. No numeric multiplier or unobserved teleport mechanic is asserted.'),
    ('04-information-rule', 'Similar figures and smoke change information. Appearance is explicitly separated from invulnerability, interaction rules and counterplay.'),
    ('05-useful-strength', 'Ground/air/offstage opportunities connect useful strength with access. The close-pressure role is explicitly a hypothetical design example.'),
    ('06-role-and-limitation', 'Preserves useful weakness, approach/return choices and opponent responses. Playable/enemy role and narrow-corridor/combination example are hypothetical and require playtests; selected footage does not prove placement effects.'),
    ('07-state-not-base', 'Damage percentage and remaining stocks are current match state, not attack tables. Historical footage is not evidence of current rankings or universal formulas.'),
    ('08-resources-and-actions', 'Hamir REACT defense/block, Slade STEAL coins and Artemis STUN opponent dice are separate shots. STEAL is not dodge, STUN is not regeneration, and per-turn dice are not permanent base stats.'),
    ('09-condition-and-time', 'Fleet SNIPE tooltip grants two stamina dice on the next turn, not immediate current +6. Separate boss STRIKE heart loss is not conflated with SNIPE. Trigger/target/time are explicit.'),
    ('10-balance-preserves-role', 'Differences do not establish fairness; test situations repeatedly rather than infer overall balance from one win. Repair unusable/dominant conditions while preserving role.'),
    ('11-cost-and-summary', 'End/turn/ability interactions motivate concise explicit states and tests. The role question connects situations, tools and opponent responses.'),
    ('12-conclusion', 'Recaps the same shared baseline/strength/limitation/rule promises, state and timing distinctions, and a practical role sentence before the stat table.'),
]
review = dict(schemaVersion=1, slug='character-parameters', reviewedAt=now(),
    method='Directly read every current Korean/English paragraph, outline and spatial intent; compared with the fully read original JA research and sealed actual source observations.',
    scenes=12, pairedParagraphs=37, koCharacters=sum(len(t) for s in ko['scenes'] for t in s['lines']),
    wholeExpectedKoEnDirectlyRead=True, independentOriginalScript=True, sourceLectureReplication=False,
    overviewPromiseReview=True, overview=dict(sentences=3,characters=sum(map(len,overview['lines'])),targetSeconds=[20,30],measuredSeconds=None),
    sceneReviews=[dict(id=i,allPairedParagraphsRead=True,reason=r) for i,r in checks],
    currentScripts=[dict(path=rel(PROJECT/f'script/narration.{lang}.json'),sha256=sha(PROJECT/f'script/narration.{lang}.json')) for lang in ['ko','en']],
    sourceActionBank=dict(path=rel(PROOF/'source-action-bank-v1.json'),sha256=sha(PROOF/'source-action-bank-v1.json')),
    contentReadyForApprovedVoiceMeasurement=True, sourceWindowAllocationMeasured=False,
    finalCueUiApproved=False, allNativeFramesReviewed=False, continuousWholeViewingApproved=False,
    humanListeningApproved=False, humanPronunciationApproved=False, publicRightsApproved=False,
    narrationCreated=False, finalMixCreated=False, actualVideoId=None)
save(review_path, review)
manifest_path = PROJECT/'project.json'; manifest = read(manifest_path)
manifest['status'] = 'script-reviewed-ready-for-approved-voice-measurement'
manifest['review']['script'] = True
manifest['editing']['exampleInterleaving']['reviewStatus'] = 'reviewed-source-action-bank-and-script-connections; measured allocation pending'
save(manifest_path, manifest)
protected = [manifest_path, PROJECT/'script/narration.ko.json', PROJECT/'script/narration.en.json',
    PROJECT/'planning/outline.md', PROJECT/'planning/scene-intents-v1.json', PROJECT/'sources/game-candidates.json',
    PROOF/'source-action-bank-v1.json', review_path,
    ROOT/'shared/voice-reference/reference-15-35s.wav', ROOT/'shared/voice-reference/reference-15-35s.ko.txt']
request = dict(schemaVersion=1,slug='character-parameters',preparedAt=now(),pairedWholeTextReview=True,overviewPromiseReview=True,
    scriptReview=rel(review_path),queueDir='C:/Users/eazuo/renderformer/tmp/placement_focus_20261008',device='cuda:0',cpuThreads=2,batchSize=1,total=12,paragraphs=37,
    model=manifest['tts']['model'],voiceApproval='Existing user-approved Qwen3-TTS 1.7B and exact channel reference; no new speaker or voice style.',
    researchHandoff='Final checkpoint/validation/done, owned cooperative job-boundary pause, single exclusive TTS, restore original command/cwd/queue on success or failure and verify actual resumed state.',
    protectedInputs=[dict(path=rel(p),sha256=sha(p)) for p in protected],
    scenes=[dict(id=s['id'],title=s['title'],paragraphs=len(s['lines']),text=' '.join(s['lines']),
        path=manifest['tts']['outputDir']+'/chunks/'+s['id']+'-scene.wav') for s in ko['scenes']],
    currentWholeAsrDirectReview=False,finalMixedAsrApproved=False,heuristicIsApproval=False)
save(request_path, request)
checkpoint = dict(schemaVersion=1,slug='character-parameters',recordedAt=now(),stage='script-reviewed-approved-voice-request-prepared',
    scriptReview=rel(review_path),sourceBank=rel(PROOF/'source-action-bank-v1.json'),ttsRequest=rel(request_path),
    scenes=12,pairedParagraphs=37,ttsStarted=False,voiceMeasured=False,motionCanvasCreated=False,finalTimingApproved=False,
    mixedAsrApproved=False,allFinalPixelsApproved=False,qa=False,collected=False,uploaded=False,actualId=None,
    nextAction='Validate the single voice wrapper, read fresh actual CIM/GPU and research queue, then start one serialized request. After actual voice exit verify original research resume and whole current-hash ASR plus independent contexts.')
save(BASE/'latest-checkpoint.json',checkpoint)
qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
raw=qpath.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='character-parameters')
item.update(stage=checkpoint['stage'],updatedAt=now(),nextAction=checkpoint['nextAction'],scriptReview=rel(review_path),
    sourceActionBank=rel(PROOF/'source-action-bank-v1.json'),sourceAdoptionApproved=True)
item['checkpoints']['script']=True
item['execution']=dict(status='exited',pid=65336,processCreateTime=1791581351.4376469,sessionId=5033,exitCode=0,
    state=rel(PROOF/'trim-boundary-execution-v1.json'),scope='Completed historical CPU boundary preparation; do not rerun.')
item['sourcePreflightReview'].update(nativeActionAdoptionApproved=True,actionBank=rel(PROOF/'source-action-bank-v1.json'),finalCueUiApproved=False)
q.update(updatedAt=now(),lastProgressAt=now())
assert qpath.read_text('utf-8-sig')==raw, 'Concurrent batch writer; inspect before updating.'
save(qpath,q)
print('Current complete 12-scene/37-paragraph paired script sealed; one TTS request prepared. Model/GPU/media/research mutation0.')
