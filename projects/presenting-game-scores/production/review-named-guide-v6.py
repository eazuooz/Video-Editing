"""One CPU2 worker for one complete unadopted named-field guide: full texts, then reviewed complete contexts.

No expected script is supplied to the recognizer. Results are review material;
this program never grants narration, timing, pixel or final-mix approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, time, traceback, wave
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def save(p, d):
    temp = p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    for retry in range(40):
        try: os.replace(temp, p); return
        except OSError:
            if retry == 39: raise
            time.sleep(.15)

parser = argparse.ArgumentParser()
parser.add_argument('--resource', required=True)
parser.add_argument('--mode', choices=['whole', 'contexts'], required=True)
args = parser.parse_args()
STATE = BASE/f'named-guide-{args.mode}-asr-execution-v6.json'
SESSION = STATE.with_name(STATE.stem+'.session.json')
LOG = BASE/f'named-guide-{args.mode}-asr-v6.log'
DEST = BASE/f'named-guide-{args.mode}-asr-v6'
resource = read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z', '+00:00'))).total_seconds() < 240
assert resource['ownHeavyJobs'] == 0 and resource['cpuLoadPercent'] < 85
assert resource['freePhysicalMemoryKiB'] > 8_000_000
assert not STATE.exists() and not DEST.exists() and not LOG.exists(), 'Read existing execution/cache; never repeat it.'
tts = read(BASE/'named-guide-tts-execution-v6.json')
assert tts['exitCode'] == 0 and tts['generationComplete'] and tts['actualExitObserved']
assert len(tts['results']) == 1
restoration = read(BASE/'named-guide-research-resume-verification-v6.json')
assert restoration['ownedCoordinatorClosed'] and restoration['restorationVerified']
assert restoration['ttsLeaseToken'] == tts['leaseToken'], 'Current voice research restoration is unverified'
request = read(BASE/'named-guide-tts-request-v6.json')
# The content inputs stay frozen; the now-ended worker's full manifest lock may
# be released for measured production metadata, so it is not an ASR input.
for row in request['protectedInputs']:
    if row['path'].endswith('/project.json'): continue
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
ko_path = ROOT/'projects/presenting-game-scores/script/named-guide-repair-v6.ko.json'
en_path = ROOT/'projects/presenting-game-scores/script/named-guide-repair-v6.en.json'
script = read(ko_path)
assert len(script['scenes']) == 1
assert sum(len(x['lines']) for x in script['scenes']) == 1
inputs = []
if args.mode == 'whole':
    for scene in script['scenes']:
        m = next(x for x in tts['results'] if x['id'] == scene['id'])
        assert sha(ROOT/m['path']) == m['sha256']
        inputs.append(dict(id=scene['id'], sourcePath=m['path'], sourceSha256=m['sha256'],
            expectedKo=scene['lines'], seconds=m['seconds'], sourceSamples=m['samples']))
else:
    whole = read(BASE/'named-guide-whole-asr-execution-v6.json')
    assert whole['exitCode'] == 0 and whole['actualExitObserved']
    plan_path = BASE/('named-guide-targeted-context-plan-v6.json' if args.mode == 'targets' else 'named-guide-independent-context-plan-v6.json')
    plan = read(plan_path)
    review = read(ROOT/plan['wholeReview'])
    assert sha(ROOT/plan['wholeReview']) == plan['wholeReviewSha256']
    assert review['allWholeTextsDirectlyCompared']
    assert plan['boundariesDirectlyComparedWithCurrentWordsAndPCM']
    assert len(plan['contexts']) == 2 if args.mode == 'targets' else len(plan['contexts']) >= 2
    inputs = plan['contexts']

subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
    'scripts/review-video-duplicates.cjs', 'presenting-game-scores', '--check'], cwd=ROOT, check=True)
for name in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS']: os.environ[name] = '2'
os.environ.update(CUDA_VISIBLE_DEVICES='', TOKENIZERS_PARALLELISM='false', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
if os.name == 'nt': ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
DEST.mkdir()
actual_process = psutil.Process()
state = dict(schemaVersion=1, slug='presenting-game-scores', pid=os.getpid(), createTime=actual_process.create_time(),
    processIdentity=dict(pid=os.getpid(), createTime=actual_process.create_time(),
                         commandLine=actual_process.cmdline(), cwd=actual_process.cwd()),
    workerReportedCommandLine=[sys.executable, *sys.argv],
    sessionId=None, startedAt=now(), status='loading-current-CPU2-whisper', mode=args.mode, cpuThreads=2, gpuJobs=0,
    cpuJobs=1, completed=0, total=len(inputs), resource=resource, audioInputs=inputs, koSha256=sha(ko_path), enSha256=sha(en_path),
    exitCode=None, automaticApproval=False, directReview=False, narrationApproved=False, finalMixedAsrApproved=False,
    humanListening='pending', humanPronunciation='pending')
def checkpoint():
    if SESSION.exists():
        launch = read(SESSION)
        if launch.get('pid') == os.getpid():
            state['sessionId'] = launch['sessionId']
            state['processIdentity'] = launch.get('processIdentity')
    state['updatedAt'] = now(); save(STATE, state)
    job = dict(status=state['status'], pid=os.getpid(), workerReportedCommandLine=state['workerReportedCommandLine'],
        processIdentity=state.get('processIdentity'), sessionId=state['sessionId'], state=rel(STATE), log=rel(LOG),
        startedAt=state['startedAt'], completed=state['completed'], total=state['total'], cpuThreads=2, gpu=0,
        singleJob=True, workerExpectedRunning=state['exitCode'] is None, exitCode=state['exitCode'])
    cp_path = BASE/'latest-checkpoint.json'; cp = read(cp_path)
    cp.update(recordedAt=now(), stage=f'named-guide-{args.mode}-CPU-ASR-v6', ownedJob=job,
        asrApproved=False, narrationApproved=False,
        nextAction='Observe actual single CPU worker. Read every complete recognized text against the current script and PCM; preserve independent context, pronunciation and final-mix gates. Measured 60:40, final depth/caption pixels, pair QA and upload remain pending.')
    save(cp_path, cp)
    qp = ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(8):
        raw = qp.read_text('utf-8-sig'); q = json.loads(raw)
        item = next(x for x in q['items'] if x['slug'] == 'presenting-game-scores')
        item.update(stage=cp['stage'], currentExecution=job, nextAction=cp['nextAction'])
        item['checkpoints']['narration'] = False
        q['updatedAt'] = now(); q['lastProgressAt'] = now()
        if qp.read_text('utf-8-sig') == raw: save(qp, q); break
        time.sleep(.15)
    else: raise RuntimeError('Concurrent batch write; preserve foreign changes.')

class Tee:
    def __init__(self, output, file): self.output = output; self.file = file
    def write(self, s): self.output.write(s); self.output.flush(); self.file.write(s); self.file.flush(); return len(s)
    def flush(self): self.output.flush(); self.file.flush()

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
original_stdout, original_stderr = sys.stdout, sys.stderr
with LOG.open('x', encoding='utf-8') as log:
    sys.stdout = Tee(original_stdout, log); sys.stderr = sys.stdout
    try:
        checkpoint()
        if args.mode != 'whole':
            audio_dir = ROOT/f'shared/output/presenting-game-scores/research/named-guide-{args.mode}-asr-v6'
            assert not audio_dir.exists(); audio_dir.mkdir(parents=True)
            sliced = []
            for c in inputs:
                source = ROOT/c['sourcePath']; assert sha(source) == c['sourceSha256']
                with wave.open(str(source), 'rb') as w:
                    params = w.getparams()
                    assert params.framerate == 24000 and params.nchannels == 1 and params.sampwidth == 2
                    a, b = c['startSample'], c['endSample']
                    assert 0 <= a < b <= w.getnframes()
                    w.setpos(a); pcm = w.readframes(b-a); assert len(pcm) == (b-a)*2
                target = audio_dir/(c['id']+'.wav')
                pad = c.get('zeroPaddingSamplesEachSide', 0)
                assert pad >= 0
                padded = b'\x00\x00'*pad + pcm + b'\x00\x00'*pad
                with wave.open(str(target), 'wb') as w: w.setparams(params); w.writeframes(padded)
                with wave.open(str(target), 'rb') as w:
                    actual = w.readframes(w.getnframes())
                    assert actual == padded
                    assert actual[pad*2:len(actual)-pad*2 if pad else None] == pcm
                sliced.append({**c, 'contextPath':rel(target), 'contextSha256':sha(target),
                    'pcmSha256':hashlib.sha256(pcm).hexdigest(), 'exactSourceSampleBytesMatched':True})
            inputs = sliced; save(DEST/'pcm-slices.json', dict(createdAt=now(), slices=sliced))
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        torch.set_num_threads(2); torch.set_num_interop_threads(1)
        model_path = ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
            low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager', local_files_only=True).to('cpu')
        processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)
        transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
        results = []
        for row in inputs:
            state['status'] = 'transcribing-current-'+row['id']; checkpoint()
            audio_path = ROOT/row.get('contextPath', row['sourcePath'])
            audio_sha = row.get('contextSha256', row['sourceSha256'])
            assert sha(audio_path) == audio_sha
            raw = transcriber(str(audio_path), generate_kwargs={'language':'korean', 'task':'transcribe'}, return_timestamps='word')
            result = {**row, 'text':raw['text'], 'words':raw['chunks'], 'audioSha256':audio_sha,
                'expectedWasRecognizerPrompt':False, 'directReview':False, 'approved':False}
            assert sha(audio_path) == audio_sha
            results.append(result); save(DEST/(row['id']+'.json'), result)
            save(DEST/'asr.json', dict(complete=len(results) == len(inputs), results=results, automaticApproval=False,
                humanListening='pending', humanPronunciation='pending'))
            state['completed'] = len(results); checkpoint()
            print(json.dumps(dict(id=row['id'], text=result['text']), ensure_ascii=False), flush=True)
        assert sha(ko_path) == state['koSha256'] and sha(en_path) == state['enSha256']
        state.update(status='closed-current-voice-ASR-awaiting-direct-review', exitCode=0, cpuJobs=0, finishedAt=now())
        checkpoint()
    except BaseException:
        state.update(status='closed-current-voice-ASR-failed', exitCode=1, cpuJobs=0, finishedAt=now(), error=traceback.format_exc())
        checkpoint(); traceback.print_exc(); raise
    finally: sys.stdout = original_stdout; sys.stderr = original_stderr
