"""Review the new identical-text onset take and its complete neighbouring context.

CPU2 only. Expected narration is never supplied to the recognizer. Selection and
current-mix approval are separate subsequent direct reviews.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, traceback, subprocess, math, psutil
R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
O = R / 'production/research/game-lighting-history/local/part1-onset-take-v281'
SP = P / 'part1-onset-take-asr-execution-v281.json'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
rel = lambda p: p.relative_to(R).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''): h.update(b)
    return h.hexdigest()
def save(p, j):
    tmp = p.with_name(p.name + '.writing-' + str(os.getpid()))
    tmp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    os.replace(tmp, p)
tts = read(P / 'part1-onset-repair-tts-execution-v280.json')
assert tts['generationComplete'] and tts['exitCode'] == 0
w = tts['actualIdentity']
assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time() - w['createTime']) > .01
plan = read(P / 'part1-final-input-plan-v240.json')
rows = [next(p for p in plan['paragraphs'] if p['id'] == name) for name in ['horizon-detail-motion', 'outer-comparison-before', 'outer-displayed-frames']]
take = tts['results'][0]
assert take['id'] == rows[1]['id'] and sha(R / take['path']) == take['sha256']
assert not SP.exists() and not O.exists()
resources = []
me = psutil.Process()
ancestors = {p.pid for p in me.parents()} | {me.pid}
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    d = proc.info; cmd = ' '.join(d['cmdline'] or [])
    if 'python' in (d['name'] or '').lower() or 'ffmpeg' in (d['name'] or '').lower(): resources.append(d)
    if d['pid'] not in ancestors and 'game-lighting-history' in cmd and ((d['name'] or '').lower() == 'ffmpeg.exe' or (d['name'] or '').lower().startswith('python') and any(t in cmd for t in ['review-part1-', 'render-part1-onset-repair', 'build-part1-reviewed-pair'])):
        raise RuntimeError('Owned media worker remains active.')
assert psutil.virtual_memory().available > 16 * 1024**3
modelProof = read(P / 'part1-independent-recognition-execution-v275.json')['model']
mp = R / modelProof['localPath']
assert sha(mp / 'model.safetensors') == modelProof['weightsSha256']
state = {'startedAt': stamp(), 'status': 'loading-cached-independent-CPU-model', 'worker': {'pid': me.pid, 'createTime': me.create_time(), 'commandLine': me.cmdline(), 'cwd': str(R)},
         'resources': {'processes': resources, 'gpu': subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader'], capture_output=True, text=True, check=True).stdout.strip()},
         'cpuThreads': 2, 'gpuJobs': 0, 'newTake': take, 'model': modelProof, 'results': [], 'total': 2,
         'expectedTextUsedAsPrompt': False, 'selected': False, 'finalMixedAsrApproved': False, 'humanWholeListening': 'pending', 'humanPronunciation': 'pending'}
def checkpoint():
    save(SP, state)
    cp = R / 'production/research/game-lighting-history/checkpoint.json'; j = read(cp)
    j['episode04Part1OnsetTakeAsrV281'] = {'execution': rel(SP), 'status': state['status'], 'worker': state['worker'], 'completed': len(state['results']), 'total': 2, 'selected': False}
    j['ownedActiveWork'] = {'type': 'part1-new-onset-take-CPU-ASR', 'execution': rel(SP), 'worker': state['worker'], 'cpuThreads': 2, 'gpuJobs': 0, 'next': 'Direct first syllable and full endings in raw take and full context before measured retiming'} if state['status'] not in ['complete', 'failed'] else {'status': 'no-active-owned-media-worker', 'execution': rel(SP), 'next': 'Directly compare new take before selecting or retiming; current final-mix approval remains false'}
    j['updatedAt'] = stamp(); save(cp, j)
try:
    checkpoint()
    import numpy as np, soundfile as sf, torch, torchaudio
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(2); torch.set_num_interop_threads(1)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(str(mp), dtype=torch.float32, low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager', local_files_only=True).to('cpu')
    processor = AutoProcessor.from_pretrained(str(mp), local_files_only=True)
    recognizer = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
    O.mkdir(parents=True)
    raw, sr = sf.read(R / take['path'], dtype='float32'); assert sr == 24000 and len(raw) == take['samples'] and raw.ndim == 1
    contextParts = []; ranges = []; at = 0
    for i, row in enumerate(rows):
        pcm = take if i == 1 else row['pcm']; assert sha(R / pcm['path']) == pcm['sha256']
        data, sr = sf.read(R / pcm['path'], dtype='float32'); assert sr == 24000 and data.ndim == 1 and len(data) == pcm['samples']
        frames = math.ceil(len(data) / 400) if i == 1 else row['endFrame'] - row['startFrame']
        padded = np.pad(data, (0, frames * 400 - len(data)))
        contextParts.append(padded); ranges.append({'id': row['id'], 'fromSample': at, 'toSample': at + len(data), 'slotEndSample': at + len(padded), 'source': pcm})
        at += len(padded)
    context = np.concatenate(contextParts)
    for label, data, mapping in [('raw-new-guide', raw, [{'id': take['id'], 'fromSample': 0, 'toSample': len(raw), 'source': take}]), ('complete-neighbour-context', context, ranges)]:
        wav = O / (label + '.wav'); sf.write(wav, data, 24000, subtype='FLOAT')
        back, sr = sf.read(wav, dtype='float32'); assert np.array_equal(back, data)
        state['status'] = 'transcribing-' + label; checkpoint()
        samples = torchaudio.functional.resample(torch.from_numpy(data), 24000, 16000).numpy()
        result = recognizer({'raw': samples, 'sampling_rate': 16000}, generate_kwargs={'language': 'korean', 'task': 'transcribe', 'num_beams': 1, 'do_sample': False}, return_timestamps='word')
        row = {'completedAt': stamp(), 'label': label, 'input': {'path': rel(wav), 'sha256': sha(wav), 'samples': len(data), 'sampleRate': 24000, 'sourceSampleRanges': mapping, 'fullPcmPreserved': True}, 'model': modelProof,
               'text': result['text'], 'words': result['chunks'], 'expectedTextUsedAsPrompt': False, 'directlyReviewed': False, 'contentApproved': False, 'currentMixedAudio': False, 'humanPronunciation': 'pending'}
        dest = O / (label + '.json'); save(dest, row)
        state['results'].append({'label': label, 'path': rel(dest), 'sha256': sha(dest)})
        checkpoint(); print(json.dumps({'done': len(state['results']), 'total': 2, 'label': label}), flush=True)
    state.update(status='complete', exitCode=0, endedAt=stamp()); checkpoint()
except BaseException:
    state.update(status='failed', exitCode=1, error=traceback.format_exc(), endedAt=stamp()); checkpoint(); raise
