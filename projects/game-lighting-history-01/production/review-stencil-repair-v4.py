"""Only changed07 whole/current independent paragraph context; CPU2/GPU0."""
from pathlib import Path
import datetime,hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-01'
STATE=BASE/'production/stencil-repair-asr-execution-v4.json';OUT=BASE/'production/local/stencil-repair-asr-v4'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
if STATE.exists() or OUT.exists():raise SystemExit('Inspect existing scoped recognition; never repeat complete work.')
completion=read(BASE/'production/tts-repair-completion-v4.json');audio=ROOT/completion['audio']['file'];patch=read(BASE/'production/line-repair-patch-map-v4.json')
researchVerified=completion.get('researchQueueRestorationRecorded') or (completion.get('researchStateVerified') is True and completion.get('userResearchPausePreserved') is True and completion.get('currentResearchStatus',{}).get('status')=='stopped')
if completion.get('producerExitCode')!=0 or not researchVerified or completion['preservedChunksByteIdentical']!=12 or sha(audio)!=completion['audio']['sha256']:raise SystemExit('Verified current repair and restored or independently user-paused research state required.')
review=read(BASE/'production/script-source-wording-review-v5.json')
for lang in ('ko','en'):
 if sha(BASE/f'script/narration.{lang}.json')!=review['finalInputHashes'][lang]:raise SystemExit('Reviewed source changed.')
import psutil,numpy as np,soundfile as sf,torch,torchaudio
from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
for p in psutil.process_iter(['pid','name','cmdline']):
 cmd=' '.join(p.info['cmdline'] or []).replace('\\','/')
 if p.info['pid'] not in (os.getpid(),os.getppid()) and (p.info['name'] or '').lower()=='python.exe' and 'game-lighting-history-01/production/review-' in cmd:raise SystemExit('Another owned recognizer active.')
torch.set_num_threads(2);torch.set_num_interop_threads(1)
all_pcm,sr=sf.read(audio,dtype='float32');chunk=next(c for c in completion['chunks'] if c['scene']=='07');start,end=chunk['combinedSampleRange'];data=all_pcm[start:end]
scene=next(s for s in read(BASE/'script/narration.ko.json')['scenes'] if s['id']=='07')
windows=[dict(label='whole-07',scene='07',fromSeconds=0,toSeconds=len(data)/sr,mode='chunked30s-stride5s',expectedKo=scene['lines']),dict(label='context-07',scene='07',fromSeconds=66.5,toSeconds=min(len(data)/sr,86.7+patch['durationDeltaSeconds']),mode='independent-sequential-long-form',expectedKo=scene['lines'][6],boundaryCaveat='Complete changedp7 with precedingp6/followingp8 margins. Margins may be clipped, changed paragraph must be complete.')]
def write(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
state=dict(schemaVersion=1,actualPythonIdentity=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline()),startedAt=now(),status='loading-CPU-recognizer',cpuThreads=2,gpuJobs=0,audioSha256=sha(audio),expectedWindows=2,completed=0,expectedTextUsedAsPrompt=False,currentNarrationApproved=False,preservedSceneResultsReexecuted=False,humanWholeListening='pending',windows=windows)
write(STATE,state)
modelPath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelPath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(modelPath),local_files_only=True)
asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
state.update(status='running');write(STATE,state)
for item in windows:
 part=data[round(item['fromSeconds']*sr):round(item['toSeconds']*sr)];settings=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 if item['mode']=='chunked30s-stride5s':settings.update(chunk_length_s=30,stride_length_s=5)
 result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(part),sr,16000).numpy(),sampling_rate=16000),**settings)
 write(OUT/(item['label']+'.json'),dict(**item,audioSha256=state['audioSha256'],currentTimelineStart=start/sr,pcmSha256=hashlib.sha256(part.tobytes()).hexdigest(),completedAt=now(),directFullTextCompared=False,approved=False,**result));state['completed']+=1;write(STATE,state);print('DONE '+item['label'],flush=True)
if sha(audio)!=state['audioSha256']:raise RuntimeError('Current PCM changed during review.')
state.update(status='complete-awaiting-direct-review',endedAt=now(),exitCode=0);write(STATE,state);print('Two changed07 windows complete; direct review pending.',flush=True)
