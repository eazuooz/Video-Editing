"""Independent CPU read-backs of uncertain speech and timestamp-warning tails.

These are evidence for direct review, never automatic speech approval.
"""
from pathlib import Path
import hashlib, json, os
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/hierarchical-game-outlines/production/initial-context'
SOURCE = ROOT / 'shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v1'
BASE.mkdir(parents=True, exist_ok=True)
if (BASE / 'asr.json').exists():
    raise RuntimeError('Context evidence exists; inspect it instead of repeating.')
requests = [
    ('01', 0, 9.20, 'Game name and any arbitrary opening syllables'),
    ('02', 0, 9.24, 'Outline opening; possible arbitrary class prefix'),
    ('03', 0, 8.12, 'First excerpt and curved part'),
    ('03', 26.80, 35.32, 'Curved track; full fourth paragraph'),
    ('05', 8.64, 16.80, 'Curved track and excerpt; full second paragraph'),
    ('05', 34.72, 42.98, 'Move between overall and detail; full fifth paragraph'),
    ('11', 45.40, 54.96, 'Several independent excerpts; full sixth paragraph'),
    ('12', 28.00, 39.52004166666666, 'Implementation and coaching; complete ending'),
    ('01', 26.20, 36.480041666666665, 'Last paragraph and intact ending'),
    ('04', 28.20, 37.68004166666667, 'Last paragraph and intact ending'),
    ('05', 43.00, 52.00004166666666, 'Comparison limit and intact ending'),
    ('08', 28.00, 39.200041666666665, 'Structure review and intact ending'),
]
print(f'Independent initial-context CPU ASR PID {os.getpid()}', flush=True)
torch.set_num_threads(2)
model_id = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_id), dtype=torch.float32,
    low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager').to('cpu')
processor = AutoProcessor.from_pretrained(str(model_id))
transcriber = pipeline('automatic-speech-recognition', model=model,
    tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor,
    dtype=torch.float32, device='cpu')
results = []
for i, (sid, start, end, focus) in enumerate(requests, 1):
    source = SOURCE / 'chunks' / f'{sid}-scene.wav'
    audio, rate = sf.read(source, dtype='int16')
    cache = json.loads((SOURCE / 'asr' / f'{sid}.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert cache['audio_sha256'] == digest, 'Stale source ASR'
    end = min(end, len(audio) / rate)
    cut = BASE / f'{i:02d}-{sid}.wav'
    sf.write(cut, audio[round(start*rate):round(end*rate)], rate, subtype='PCM_16')
    raw = transcriber(str(cut), generate_kwargs={'language':'korean',
        'task':'transcribe', 'num_beams':5}, return_timestamps='word')
    row = {'scene':sid, 'source':source.relative_to(ROOT).as_posix(),
        'sourceSha256':digest, 'from':start, 'to':end, 'focus':focus,
        'text':raw['text'], 'words':raw['chunks']}
    results.append(row)
    report = {'pid':os.getpid(), 'device':'cpu', 'numBeams':5,
        'complete':len(results)==len(requests), 'results':results,
        'humanListening':'pending', 'automaticallyApproved':False}
    (BASE / 'asr.json').write_text(json.dumps(report, ensure_ascii=False,
        indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in row.items() if k!='words'},
        ensure_ascii=False), flush=True)
