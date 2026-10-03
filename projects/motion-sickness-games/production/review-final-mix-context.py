"""Independent CPU readback of four ambiguous full-mix ASR spans."""
from pathlib import Path
import hashlib, json, os
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/motion-sickness-games/production/final-v1'
DEST = BASE / 'mixed-context'
DEST.mkdir(parents=True, exist_ok=True)
assert not (DEST / 'asr.json').exists(), 'Inspect existing evidence; never overwrite it.'
plan = json.loads((BASE / 'plan.json').read_text(encoding='utf-8'))
report = json.loads((BASE / 'mixed-asr/asr.json').read_text(encoding='utf-8'))
assert report['complete'] and len(report['results']) == 12
mix = ROOT / report['mix']
digest = hashlib.sha256(mix.read_bytes()).hexdigest()
assert digest == report['mixSha256']
audio, rate = sf.read(mix, dtype='float32', always_2d=True)
requests = [('03', 18.8, 27.6, '에임 모드라고 해서 카메라가 언제나 완전히 고정되는 것은 아닙니다.'),
            ('04', 0, 10.6, '시점을 돌리는 입력, 도구의 조준, 걸을 때의 흔들림'),
            ('06', 21.2, 31.5, '지금 도식의 옵션 목록은 설계 제안입니다.'),
            ('07', 14.7, 26.6, '서로 다른 컷이므로 연속 플레이로 읽지는 마세요.')]
torch.set_num_threads(2)
model_path = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
    low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager').to('cpu')
processor = AutoProcessor.from_pretrained(str(model_path))
transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
results = []
for i, (sid, start, end, focus) in enumerate(requests, 1):
    scene = next(s for s in plan['scenes'] if s['id'] == sid)
    absolute_start, absolute_end = scene['start'] + start, scene['start'] + end
    cut = DEST / f'{i:02d}-{sid}.wav'
    sf.write(cut, audio[round(absolute_start*rate):round(absolute_end*rate)].mean(axis=1),
        rate, subtype='PCM_16')
    raw = transcriber(str(cut), generate_kwargs={'language':'korean','task':'transcribe'},
        return_timestamps='word')
    row = {'scene':sid, 'from':absolute_start, 'to':absolute_end, 'localFrom':start,
        'localTo':end, 'windowSha256':hashlib.sha256(cut.read_bytes()).hexdigest(),
        'focus':focus, 'text':raw['text'], 'words':raw['chunks']}
    results.append(row)
    (DEST / 'asr.json').write_text(json.dumps({'pid':os.getpid(), 'device':'cpu',
        'mix':report['mix'], 'mixSha256':digest, 'complete':len(results)==len(requests),
        'results':results, 'humanListening':'pending', 'automaticallyApproved':False},
        ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in row.items() if k != 'words'}, ensure_ascii=False), flush=True)
