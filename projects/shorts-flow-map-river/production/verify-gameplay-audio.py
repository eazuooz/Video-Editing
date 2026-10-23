"""Full unprompted CPU ASR of changed mix; approved voice PCM is untouched."""
import os, json, hashlib, subprocess, difflib, re, time
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('gameplay_revision',Path(__file__).with_name('gameplay-revision.py'))
revision=importlib.util.module_from_spec(spec);spec.loader.exec_module(revision)
guard,P,R,O,A,sha,save,run=[getattr(revision,k) for k in ['guard','P','R','O','A','sha','save','run']]
guard(); digest=sha(O/'captioned.mp4'); target=O/'mix-asr.json'
assert not target.exists(), 'Preserve successful ASR; do not repeat without a new input.'
wav=O/'mix-16k.wav'
if not wav.exists():run(['ffmpeg','-v','error','-n','-i',str(O/'captioned.mp4'),'-vn','-ar','16000','-ac','1',str(wav)])
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['OMP_NUM_THREADS']='3'
import torch
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
torch.set_num_threads(3);torch.set_num_interop_threads(1)
model_path=R/'qwen3-tts/models/whisper-large-v3-turbo'; start=time.monotonic()
if not (model_path/'config.json').exists():model_path='openai/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,attn_implementation='eager',local_files_only=True).to('cpu')
proc=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
result=recognize(str(wav),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
expected=(P/'script/narration.ko.txt').read_text(encoding='utf-8')
norm=lambda s:re.sub(r'[^0-9a-z가-힣]','',s.lower())
report=dict(inputSha256=digest,fullInput=True,expectedTextPromptUsed=False,device='cpu',threads=3,model=str(model_path),rawRecognitionUnmodified=True,**result,expected=expected,similarity=difflib.SequenceMatcher(None,norm(expected),norm(result['text']),autojunk=False).ratio(),voiceSha256=sha(A/'voice/flow-map.wav'),elapsedSeconds=time.monotonic()-start,humanListening='not-claimed')
assert sha(O/'captioned.mp4')==digest
save(target,report);print(json.dumps({'text':result['text'],'similarity':report['similarity']},ensure_ascii=False))
