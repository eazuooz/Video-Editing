"""Read actual final mixed audio, per scene and as one body; listening approval is separate."""
from pathlib import Path
import json,hashlib,subprocess,time
import numpy as np,soundfile as sf,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).parent/'final-v1'
m=json.loads((ROOT/'projects/game-writing/project.json').read_text(encoding='utf-8'));plan=json.loads((WORK/'plan.json').read_text(encoding='utf-8'))
source=ROOT/m['paths']['audioMix'];digest=hashlib.sha256(source.read_bytes()).hexdigest();dest=WORK/'mixed-asr';dest.mkdir(exist_ok=True)
script=json.loads((ROOT/m['paths']['script']).read_text(encoding='utf-8'));scripts={s['id']:s for s in script['scenes']}
torch.set_num_threads(2);model_id=str(ROOT/'qwen3-tts/models/whisper-large-v3-turbo')
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');processor=AutoProcessor.from_pretrained(model_id)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
entries=[]
for scene in plan['scenes']:
    sid=scene['id'];cache=dest/f'{sid}.json'
    if cache.exists() and json.loads(cache.read_text(encoding='utf-8')).get('mixSha256')==digest:
        result=json.loads(cache.read_text(encoding='utf-8'))
    else:
        wav=dest/f'{sid}.wav';subprocess.check_call(['ffmpeg','-v','error','-y','-threads','2','-ss',str(scene['start']),'-i',str(source),'-t',str(scene['seconds']),'-ar','16000','-ac','1',str(wav)])
        raw=asr(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        result={'scene':sid,'mixSha256':digest,'start':scene['start'],'seconds':scene['seconds'],'expected':' '.join(scripts[sid]['lines']),'recognized':raw['text'],'words':raw['chunks'],'humanListening':'pending','directReview':'pending'}
        cache.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    entries.append(result);print(f"[{sid}] {result['recognized']}",flush=True)
    (WORK/'full-mix-asr.json').write_text(json.dumps({'source':m['paths']['audioMix'],'sha256':digest,'complete':len(entries)==len(plan['scenes']),'scenes':entries,'directReview':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(WORK/'full-mix-asr.txt').write_text('\n\n'.join(f"[{s['scene']}] EXPECTED: {s['expected']}\nACTUAL MIX: {s['recognized']}" for s in entries)+'\n',encoding='utf-8')
print('All actual mixed scene windows transcribed; direct comparison required.',flush=True)
