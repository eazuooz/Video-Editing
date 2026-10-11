"""Bounded unprompted readback resolves chunk-overlap/word-count ambiguities."""
from pathlib import Path
import json,hashlib,os,argparse
parser=argparse.ArgumentParser();parser.add_argument('--extra',action='store_true');args=parser.parse_args()
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
import soundfile as sf,torch,psutil
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).parent/'cross-game-review-20261011/quaternion-four-game-v3'
W=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/baseline-diagnostic-windows'
W.mkdir(exist_ok=True)
assert psutil.virtual_memory().available>8_000_000_000
torch.set_num_threads(2);torch.set_num_interop_threads(1)
modelpath=str(ROOT/'qwen3-tts/models/whisper-large-v3-turbo')
model=AutoModelForSpeechSeq2Seq.from_pretrained(modelpath,dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
proc=AutoProcessor.from_pretrained(modelpath,local_files_only=True)
transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
target=R/'baseline-diagnostic-readback.json'
rows=json.loads(target.read_text(encoding='utf8')) if args.extra else []
windows=[('N08',17.8,27.5,'Full-scene readback collapsed the repeated two in sqrt2 divided by2.'),('20',92,108.2,'Verify whether the whole-scene next-video greeting is a recognition hallucination.')]
if not args.extra:windows=[('06',20,37,'30s chunk overlap generated a zero-duration thank-you and repeated the earlier20s words.'),('09',19.8,28.7,'Full-scene transcript collapsed the four repeated zero components.'),('12',0,10,'Full-scene first-word hallucination before conjugate definition.'),('N01',15.3,20,'Unit definition was shortened by full-scene readback.'),('F02',11.5,17,'Inverse/cancellation homophones in the conclusion.'),('QF00',0,4,'Ski-prefix recognition in current final AAC.'),('18',5,22,'A inverse was written as a passport homophone in full-scene recognition.')]
for ident,start,end,reason in windows:
 episode='calculations' if ident in ['18','N08','20'] else 'foundations'
 source=ROOT/f'shared/output/game-math-quaternion-{episode}-v3/mixed-asr-v3/{ident}.wav'
 a,sr=sf.read(source,dtype='float32',always_2d=True)
 assert sr==48000
 window=W/f'{ident}.wav';sf.write(window,a[round(start*sr):round(end*sr)],sr)
 raw=transcriber(str(window),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 row={'scene':ident,'source':source.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'start':start,'end':end,'reason':reason,'text':raw['text'],'words':raw['chunks'],'expectedTextUsedAsPrompt':False,'humanListening':'pending','automaticApproval':False}
 rows.append(row)
 target.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(ident,raw['text'],flush=True)
