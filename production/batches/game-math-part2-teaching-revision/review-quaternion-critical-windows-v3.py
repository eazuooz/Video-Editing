"""Second unprompted CPU read-back of small current-audio critical windows."""
from pathlib import Path
import hashlib,json,subprocess
import soundfile as sf,numpy as np,torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'production/batches/game-math-part2-teaching-revision/cross-game-review-20261011/quaternion-four-game-v3'
O=ROOT/'shared/output/narration/game-math-quaternion-cross-game-additions-v3/qwen3-1.7b-balanced-v1'
W=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/critical-readback-windows';W.mkdir(exist_ok=True)
torch.set_num_threads(2);model_id=str(ROOT/'qwen3-tts/models/whisper-large-v3-turbo')
model=AutoModelForSpeechSeq2Seq.from_pretrained(model_id,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to('cpu')
processor=AutoProcessor.from_pretrained(model_id)
transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
results=[]
for key,path,start,end in [('ski-prefix',O/'chunks/01-01.wav',0,3),('inverse-statement',O/'chunks/12-scene.wav',16.2,19.8),('current-pose',O/'chunks/12-02.wav',0,6),('input-vector',O/'chunks/14-01.wav',0,5),('length-conservation',O/'chunks/14-02.wav',0,4)]:
 a,sr=sf.read(path,dtype='float32');end=min(end,len(a)/sr);window=W/f'{key}.wav';sf.write(window,a[round(start*sr):round(end*sr)],sr)
 raw=transcriber(str(window),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 row=dict(key=key,source=path.relative_to(ROOT).as_posix(),sourceSha256=hashlib.sha256(path.read_bytes()).hexdigest(),start=start,end=end,unprompted=True,text=raw['text'],words=raw['chunks'],meaningAndHumanListeningApproval=False)
 results.append(row);print(key,raw['text'],flush=True)
 (R/'critical-window-readback.json').write_text(json.dumps(dict(currentAudioEvidenceOnly=True,results=results),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
