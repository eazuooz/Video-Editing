"""Independent full large-v3 recognition of three unresolved mixed contexts.

The Turbo results remain evidence. This worker does not approve language or
receive expected text as a prompt. Reuse exact windows and preserve all PCM.
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
O = R / 'production/research/game-lighting-history/local/part1-independent-recognition-v275'
SP = P / 'part1-independent-recognition-execution-v275.json'
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
previousPath = P / 'part1-recognition-ambiguities-execution-v272.json'
previous = read(previousPath)
assert previous['status'] == 'complete' and previous['exitCode'] == 0
worker = previous['worker']
if psutil.pid_exists(worker['pid']):
    assert abs(psutil.Process(worker['pid']).create_time() - worker['createTime']) > .01
settings = read(P / 'part1-final-mix-settings-v242.json')
plan = P / 'part1-final-input-plan-v240.json'
assert sha(R / settings['wav']) == settings['wavSha256'] and sha(plan) == settings['planSha256']
selected = previous['selectedResults']
assert len(selected) == 3 and not SP.exists() and not O.exists()
resources = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    d = proc.info
    cmd = ' '.join(d['cmdline'] or [])
    if 'python' in (d['name'] or '').lower() or 'ffmpeg' in (d['name'] or '').lower():
        resources.append(d)
    if d['pid'] != os.getpid() and (d['name'] or '').lower().startswith('python') and any(t in cmd for t in ['review-part1-recognition-ambiguities-v272.py', 'build-part1-reviewed-pair-v252.py', 'repair-part1-observed-native-pixels-v250.py', 'review-part1-artifact-contexts-v255.py']):
        raise RuntimeError('Owned media worker still active; preserve single worker.')
    if 'game-lighting-history' in cmd and (d['name'] or '').lower() == 'ffmpeg.exe':
        raise RuntimeError('Owned FFmpeg still active.')
memory = psutil.virtual_memory()
assert memory.available > 16 * 1024**3
gpu = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader'], capture_output=True, text=True, check=True).stdout.strip()
me = psutil.Process()
state = {'startedAt': stamp(), 'status': 'acquiring-pinned-official-model',
         'worker': {'pid': me.pid, 'createTime': me.create_time(), 'commandLine': me.cmdline(), 'cwd': str(R)},
         'resourceObservation': {'processes': resources, 'gpu': gpu, 'cpuThreads': 2, 'gpuJobs': 0, 'availableMemoryBytes': memory.available},
         'currentMixSha256': settings['wavSha256'], 'planSha256': sha(plan),
         'previousExecution': {'path': rel(previousPath), 'sha256': sha(previousPath)},
         'model': {'repository': 'openai/whisper-large-v3', 'officialModelCard': 'https://huggingface.co/openai/whisper-large-v3', 'revision': None},
         'selectedResults': selected, 'results': [], 'total': 3, 'currentWindow': None,
         'expectedTextUsedAsPrompt': False, 'automaticApproval': False, 'finalMixedAsrApproved': False}
def checkpoint():
    save(SP, state)
    cp = R / 'production/research/game-lighting-history/checkpoint.json'
    j = read(cp)
    j['episode04Part1IndependentRecognitionV275'] = {'execution': rel(SP), 'status': state['status'], 'worker': state['worker'], 'completed': len(state['results']), 'total': 3, 'currentWindow': state['currentWindow'], 'approved': False}
    j['ownedActiveWork'] = {'type': 'part1-independent-full-model-recognition', 'execution': rel(SP), 'worker': state['worker'], 'cpuThreads': 2, 'gpuJobs': 0, 'next': 'Direct full independent text and word timestamps; do not infer pronunciation from math or PCM'} if state['status'] not in ['complete', 'failed'] else {'status': 'no-active-owned-media-worker', 'execution': rel(SP), 'next': 'Direct independent recognition and resolve or repair actual language concerns'}
    j['updatedAt'] = stamp()
    save(cp, j)
try:
    checkpoint()
    from huggingface_hub import HfApi, snapshot_download
    info = HfApi().model_info('openai/whisper-large-v3')
    state['model']['revision'] = info.sha
    checkpoint()
    mp = R / 'qwen3-tts/models/whisper-large-v3'
    allowed = ['model.safetensors', 'config.json', 'generation_config.json', 'preprocessor_config.json', 'tokenizer.json', 'tokenizer_config.json', 'normalizer.json', 'special_tokens_map.json', 'added_tokens.json', 'merges.txt', 'vocab.json']
    downloaded = snapshot_download('openai/whisper-large-v3', revision=info.sha, local_dir=str(mp), allow_patterns=allowed, max_workers=1)
    config = read(mp / 'config.json')
    assert config['decoder_layers'] == 32
    state['model'].update(localPath=rel(mp), decoderLayers=config['decoder_layers'], weightsSha256=sha(mp / 'model.safetensors'), files=[{'path': rel(mp / name), 'sha256': sha(mp / name)} for name in allowed if (mp / name).exists()])
    state['status'] = 'loading-independent-full-CPU-model'
    checkpoint()
    import numpy as np, soundfile as sf, torch, torchaudio
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
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
        result = recognizer({'raw': samples, 'sampling_rate': 16000}, generate_kwargs={'language': 'korean', 'task': 'transcribe', 'num_beams': 1, 'do_sample': False}, return_timestamps='word')
        row = {'completedAt': stamp(), 'mixSha256': state['currentMixSha256'], 'planSha256': state['planSha256'], 'window': old['window'],
               'inputWindow': {'path': rel(wav), 'sha256': old['windowSha256'], 'currentMixedSamplesExact': True},
               'previousResult': done, 'independentModel': state['model'], 'numBeams': 1, 'doSample': False, 'expectedTextUsedAsPrompt': False,
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
