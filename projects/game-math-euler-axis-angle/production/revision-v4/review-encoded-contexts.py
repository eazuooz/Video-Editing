"""One finite independent check of newly flagged encoded contexts, no script prompt."""
from pathlib import Path
import importlib.util,json,hashlib,sys,os
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import soundfile as sf
R=Path(__file__).resolve().parents[4];H=Path(__file__).parent;O=H.parent/'local/revision-v4';D=O/'encoded-contexts';D.mkdir(exist_ok=True)
if '--clarity' in sys.argv:
 O=H.parent/'local/revision-v4-clarity';D=O/'encoded-contexts';D.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('final_asr_guard',H.parent/'revision-v3/review-final-audio.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
def save(d):(D/'results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if (D/'results.json').exists() and guard.read(D/'results.json').get('status')=='complete':raise SystemExit('Already complete; preserve successful recognition')
source=O/'encoded-audio.wav';digest=guard.sha_file(source)
assert digest==guard.read(O/'final-mix-asr.json')['audioSha256']
ranges=[('07-vector',410,429.45),('14-tail',814.8,824.5),('17-landing-overlap',958,984.4),('17-negation',986.5,998.6),('20-vector-length',1195.8,1217),('24-units',1399.12,1425),('24-overlap',1436,1457.65),('25-wrap',1466,1480.03)]
if '--clarity' in sys.argv:ranges=[r for r in ranges if r[0].startswith(('20-','24-','25-'))]
audio,rate=sf.read(source,dtype='float32');assert rate==16000
report={'status':'running','audioSha256':digest,'ranges':[],'expectedPromptUsed':False,'purpose':'Only ambiguities in successful complete encoded-mix recognition; no whole-video repeat','humanListening':'pending'}
with guard.parent_lease('cuda:0'):
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(8192*1048576/torch.cuda.get_device_properties(0).total_memory)
 local=R/'qwen3-tts/models/whisper-large-v3-turbo';mid=str(local) if (local/'config.json').exists() else 'openai/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float16,attn_implementation='sdpa',local_files_only=True).to('cuda:0')
 processor=AutoProcessor.from_pretrained(mid,local_files_only=True)
 asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0')
 for name,a,b in ranges:
  guard.selected();pcm=audio[round(a*rate):round(b*rate)]
  result=asr({'raw':pcm,'sampling_rate':rate},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps=True)
  report['ranges'].append({'id':name,'in':a,'out':b,'pcmSha256':hashlib.sha256(pcm.tobytes()).hexdigest(),'text':result['text'],'chunks':result['chunks']});save(report);print(name,result['text'],flush=True)
 report['status']='complete';save(report)
