"""Fresh recognition only for changed current-mix windows; exact old windows reuse proofs."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil,subprocess,traceback,copy
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production';OUT=R/'production/research/game-lighting-history/local/part1-current-mixed-asr-v290'
rd=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(R).as_posix();stamp=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(t,p)
execution=rd(P/'part1-final-media-execution-v289.json');assert execution['status']=='complete-awaiting-current-mix-direct-review' and execution['exitCode']==0
worker=execution['worker'];assert not psutil.pid_exists(worker['pid']) or abs(psutil.Process(worker['pid']).create_time()-worker['createTime'])>.01
PP=P/'part1-final-input-plan-v288.json';plan=rd(PP);mixdata=rd(P/'part1-final-mix-settings-v289.json');mix=R/mixdata['wav'];reuse=rd(P/'part1-current-mixed-window-reuse-v289.json')
assert sha(PP)==reuse['planSha256']==mixdata['planSha256'] and sha(mix)==reuse['mixSha256']==mixdata['wavSha256']
windows=[r['window'] for r in reuse['freshRequiredWindows']];assert windows and reuse['reusedCount']+len(windows)==36
me=psutil.Process();anc={p.pid for p in me.parents()}|{me.pid};resources=[]
for proc in psutil.process_iter(['pid','name','cmdline','create_time']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline'] or [])
  if any(t in (d['name'] or '').lower() for t in ['python','ffmpeg']):resources.append(d)
  if proc.pid not in anc and 'game-lighting-history' in cmd and ('ffmpeg' in (d['name'] or '').lower() or any(t in cmd for t in ['build-part1-one-guide-media-v289.py','review-part1-changed-mix-v290.py'])):raise RuntimeError('Owned media worker live')
 except(psutil.NoSuchProcess,psutil.AccessDenied):pass
assert psutil.virtual_memory().available>16*1024**3
proof=rd(P/'part1-independent-recognition-execution-v275.json')['model'];mp=R/proof['localPath'];assert sha(mp/'model.safetensors')==proof['weightsSha256']
SP=P/'part1-current-mixed-asr-execution-v290.json';assert not SP.exists() and not OUT.exists();OUT.mkdir(parents=True)
state={'startedAt':stamp(),'status':'loading-cached-full-CPU-model','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(R)},'model':proof,'resources':{'processes':resources,'gpu':subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True).strip()},'results':[],'total':len(windows),'windows':windows,'currentWindow':None,'reusedExactWindows':reuse['reusedCount'],'cpuThreads':2,'gpuJobs':0,'planSha256':sha(PP),'mixSha256':mixdata['wavSha256'],'expectedTextUsedAsPrompt':False,'automaticApproval':False,'finalMixedAsrApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending'}
def checkpoint():
 save(SP,state);cp=R/'production/research/game-lighting-history/checkpoint.json';j=rd(cp);j['updatedAt']=stamp();j['episode04Part1CurrentMixedAsrV290']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'results':len(state['results']),'total':len(windows),'currentWindow':state['currentWindow'],'finalApproved':False};j['ownedActiveWork']={'type':'part1-changed-current-mix-CPU-ASR','execution':rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Direct fresh complete contexts and exact reuse before strict final pair'} if state['status'] not in ['complete','failed'] else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct current full text and all word timestamps; final pair/pixels/private delivery'};save(cp,j)
try:
 checkpoint()
 import numpy as np,soundfile as sf,torch,torchaudio
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(mp),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(mp),local_files_only=True)
 recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
 for w in windows:
  with sf.SoundFile(mix) as f:
   assert f.samplerate==48000 and f.channels==2;f.seek(w['fromFrame']*800);audio=f.read((w['toFrame']-w['fromFrame'])*800,dtype='float32',always_2d=True).mean(axis=1)
  wav=OUT/(w['label']+'.wav');sf.write(wav,audio,48000,subtype='FLOAT');state.update(status='transcribing-'+w['label'],currentWindow=w['label']);checkpoint()
  samples=torchaudio.functional.resample(torch.from_numpy(audio),48000,16000).numpy();options={'generate_kwargs':{'language':'korean','task':'transcribe','num_beams':1,'do_sample':False},'return_timestamps':'word'}
  if w['mode'].startswith('whole'):options.update(chunk_length_s=30,stride_length_s=5)
  result=recognizer({'raw':samples,'sampling_rate':16000},**options)
  row={'completedAt':stamp(),'mixSha256':state['mixSha256'],'planSha256':state['planSha256'],'window':w,'windowSha256':sha(wav),'sourceSamples':len(audio),'sampleRate':48000,'model':proof,'expectedTextUsedAsPrompt':False,'text':result['text'],'words':result['chunks'],'directFullTextCompared':False,'wordEndingsAndTimestampsCompared':False,'contentApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending'}
  dest=OUT/(w['label']+'.json');save(dest,row);state['results'].append({'label':w['label'],'path':rel(dest),'sha256':sha(dest)});checkpoint();print(json.dumps({'done':len(state['results']),'total':len(windows),'label':w['label']},ensure_ascii=False),flush=True)
 assert sha(mix)==state['mixSha256'];state.update(status='complete',exitCode=0,completedAt=stamp(),currentWindow=None);checkpoint()
except BaseException:
 state.update(status='failed',exitCode=1,error=traceback.format_exc(),endedAt=stamp());checkpoint();raise
