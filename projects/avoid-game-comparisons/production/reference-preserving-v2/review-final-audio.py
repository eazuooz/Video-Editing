"""One cached whole encoded-mix recognition pass, independent of the script."""
from pathlib import Path
import sys,json,hashlib,subprocess,difflib,psutil
R=Path(__file__).resolve().parents[4];P=R/'projects/avoid-game-comparisons';O=P/'production/local/reference-preserving-v2/edit'
sys.path.insert(0,str(R/'qwen3-tts'))
from review_project_narration import normalize
assert json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['selectedVideo']==P.name
assert json.loads((O/'audio-build.json').read_text(encoding='utf8')).get('voiceGainMode')=='constant-global-gain-with-short-peak-limiter','Stop at completed encode boundary: replace the diagnosed adaptive voice normalization before final ASR'
video=O/'avoid-game-comparisons-v2-captioned.mp4';out=O/'encoded-audio.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(out)],check=True)
digest=hashlib.sha256(out.read_bytes()).hexdigest();cache=O/'final-mix-asr.json'
if cache.exists() and json.loads(cache.read_text(encoding='utf8')).get('audioSha256')==digest:print('Reusing current complete final-mix ASR')
else:
 assert not (R/'shared/output/GPU_HANDOFF.json').exists(),'Preserve another GPU lease'
 me=psutil.Process();family={p.pid for p in [me,*me.parents()]}
 assert not [p.pid for p in psutil.process_iter(['name']) if p.pid not in family and (p.info['name'] or '').lower().startswith('python')],'Another compute process must finish'
 free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>=8000
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);local=R/'qwen3-tts/models/whisper-large-v3-turbo';mid=str(local) if (local/'config.json').exists() else 'openai/whisper-large-v3-turbo';m=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float16,attn_implementation='eager',local_files_only=True).to('cuda:0');p=AutoProcessor.from_pretrained(mid,local_files_only=True)
 asr=pipeline('automatic-speech-recognition',model=m,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float16,device='cuda:0')
 result=asr(str(out),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 cache.write_text(json.dumps({'audioSha256':digest,'text':result['text'],'words':result['chunks'],'scope':'complete encoded final mix, including joins and music; direct full-text comparison required','humanListening':'pending local user review','noOtherProcessPaused':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
script=json.loads((P/'script/reference-preserving-v2/narration.tts.ko.json').read_text(encoding='utf8'));expected=' '.join(x for s in script['scenes'] for x in s['lines']);actual=json.loads(cache.read_text(encoding='utf8'))['text'];a,b=normalize(expected),normalize(actual);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
diff=[{'kind':op,'expected':a[i:j],'recognized':b[k:l]} for op,i,j,k,l in matcher.get_opcodes() if op!='equal']
(O/'final-mix-text-comparison.json').write_text(json.dumps({'similarity':matcher.ratio(),'expected':expected,'recognized':actual,'differences':diff,'reviewStatus':'pending direct reading of complete recognized text'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Final encoded mix ASR complete; similarity',matcher.ratio())
