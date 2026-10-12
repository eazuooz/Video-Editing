"""Resolve only directly evidenced recognition concerns in complete independent current PCM."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1';os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,argparse,traceback,psutil
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
OUT=ROOT/'production/research/game-lighting-history/local/part1-artifact-contexts-v255'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
stamp=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.writing-'+str(os.getpid()));t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--plan-only',action='store_true');args=ap.parse_args()
PP=P/'part1-final-input-plan-v240.json';plan=read(PP);settings=read(P/'part1-final-mix-settings-v242.json');mix=ROOT/settings['wav']
assert sha(mix)==settings['wavSha256'] and sha(PP)==settings['planSha256']
progressPath=P/'part1-final-mixed-asr-direct-progress-v251.json';progress=read(progressPath)
assert progress['currentMixSha256']==settings['wavSha256'] and progress['planSha256']==sha(PP)
main=read(P/'part1-final-mixed-asr-request-v243.json')
already={p for w in main['windows'] if w['mode']=='independent-sequential-long-form' for p in w['paragraphIds']}
targets={}
for r in progress['manuallyReadResults']:
 if r.get('independentContextRequired') and not r.get('contextAlreadyRequested'):
  targets.setdefault(r['contextTarget'],[]).append({'result':r['label'],'reason':r['finding']})
 if r.get('additionalSemanticContextTarget'):
  targets.setdefault(r['additionalSemanticContextTarget'],[]).append({'result':r['label'],'reason':r['finding']})
paras=[]
for p in plan['paragraphs']:
 paras.append({'id':p['id'],'ko':p['ko'],'first':min(c['fromFrame'] for c in p['koCues']),'last':max(c['toFrame'] for c in p['koCues'])})
paras.sort(key=lambda p:p['first']);windows=[]
for target,reasons in targets.items():
 i=next(i for i,p in enumerate(paras) if p['id']==target);g=paras[max(0,i-1):min(len(paras),i+2)]
 lo=max(120,g[0]['first']-12);hi=min(plan['finalFrames']-600,g[-1]['last']+12)
 windows.append({'label':'artifact-context-'+target,'mode':'independent-sequential-long-form','target':target,'fromFrame':lo,'toFrame':hi,
  'expectedKo':[p['ko'] for p in g],'paragraphIds':[p['id'] for p in g],'directEvidence':reasons,
  'scope':'Complete preceding/target/following paragraphs from current Nimbus mix; expected text is comparison evidence only, never a recognizer prompt.'})
assert windows
RP=P/'part1-artifact-context-request-v255.json';SP=P/'part1-artifact-context-execution-v255.json'
request={'preparedAt':stamp(),'mixSha256':settings['wavSha256'],'planSha256':sha(PP),'windows':windows,'device':'cpu','cpuThreads':2,'gpuJobs':0,
 'directProgressAtPreparation':{'path':rel(progressPath),'sha256':sha(progressPath)},'expectedTextUsedAsPrompt':False,'automaticApproval':False,'allFullTextsAndTimestampsDirectlyCompared':False,'finalMixedAsrApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending'}
if RP.exists() and SP.exists():
 old=read(RP);assert old['windows']==windows and old['mixSha256']==request['mixSha256']
elif not SP.exists():save(RP,request)
if args.plan_only:
 print(json.dumps({'independentWindowsPrepared':len(windows),'targets':list(targets),'audioCreated':0,'approved':False}));raise SystemExit
execution=read(P/'part1-final-mixed-asr-execution-v243.json')
assert execution['status']=='complete' and execution['exitCode']==0 and len(execution['results'])==30
assert len(progress['manuallyReadResults'])==30,'Read all main results before defining the final concern list.'
assert not SP.exists() and not OUT.exists(),'Preserve prior execution and outputs; explicit resume only'
me=psutil.Process();resources=[]
for proc in psutil.process_iter(['pid','name','cmdline','create_time']):
 d=proc.info;cmd=' '.join(d['cmdline'] or [])
 if 'python' in (d['name'] or '').lower() or 'ffmpeg' in (d['name'] or '').lower():resources.append(d)
 if d['pid']!=me.pid and (d['name'] or '').lower().startswith('python') and any(t in cmd for t in ['review-part1-final-mix-v243.py','repair-part1-observed-native-pixels-v250.py','build-part1-reviewed-pair-v252.py','extract-part1-final-pixels-v253.py']):raise RuntimeError('Preserve the actual single owned media worker.')
 if 'game-lighting-history' in cmd and (d['name'] or '').lower()=='ffmpeg.exe':raise RuntimeError('Owned media worker still active')
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
state={'startedAt':stamp(),'status':'loading-local-CPU-model','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},
 'resources':{'processes':resources,'gpu':gpu},'results':[],'currentWindow':None,'total':len(windows),'cpuThreads':2,'gpuJobs':0,'mixSha256':settings['wavSha256'],'planSha256':sha(PP),'expectedTextUsedAsPrompt':False,'automaticApproval':False,'finalMixedAsrApproved':False}
def checkpoint():
 save(SP,state);cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
 j['episode04Part1ArtifactContextsV255']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'completed':len(state['results']),'total':len(windows),'currentWindow':state['currentWindow'],'finalApproved':False}
 j['ownedActiveWork']={'type':'part1-independent-current-mix-concerns','execution':rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Direct all complete additional contexts and exact current PCM before mixed-ASR approval'} if state['status']!='complete' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct additional contexts and exact PCM'}
 j['updatedAt']=stamp();save(cp,j)
try:
 checkpoint()
 import numpy as np,soundfile as sf,torch,torchaudio
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 assert sf.info(mix).frames==plan['finalFrames']*800
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
 processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
 recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
 OUT.mkdir(parents=True,exist_ok=True)
 for w in windows:
  dest=OUT/(w['label']+'.json');wav=OUT/(w['label']+'.wav');assert not dest.exists() and not wav.exists()
  with sf.SoundFile(mix) as f:
   assert f.samplerate==48000 and f.channels==2;f.seek(w['fromFrame']*800);audio=f.read((w['toFrame']-w['fromFrame'])*800,dtype='float32',always_2d=True).mean(axis=1)
  sf.write(wav,audio,48000,subtype='FLOAT');state.update(status='transcribing-'+w['label'],currentWindow=w['label']);checkpoint()
  samples=torchaudio.functional.resample(torch.from_numpy(audio),48000,16000).numpy()
  result=recognizer({'raw':samples,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  row={'completedAt':stamp(),'mixSha256':state['mixSha256'],'planSha256':state['planSha256'],'window':w,'windowSha256':sha(wav),'sourceSamples':len(audio),'sampleRate':48000,
   'expectedTextUsedAsPrompt':False,'text':result['text'],'words':result['chunks'],'directFullTextCompared':False,'wordEndingsAndTimestampsCompared':False,'contentApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending'}
  save(dest,row);state['results'].append({'label':w['label'],'path':rel(dest),'sha256':sha(dest)});state['status']='between-windows';checkpoint()
  print(json.dumps({'done':len(state['results']),'total':len(windows),'label':w['label']},ensure_ascii=False),flush=True)
 assert sha(mix)==state['mixSha256'];state.update(status='complete',exitCode=0,completedAt=stamp(),currentWindow=None);checkpoint()
except BaseException:
 state.update(status='failed',exitCode=1,failedAt=stamp(),error=traceback.format_exc());checkpoint();raise
