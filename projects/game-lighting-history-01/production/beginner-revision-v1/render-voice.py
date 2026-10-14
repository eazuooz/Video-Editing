"""Generate only the 52 reviewed beginner replacements; retain all baseline PCM."""
import datetime, hashlib, json, os, pathlib, runpy, sys
R = pathlib.Path(__file__).resolve().parents[4]
P = R / 'projects/game-lighting-history-01'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p, data): p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
review = read(P/'production/beginner-revision-v1/changes.json')
assert review['completeKoEnDirectReview'] and len(review['rows']) == 52
for lang in ['ko', 'en']:
    assert sha(P/f'script/beginner-changes-v1.{lang}.json') == review['hashes'][lang]
control = read(R/'shared/publishing/video-production-control.json')
assert control['mode'] == 'one-video-autonomous-until-private-upload'
assert not control['automaticNextVideoEnabled']
ck = read(P/'production/checkpoint.json')
assert ck['beginnerRevision']['privateUploadAuthorized']
assert read(P/'production/review-ledger.json')['beginnerRevision']['prerequisiteSample']
manifest = 'projects/game-lighting-history-01/production/beginner-revision-v1/tts.project.json'
assert sys.argv[sys.argv.index('--manifest')+1] == manifest
# This retained entrypoint checks inventory, existing voice hashes and acquires
# an exclusive cooperative GPU lease. It restores only a queue it paused.
ns = runpy.run_path(str(P/'production/render-voice.py'), run_name='beginner_configuration')
if '--dry-run' in sys.argv:
    ns['render_narration'].main()
    raise SystemExit(0)
import psutil
out = P/'production/local/beginner-revision-v1/tts'
out.mkdir(parents=True, exist_ok=True)
state = dict(status='running', startedAt=now(), pid=os.getpid(),
             createTime=psutil.Process().create_time(), command=psutil.Process().cmdline(),
             gpuJobs=1, cpuThreads=2, replacementCount=52, baselinePcmRegenerated=False,
             scriptHashes=review['hashes'], completedChunks=[], humanListening='pending')
write(out/'execution.json', state)
ck.update(updatedAt=now(), stage='beginner-replacement-tts',
          activeOwnedHeavyJob={**state, 'execution':str((out/'execution.json').relative_to(R)).replace('\\','/')},
          nextAction='Complete52changed-utterance batch; measured speech/full changed ASR, semantic motion and retained native placement, final mix and pair QA/private upload. Preserve baseline IDs.')
ck['beginnerRevision']['newTts'] = 'running'
write(P/'production/checkpoint.json', ck)
try:
    ns['render_narration'].main()
    state.update(status='complete-exit0', exitCode=0, finishedAt=now())
except BaseException as exc:
    state.update(status='failed', error=repr(exc), finishedAt=now())
    raise
finally:
    chunks = R/'shared/output/narration/game-lighting-history-01/beginner-revision-v1/chunks'
    state['completedChunks'] = [p.name for p in sorted(chunks.glob('b*-scene.wav'))]
    write(out/'execution.json', state)
    ck = read(P/'production/checkpoint.json')
    if ck.get('activeOwnedHeavyJob',{}).get('pid') == state['pid']:
        ck['activeOwnedHeavyJob'] = None
        ck['beginnerRevision']['newTts'] = state['status']
        ck['beginnerRevision']['ttsExecution'] = str((out/'execution.json').relative_to(R)).replace('\\','/')
        write(P/'production/checkpoint.json', ck)
