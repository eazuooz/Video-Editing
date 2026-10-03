"""Single CPU readback of all twelve current mixed narration windows."""
from pathlib import Path
import hashlib, json, os
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'projects/motion-sickness-games/production/final-v1'
DEST = WORK / 'mixed-asr'
DEST.mkdir(parents=True, exist_ok=True)
if (DEST / 'asr.json').exists():
    raise RuntimeError('Inspect existing mixed readback; do not run a duplicate.')
plan = json.loads((WORK / 'plan.json').read_text(encoding='utf-8'))
script = json.loads((ROOT / 'projects/motion-sickness-games/script/narration.ko.json').read_text(encoding='utf-8'))
manifest = json.loads((ROOT / 'projects/motion-sickness-games/project.json').read_text(encoding='utf-8'))
mix = ROOT / manifest['paths']['editorAudioMix']
mix_sha = hashlib.sha256(mix.read_bytes()).hexdigest()
audio, rate = sf.read(mix, dtype='float32', always_2d=True)
assert rate == 48000 and abs(len(audio)/rate-plan['seconds']) < 1/rate
torch.set_num_threads(2)
model_path = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
    low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager').to('cpu')
processor = AutoProcessor.from_pretrained(str(model_path))
transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
rows = []
for scene in plan['scenes']:
    start, end = scene['start'], scene['start'] + scene['voiceSeconds']
    out = DEST / f"{scene['id']}.wav"
    sf.write(out, audio[round(start*rate):round(end*rate)].mean(axis=1), rate, subtype='PCM_16')
    raw = transcriber(str(out), generate_kwargs={'language':'korean','task':'transcribe'},
        chunk_length_s=30, return_timestamps='word')
    row = {'scene':scene['id'], 'from':start, 'to':end,
        'windowSha256':hashlib.sha256(out.read_bytes()).hexdigest(),
        'expected':next(s['lines'] for s in script['scenes'] if s['id']==scene['id']),
        'text':raw['text'], 'words':raw['chunks']}
    rows.append(row)
    (DEST / 'asr.json').write_text(json.dumps({'pid':os.getpid(), 'device':'cpu', 'mixSha256':mix_sha,
        'mix':mix.relative_to(ROOT).as_posix(), 'complete':len(rows)==12, 'results':rows,
        'humanListening':'pending', 'automaticallyApproved':False}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'scene':scene['id'], 'text':row['text']}, ensure_ascii=False), flush=True)
