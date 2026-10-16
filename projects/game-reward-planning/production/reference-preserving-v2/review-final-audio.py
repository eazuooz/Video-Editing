from pathlib import Path
import sys,json,hashlib,subprocess,difflib
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-reward-planning';O=P/'production/local/reference-preserving-v2/edit';N=R/'shared/output/narration/game-reward-planning/reference-preserving-v2';sys.path.insert(0,str(R/'qwen3-tts'))
from gpu_handoff_guard import schedule_gpu_handoff
from review_project_narration import normalize
video=O/'game-reward-planning-v2-clean.mp4';out=O/'encoded-audio.wav';subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(out)],check=True)
digest=hashlib.sha256(out.read_bytes()).hexdigest();cache=O/'final-mix-asr.json'
if cache.exists() and json.loads(cache.read_text(encoding='utf8')).get('audioSha256')==digest:print('Reusing current complete final-mix ASR')
else:
 schedule_gpu_handoff('game-reward-planning','cuda:0',False,11000)
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);mid='openai/whisper-large-v3-turbo';m=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float16,attn_implementation='eager').to('cuda:0');p=AutoProcessor.from_pretrained(mid);asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float16,device='cuda:0')
 result=asr(str(out),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word');cache.write_text(json.dumps({'audioSha256':digest,'text':result['text'],'words':result['chunks'],'scope':'complete encoded final mix, including scene joins and music; manual full-text comparison required','humanListening':'pending user Drive review'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
script=json.loads((P/'script/reference-preserving-v2/narration.tts.ko.json').read_text(encoding='utf8'));expected=' '.join(x for s in script['scenes'] for x in s['lines']);actual=json.loads(cache.read_text(encoding='utf8'))['text'];a,b=normalize(expected),normalize(actual);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
diff=[{'kind':op,'expected':a[i:j],'recognized':b[k:l]} for op,i,j,k,l in matcher.get_opcodes() if op!='equal'];(O/'final-mix-text-comparison.json').write_text(json.dumps({'similarity':matcher.ratio(),'expected':expected,'recognized':actual,'differences':diff,'reviewStatus':'pending direct reading of complete recognized text'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Final encoded mix ASR complete; similarity',matcher.ratio())
