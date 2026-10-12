"""Focused alternative decoding of unresolved words; reuse exact current-mix windows.

The expected text is never passed to the recognizer. This supplements, rather
than replaces, the full mixed-ASR review. It cannot approve its own results.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess, traceback, psutil
R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
O = R / 'production/research/game-lighting-history/local/part1-recognition-ambiguities-v272'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
rel = lambda p: p.relative_to(R).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()
def save(p, j):
    tmp = p.with_name(p.name + '.writing-' + str(os.getpid()))
    tmp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)
previousPath = P / 'part1-artifact-context-execution-v255.json'
previous = read(previousPath)
assert previous['status'] == 'complete' and previous['exitCode'] == 0
w = previous['worker']
if psutil.pid_exists(w['pid']):
    assert abs(psutil.Process(w['pid']).create_time() - w['createTime']) > .01
settings = read(P / 'part1-final-mix-settings-v242.json')
plan = P / 'part1-final-input-plan-v240.json'
assert sha(R / settings['wav']) == settings['wavSha256'] and sha(plan) == settings['planSha256']
targets = {
    'artifact-context-outer-comparison-before': 'Initial 자수의 recognized as 수의 in whole and complete context.',
    'artifact-context-runtime-texture-consumer': '정보/전구 disagreement between current whole, mixed contexts and unmixed source.',
    'artifact-context-original-18t-3': 'Quarter-pixel fraction rendered as1분의4 despite complete8x4 to4x2 explanation.'
}
selected = [r for r in previous['results'] if r['label'] in targets]
assert len(selected) == 3
resources = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    d = proc.info
    cmd = ' '.join(d['cmdline'] or [])
    if 'python' in (d['name'] or '').lower() or 'ffmpeg' in (d['name'] or '').lower():
        resources.append(d)
    if d['pid'] != os.getpid() and (d['name'] or '').lower().startswith('python') and any(t in cmd for t in ['review-part1-artifact-contexts-v255.py', 'build-part1-reviewed-pair-v252.py', 'repair-part1-observed-native-pixels-v250.py']):
        raise RuntimeError('Preserve the single actual owned media worker.')
    if 'game-lighting-history' in cmd and (d['name'] or '').lower() == 'ffmpeg.exe':
        raise RuntimeError('Owned media worker still active.')
gpu = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader'], capture_output=True, text=True, check=True).stdout.strip()
SP = P / 'part1-recognition-ambiguities-execution-v272.json'
assert not SP.exists() and not O.exists()
me = psutil.Process()
state = {'startedAt': stamp(), 'status': 'loading-local-CPU-model', 'worker': {'pid': me.pid, 'createTime': me.create_time(), 'commandLine': me.cmdline(), 'cwd': str(R)},
         'resourceObservation': {'processes': resources, 'gpu': gpu, 'cpuThreads': 2, 'gpuJobs': 0},
         'currentMixSha256': settings['wavSha256'], 'planSha256': sha(plan),
         'previousExecution': {'path': rel(previousPath), 'sha256': sha(previousPath)},
         'selectedResults': selected, 'reasons': targets, 'numBeams': 5, 'doSample': False,
         'expectedTextUsedAsPrompt': False, 'results': [], 'total': 3, 'currentWindow': None, 'automaticApproval': False, 'finalMixedAsrApproved': False}
def checkpoint():
    save(SP, state)
    cp = R / 'production/research/game-lighting-history/checkpoint.json'
    j = read(cp)
    j['episode04Part1RecognitionAmbiguitiesV272'] = {'execution': rel(SP), 'status': state['status'], 'worker': state['worker'], 'completed': len(state['results']), 'total': 3, 'currentWindow': state['currentWindow'], 'approved': False}
    j['ownedActiveWork'] = {'type': 'part1-focused-alternative-recognition', 'execution': rel(SP), 'worker': state['worker'], 'cpuThreads': 2, 'gpuJobs': 0, 'next': 'Direct all alternative word/timestamp results; preserve unresolved real pronunciation and numerical failures'} if state['status'] not in ['complete', 'failed'] else {'status': 'no-active-owned-media-worker', 'execution': rel(SP), 'next': 'Direct ambiguity results, current PCM and semantic review'}
    j['updatedAt'] = stamp()
    save(cp, j)
try:
    checkpoint()
    import numpy as np, soundfile as sf, torch, torchaudio
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    mp = R / 'qwen3-tts/models/whisper-large-v3-turbo'
    model = AutoModelForSpeechSeq2Seq.from_pretrained(str(mp), dtype=torch.float32, low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager', local_files_only=True).to('cpu')
    processor = AutoProcessor.from_pretrained(str(mp), local_files_only=True)
    recognizer = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
    O.mkdir(parents=True)
    for done in selected:
        source = R / done['path']
        assert sha(source) == done['sha256']
        old = read(source)
        assert old['mixSha256'] == state['currentMixSha256'] and old['planSha256'] == state['planSha256']
        wav = source.with_suffix('.wav')
        assert sha(wav) == old['windowSha256']
        audio, sr = sf.read(wav, dtype='float32')
        assert sr == 48000 and audio.ndim == 1 and len(audio) == old['sourceSamples']
        with sf.SoundFile(R / settings['wav']) as f:
            f.seek(old['window']['fromFrame'] * 800)
            exact = f.read(len(audio), dtype='float32', always_2d=True).mean(axis=1)
        assert np.array_equal(audio, exact)
        samples = torchaudio.functional.resample(torch.from_numpy(audio), 48000, 16000).numpy()
        state.update(status='transcribing-' + done['label'], currentWindow=done['label'])
        checkpoint()
        result = recognizer({'raw': samples, 'sampling_rate': 16000}, generate_kwargs={'language': 'korean', 'task': 'transcribe', 'num_beams': 5, 'do_sample': False}, return_timestamps='word')
        row = {'completedAt': stamp(), 'mixSha256': state['currentMixSha256'], 'planSha256': state['planSha256'], 'window': old['window'],
               'inputWindow': {'path': rel(wav), 'sha256': old['windowSha256'], 'currentMixedSamplesExact': True},
               'previousResult': done, 'numBeams': 5, 'doSample': False, 'expectedTextUsedAsPrompt': False,
               'text': result['text'], 'words': result['chunks'], 'directlyReviewed': False, 'contentApproved': False, 'humanPronunciation': 'pending'}
        dest = O / (done['label'] + '.json')
        save(dest, row)
        state['results'].append({'label': done['label'], 'path': rel(dest), 'sha256': sha(dest)})
        state.update(status='between-windows')
        checkpoint()
        print(json.dumps({'done': len(state['results']), 'total': 3, 'label': done['label']}), flush=True)
    state.update(status='complete', exitCode=0, completedAt=stamp(), currentWindow=None)
    checkpoint()
except BaseException:
    state.update(status='failed', exitCode=1, failedAt=stamp(), error=traceback.format_exc())
    checkpoint()
    raise
