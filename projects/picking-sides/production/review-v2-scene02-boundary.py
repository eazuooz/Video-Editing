"""Independent CPU read-back of the bridge and the unchanged splice boundary."""
from pathlib import Path
import hashlib
import json
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'projects/picking-sides/production/existing-game-replan/boundary02'
DEST.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(2)
model_id = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_id), dtype=torch.float32,
    low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager').to('cpu')
processor = AutoProcessor.from_pretrained(str(model_id))
transcribe = pipeline('automatic-speech-recognition', model=model,
    tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor,
    dtype=torch.float32, device='cpu')
jobs = [
    ('bridge', 'qwen3-1.7b-balanced-v2-bridge02', 0),
    ('composite-tail', 'qwen3-1.7b-balanced-v2', 23),
]
reports = []
for name, folder, start in jobs:
    source = ROOT / 'shared/output/narration/picking-sides' / folder / 'chunks/02-scene.wav'
    pcm, rate = sf.read(source, dtype='int16')
    excerpt = DEST / (name + '.wav')
    sf.write(excerpt, pcm[round(start*rate):], rate, subtype='PCM_16')
    result = transcribe(str(excerpt), generate_kwargs={'language':'korean', 'task':'transcribe'},
                        return_timestamps='word')
    reports.append({'kind':name, 'source':source.relative_to(ROOT).as_posix(),
        'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'sourceStart':start, 'result':result})
    print(name, result['text'], flush=True)
(DEST / 'asr.json').write_text(json.dumps({'directReview':'pending',
    'humanListening':'pending','reports':reports}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
