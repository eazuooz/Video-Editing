"""Resolve whole-scene ASR's zero-duration terminal insertion; no automatic approval."""
from pathlib import Path
import hashlib, json, os
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/motion-sickness-games/production/v2-end-context'
SOURCE = ROOT / 'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v2'
BASE.mkdir(parents=True, exist_ok=True)
if (BASE / 'asr.json').exists():
    raise RuntimeError('Existing context evidence must be inspected, not overwritten.')
requests = [('05', 47.8, 55.72, '전체 마지막 문단과 임의 자막 감사 인사 유무'),
            ('05', 53.2, 55.72, '보이는 이동과 조준의 관계부터 설명해야 합니다.'),
            ('07', 16.6, 26.5, '서로 다른 컷이므로 연속 플레이로 읽지는 마세요.'),
            ('10', 31.0, 41.12, '사람마다 다르므로 별도의 피드백과 불편함을 참게 하지 않음')]
torch.set_num_threads(2)
model_path = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
    low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager').to('cpu')
processor = AutoProcessor.from_pretrained(str(model_path))
transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
results = []
for i, (sid, start, end, focus) in enumerate(requests, 1):
    source = SOURCE / 'chunks' / f'{sid}-scene.wav'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    cache = json.loads((SOURCE / 'asr' / f'{sid}.json').read_text(encoding='utf-8'))
    assert cache['audio_sha256'] == digest
    audio, rate = sf.read(source, dtype='int16')
    cut = BASE / f'{i:02d}-{sid}.wav'
    sf.write(cut, audio[round(start*rate):round(end*rate)], rate, subtype='PCM_16')
    raw = transcriber(str(cut), generate_kwargs={'language': 'korean', 'task': 'transcribe'},
        return_timestamps='word')
    row = {'scene': sid, 'source': source.relative_to(ROOT).as_posix(), 'sourceSha256': digest,
        'from': start, 'to': end, 'focus': focus, 'text': raw['text'], 'words': raw['chunks']}
    results.append(row)
    (BASE / 'asr.json').write_text(json.dumps({'pid': os.getpid(), 'device': 'cpu',
        'complete': len(results) == len(requests), 'results': results,
        'humanListening': 'pending', 'automaticallyApproved': False},
        ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in row.items() if k != 'words'}, ensure_ascii=False), flush=True)
