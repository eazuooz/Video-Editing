from pathlib import Path
import hashlib,json,subprocess,sys
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3];W=Path(__file__).parent/'final-v1';M=json.loads((ROOT/'projects/game-writing/project.json').read_text(encoding='utf-8'));P=json.loads((W/'plan.json').read_text(encoding='utf-8'));starts={s['id']:s['start'] for s in P['scenes']};source=ROOT/M['paths']['audioMix'];sha=hashlib.sha256(source.read_bytes()).hexdigest()
torch.set_num_threads(2);modelpath=str(ROOT/'qwen3-tts/models/whisper-large-v3-turbo');model=AutoModelForSpeechSeq2Seq.from_pretrained(modelpath,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu');proc=AutoProcessor.from_pretrained(modelpath);asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
route_only='--route-only' in sys.argv
targets=[('07',12,36)] if route_only else [('01',2.5,9.5),('04',18,29),('07',14,31),('07',29,43),('09',47.5,57.6),('10',13,25),('11',33,46)]
result=[]
for sid,a,b in targets:
    wav=W/'mixed-asr'/f'focused-{sid}-{a}.wav';subprocess.check_call(['ffmpeg','-v','error','-y','-ss',str(starts[sid]+a),'-i',str(source),'-t',str(b-a),'-ar','16000','-ac','1',str(wav)])
    r=asr(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');entry={'scene':sid,'sceneWindow':[a,b],'absoluteWindow':[starts[sid]+a,starts[sid]+b],'text':r['text'],'words':r['chunks']};result.append(entry);print(entry,flush=True)
    (W/('focused-mix-route.json' if route_only else 'focused-mix-asr.json')).write_text(json.dumps({'source':M['paths']['audioMix'],'mixSha256':sha,'complete':len(result)==len(targets),'entries':result,'directReview':'pending','humanListening':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
