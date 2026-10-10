"""After actual TTS/resume verification, preserve prefixes and review four texts.

This makes two candidate full-scene WAVs and two independently recognized whole
replacement paragraphs. It never adopts scripts or approves ASR automatically.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, subprocess, sys, time, traceback, wave
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
FOLDER = BASE/'voice-clarity-v2'
STATE = FOLDER/'asr-execution.json'
SESSION = FOLDER/'asr-session.json'
DEST = FOLDER/'asr'
AUDIO = ROOT/'shared/output/narration/character-parameters/voice-clarity-v2/review-candidates'
LOG = FOLDER/'asr.log'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.resolve().relative_to(ROOT).as_posix()
now = lambda: datetime.now(timezone.utc).isoformat()

def save(p, value):
    temp = p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    os.replace(temp, p)

def pcm(path):
    with wave.open(str(path), 'rb') as w:
        params = w.getparams()
        assert params.framerate == 24000 and params.nchannels == 1 and params.sampwidth == 2
        return params, w.readframes(w.getnframes())

def write_pcm(path, params, data):
    with wave.open(str(path), 'wb') as w:
        w.setparams(params)
        w.writeframes(data)
    assert pcm(path)[1] == data

def checkpoint():
    if SESSION.exists():
        session = read(SESSION)
        assert session['pid'] == state['pid']
        state['sessionId'] = session['sessionId']
    state['updatedAt'] = now()
    save(STATE, state)
    job = dict(pid=state['pid'], createTime=state['createTime'],
               commandLine=state['commandLine'], cwd=state['cwd'],
               sessionId=state['sessionId'], state=rel(STATE), log=rel(LOG),
               cpuThreads=2, gpu=0, completed=state['completed'], total=4,
               workerExpectedRunning=state['exitCode'] is None, exitCode=state['exitCode'])
    cp = read(BASE/'latest-checkpoint.json')
    cp.update(recordedAt=now(), stage=state['status'], ownedJob=job,
              narrationApproved=False, asrApproved=False,
              currentVoiceClarityAsr=rel(STATE),
              researchRestorationVerified=True,
              researchResumeVerification=rel(FOLDER/'research-resume-verification.json'),
              nextAction='Observe actual CPU2 worker exit. Compare both complete candidate scenes and both independent complete paragraphs with their entire expected text and word/PCM boundaries. Adopt only after direct current review; all mixed/final/publishing gates remain pending.')
    save(BASE/'latest-checkpoint.json', cp)
    qp = ROOT/'production/batches/sakurai-planning-game-design/queue.json'
    for _ in range(10):
        raw = qp.read_text('utf-8-sig'); queue = json.loads(raw)
        item = next(x for x in queue['items'] if x['slug'] == 'character-parameters')
        item.update(stage=cp['stage'], currentExecution=job, nextAction=cp['nextAction'],
                    researchRestorationVerified=True,
                    researchResumeVerification=cp['researchResumeVerification'])
        item['checkpoints']['narration'] = False
        queue['updatedAt'] = now()
        if qp.read_text('utf-8-sig') == raw:
            save(qp, queue); break
        time.sleep(.15)
    else:
        raise RuntimeError('Concurrent batch write; preserve other task changes')

ap = argparse.ArgumentParser()
ap.add_argument('--resource')
ap.add_argument('--dry-run', action='store_true')
args = ap.parse_args()
request = read(FOLDER/'request.json')
for row in request['protectedInputs']:
    assert sha(ROOT/row['path']) == row['sha256'], row['path']
paired = read(ROOT/request['review'])
assert sha(ROOT/request['review']) == request['reviewSha256']
assert paired['entireChangedKoEnDirectlyCompared'] and paired['allOtherParagraphsPreserved']
candidate_ko = read(FOLDER/'narration.ko.json')
assert len(candidate_ko['scenes']) == 12 and sum(len(x['lines']) for x in candidate_ko['scenes']) == 37
assert not STATE.exists() and not DEST.exists() and not AUDIO.exists() and not LOG.exists(), 'Read existing outputs; never repeat review execution'
if args.dry_run:
    print('Prepared: two preserved-prefix full-scene candidates plus two independent complete paragraphs. No assembly, model, GPU or adoption.')
    raise SystemExit(0)

assert args.resource
resource = read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z', '+00:00'))).total_seconds() < 240
assert resource['ownHeavyJobs'] == 0 and resource['cpuLoadPercent'] < 85
assert resource['freePhysicalMemoryKiB'] > 8_000_000
tts = read(FOLDER/'execution.json')
assert tts['generationComplete'] and tts['exitCode'] == 0 and tts['actualExitObserved']
assert tts['actualOuterSession'] == 33582 and len(tts['results']) == 2
restoration = read(FOLDER/'research-resume-verification.json')
assert restoration['restorationVerified'] and restoration['ownedCoordinatorClosed']
assert restoration['ttsLeaseToken'] == tts['leaseToken']
lease_path = ROOT/'shared/output/GPU_HANDOFF.json'
assert not lease_path.exists() or read(lease_path)['token'] != tts['leaseToken']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
                'scripts/review-video-duplicates.cjs', 'character-parameters', '--check'], cwd=ROOT, check=True)
for key in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
    os.environ[key] = '2'
os.environ.update(CUDA_VISIBLE_DEVICES='', TOKENIZERS_PARALLELISM='false', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
if os.name == 'nt':
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
DEST.mkdir(); AUDIO.mkdir(parents=True)
me = psutil.Process()
state = dict(schemaVersion=1, slug='character-parameters', pid=me.pid, createTime=me.create_time(),
             commandLine=me.cmdline(), cwd=me.cwd(), sessionId=None,
             startedAt=now(), status='assembling-two-preserved-prefix-candidates',
             completed=0, total=4, cpuThreads=2, gpuJobs=0, cpuJobs=1,
             request=rel(FOLDER/'request.json'), requestSha256=sha(FOLDER/'request.json'),
             resource=resource, audioInputs=[], candidateScenes=[], results=[], exitCode=None,
             automaticApproval=False, directReview=False, candidateAdopted=False,
             narrationApproved=False, finalMixedAsrApproved=False,
             humanListening='pending', humanPronunciation='pending')
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

class Tee:
    def __init__(self, output, file): self.output = output; self.file = file
    def write(self, text): self.output.write(text); self.output.flush(); self.file.write(text); self.file.flush(); return len(text)
    def flush(self): self.output.flush(); self.file.flush()

original_stdout, original_stderr = sys.stdout, sys.stderr
with LOG.open('x', encoding='utf-8') as log:
    sys.stdout = Tee(original_stdout, log); sys.stderr = sys.stdout
    try:
        import numpy as np
        original_tts = read(BASE/'narration-tts-execution-v2.json')
        changed = {row['id']: row for row in paired['changes']}
        independent = []
        for scene in candidate_ko['scenes']:
            original = next(x for x in original_tts['results'] if x['id'] == scene['id'])
            assert sha(ROOT/original['path']) == original['sha256']
            if scene['id'] not in changed:
                state['candidateScenes'].append({**original, 'unchangedOriginalPcm':True})
                continue
            edit = changed[scene['id']]
            new = next(x for x in tts['results'] if x['id'] == scene['id']+'-p3-clarity')
            assert sha(ROOT/new['path']) == new['sha256']
            params, old_pcm = pcm(ROOT/original['path'])
            new_params, new_pcm = pcm(ROOT/new['path'])
            assert params[:3] == new_params[:3]
            retained = edit['retainedPrefixSamples']
            prefix = old_pcm[:retained*2]
            assert len(prefix) == retained*2
            quiet = np.frombuffer(prefix[-480:], dtype='<i2').astype(np.float64)
            assert np.sqrt(np.mean(quiet**2)) < 350 and np.max(np.abs(quiet)) < 1600
            gap_samples = 2400
            data = prefix + b'\x00\x00'*gap_samples + new_pcm
            full = AUDIO/(scene['id']+'-candidate-scene.wav')
            write_pcm(full, params, data)
            candidate = dict(id=scene['id'], path=rel(full), sha256=sha(full),
                             sampleRate=24000, samples=len(data)//2, seconds=len(data)/48000,
                             unchangedOriginalPcm=False, retainedOriginalPrefixSamples=retained,
                             retainedOriginalPrefixPcmSha256=hashlib.sha256(prefix).hexdigest(),
                             originalPath=original['path'], originalSha256=original['sha256'],
                             replacementPath=new['path'], replacementSha256=new['sha256'],
                             replacementStartSample=retained+gap_samples,
                             zeroGapSamples=gap_samples, exactPrefixAndWholeReplacementBytesMatched=True,
                             prefixBoundaryRms=float(np.sqrt(np.mean(quiet**2))),
                             prefixBoundaryPeak=float(np.max(np.abs(quiet))))
            state['candidateScenes'].append(candidate)
            state['audioInputs'].append(dict(id=scene['id']+'-whole-candidate', kind='whole-scene',
                                            path=rel(full), sha256=sha(full), expectedKo=scene['lines'],
                                            seconds=candidate['seconds'], samples=candidate['samples']))
            context = AUDIO/(scene['id']+'-p3-independent.wav')
            pad = 6000
            context_pcm = b'\x00\x00'*pad + new_pcm + b'\x00\x00'*pad
            write_pcm(context, new_params, context_pcm)
            independent.append(dict(id=scene['id']+'-p3-independent', kind='complete-independent-paragraph',
                                    path=rel(context), sha256=sha(context), expectedKo=[scene['lines'][2]],
                                    seconds=len(context_pcm)/48000, samples=len(context_pcm)//2,
                                    sourcePath=new['path'], sourceSha256=new['sha256'],
                                    exactWholeReplacementBytesMatched=True, zeroPaddingSamplesEachSide=pad))
        state['audioInputs'].extend(independent)
        assert len(state['candidateScenes']) == 12 and len(state['audioInputs']) == 4
        state['status'] = 'loading-current-clarity-CPU2-whisper'; checkpoint()
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        torch.set_num_threads(2); torch.set_num_interop_threads(1)
        model_path = ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
                low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager', local_files_only=True).to('cpu')
        processor = AutoProcessor.from_pretrained(str(model_path), local_files_only=True)
        transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
                               feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
        for row in state['audioInputs']:
            state['status'] = 'transcribing-'+row['id']; checkpoint()
            assert sha(ROOT/row['path']) == row['sha256']
            result = transcriber(str(ROOT/row['path']), generate_kwargs={'language':'korean', 'task':'transcribe'}, return_timestamps='word')
            output = {**row, 'text':result['text'], 'words':result['chunks'],
                      'expectedWasRecognizerPrompt':False, 'directReview':False, 'approved':False}
            assert sha(ROOT/row['path']) == row['sha256']
            state['results'].append(output)
            save(DEST/(row['id']+'.json'), output)
            save(DEST/'asr.json', dict(complete=len(state['results'])==4, results=state['results'], automaticApproval=False))
            state['completed'] = len(state['results']); checkpoint()
            print(json.dumps(dict(id=row['id'], text=output['text']), ensure_ascii=False), flush=True)
        for row in request['protectedInputs']:
            assert sha(ROOT/row['path']) == row['sha256'], row['path']
        state.update(status='four-clarity-texts-awaiting-direct-review', exitCode=0,
                     finishedAt=now(), cpuJobs=0, all25ProtectedInputsUnchanged=True)
        checkpoint()
    except BaseException:
        state.update(status='failed-clarity-CPU-ASR-preserve-candidates', exitCode=1,
                     finishedAt=now(), cpuJobs=0, error=traceback.format_exc())
        checkpoint(); traceback.print_exc(); raise
    finally:
        sys.stdout, sys.stderr = original_stdout, original_stderr
