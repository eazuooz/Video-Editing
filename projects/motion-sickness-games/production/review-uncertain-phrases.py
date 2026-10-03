"""A second contextual read-back of ambiguous current-v1 words; no approval."""
from pathlib import Path
import hashlib, json, os, time
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/motion-sickness-games/production/uncertain-phrases-v1'
SOURCE = ROOT / 'shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1'
BASE.mkdir(parents=True, exist_ok=True)
if (BASE / 'asr.json').exists():
    raise RuntimeError('Contextual evidence exists; review it instead of rerunning.')
requests = [
    ('04', 9.8, 19.8, '조절 값도 분리할 수 있죠.'),
    ('04', 29.0, 38.88, '한 스위치가 조준과 이동까지 뜻밖에 바꾸지 않도록'),
    ('06', 31.3, 42.72, '만능 권장값을 하나 고르는 것보다'),
    ('07', 26.5, 36.0, '가까운 판자와 기둥이 다음 방향을 찾는 단서'),
    ('10', 10.2, 19.9, '도구의 조준은 분리하지만'),
    ('11', 28.05, 38.0, '앞에서 본 에임 모드의 아이디어는'),
    ('02', 28.9, 38.24, '둘을 한 값으로 묶지 않는 것이 첫 번째 설계 질문입니다.'),
    ('08', 26.98, 38.0, '플레이어가 즉시 멈추거나 되돌릴 수 있게 해야 합니다.'),
    ('03', 27.1, 38.3, '이제 놀이기구를 씻는 장면을 보세요.'),
    ('05', 28.4, 37.3, '같은 방향을 바라보며 표면을 씻는 구간'),
]
torch.set_num_threads(2)
model_id = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_id), dtype=torch.float32,
    low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager').to('cpu')
processor = AutoProcessor.from_pretrained(str(model_id))
transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
results = []
for number, (sid, start, end, expected) in enumerate(requests, 1):
    source = SOURCE / 'chunks' / f'{sid}-scene.wav'
    audio, rate = sf.read(source, dtype='int16')
    cut = BASE / f'{number:02}-{sid}.wav'
    sf.write(cut, audio[round(start*rate):round(end*rate)], rate, subtype='PCM_16')
    raw = transcriber(str(cut), generate_kwargs={'language':'korean', 'task':'transcribe'},
        return_timestamps='word')
    result = {'scene':sid, 'source':source.relative_to(ROOT).as_posix(),
        'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'from':start, 'to':end, 'focus':expected, 'text':raw['text'], 'words':raw['chunks']}
    results.append(result)
    print(json.dumps({k:v for k,v in result.items() if k != 'words'}, ensure_ascii=False), flush=True)
    (BASE / 'asr.json').write_text(json.dumps({'pid':os.getpid(), 'device':'cpu',
        'complete':len(results)==len(requests), 'results':results,
        'humanListening':'pending', 'automaticallyApproved':False}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
