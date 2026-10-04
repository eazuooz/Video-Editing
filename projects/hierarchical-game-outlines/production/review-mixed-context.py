"""Independent short CPU windows for ambiguous whole-mix ASR tokens."""
from pathlib import Path
import hashlib, json, os
from datetime import datetime, timezone
import soundfile as sf
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'projects/hierarchical-game-outlines/production/final-v1'
DEST = WORK / 'mixed-context-v1'
assert not DEST.exists(), 'Inspect existing independent readback; never duplicate.'
DEST.mkdir()
plan = json.loads((WORK / 'plan.json').read_text(encoding='utf-8'))
manifest = json.loads((ROOT / 'projects/hierarchical-game-outlines/project.json').read_text(encoding='utf-8'))
mix = ROOT / manifest['paths']['editorAudioMix']
mix_sha = hashlib.sha256(mix.read_bytes()).hexdigest()
assert mix_sha == json.loads((WORK / 'mixed-asr/asr.json').read_text(encoding='utf-8'))['mixSha256']
audio, rate = sf.read(mix, dtype='float32', always_2d=True)
torch.set_num_threads(2)
model_path = ROOT / 'qwen3-tts/models/whisper-large-v3-turbo'
model = AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path), dtype=torch.float32,
    low_cpu_mem_usage=True, use_safetensors=True, attn_implementation='eager').to('cpu')
processor = AutoProcessor.from_pretrained(str(model_path))
transcriber = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
windows = [('03-support', '03', 27.5, 38), ('07-excerpt', '07', 7.5, 19.5),
           ('09-new-curve', '09', 0, 9), ('09-chunk-boundary', '09', 23, 38),
           ('11-independent-excerpts', '11', 46.5, 59)]
rows = []
def save(status, exit_code=None):
    (WORK / 'mixed-context-execution.json').write_text(json.dumps({
        'pid': os.getpid(), 'status': status, 'completed': len(rows), 'total': len(windows),
        'mixSha256': mix_sha, 'updatedAt': datetime.now(timezone.utc).isoformat(),
        'device': 'cpu', 'exitCode': exit_code, 'automaticallyApproved': False
    }, indent=2)+'\n', encoding='utf-8')
save('running')
for label, scene_id, start, end in windows:
    scene = next(s for s in plan['scenes'] if s['id'] == scene_id)
    a, b = scene['start'] + start, scene['start'] + end
    out = DEST / (label + '.wav')
    sf.write(out, audio[round(a*rate):round(b*rate)].mean(axis=1), rate, subtype='PCM_16')
    raw = transcriber(str(out), generate_kwargs={'language':'korean','task':'transcribe'}, return_timestamps='word')
    rows.append({'label':label, 'scene':scene_id, 'from':a, 'to':b,
        'windowSha256':hashlib.sha256(out.read_bytes()).hexdigest(), 'text':raw['text'], 'words':raw['chunks']})
    (DEST / 'asr.json').write_text(json.dumps({'mixSha256':mix_sha, 'complete':len(rows)==len(windows),
        'rows':rows, 'humanListening':'pending', 'automaticallyApproved':False}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    save('running')
    print(json.dumps({'label':label,'text':raw['text']}, ensure_ascii=False), flush=True)
save('finished', 0)
