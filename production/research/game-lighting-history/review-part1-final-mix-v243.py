"""Recognize the current mix, without expected-text prompting or automatic approval."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['OMP_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,argparse,traceback,psutil
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
OUT=ROOT/'production/research/game-lighting-history/local/part1-mixed-asr-v243'
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
assert read(P/'part1-final-mix-execution-v242.json')['status']=='complete-mix-awaiting-direct-review'
# Paragraph metadata can span inserted material at fractional original sample boundaries.
# Use complete literal cue spans to order semantic text, not that historical floor.
paragraphs=[]
for p in plan['paragraphs']:
 cues=p['koCues'];assert cues
 paragraphs.append({'id':p['id'],'ko':p['ko'],'first':min(c['fromFrame'] for c in cues),'last':max(c['toFrame'] for c in cues)})
paragraphs.sort(key=lambda p:p['first']);assert len(paragraphs)==77
assert all(a['last']<=b['first'] for a,b in zip(paragraphs,paragraphs[1:]))
windows=[];group=[]
def whole(g):
 n=len(windows)+1
 lo=120 if not windows else windows[-1]['toFrame'];hi=plan['finalFrames']-600 if g[-1] is paragraphs[-1] else g[-1]['last']
 windows.append({'label':f'whole-{n:02d}','mode':'whole-chunked-30-stride5','fromFrame':lo,'toFrame':hi,'expectedKo':[p['ko'] for p in g],'paragraphIds':[p['id'] for p in g],'scope':'Complete contiguous current-mix region; all literal paragraphs are included once in whole coverage.'})
for p in paragraphs:
 if group and p['last']-group[0]['first']>150*60:whole(group);group=[]
 group.append(p)
whole(group)
assert windows[0]['fromFrame']==120 and windows[-1]['toFrame']==(plan['finalFrames']-600)
assert sum(w['toFrame']-w['fromFrame'] for w in windows)==plan['bodyFrames']
assert [i for w in windows for i in w['paragraphIds']]==[p['id'] for p in paragraphs]
targets=['part1-overview','04-guide-vsm-motion','shadow-wheel-change','runtime-texture-size','texture-scene-return','tsr-silhouette-history','tsr-rotation-vectors','horizon-detail-motion','outer-displayed-frames','cyber-light-reconstruction','cyber-surface-observation','geometry-barrier-views','geometry-car-material','mobile-compiler-availability','fortnite-mobile-test','rivalry-mobile-history','rivalry-surface-observation','four-game-transfer-conclusion','part1-conclusion']
for target in targets:
 i=next(i for i,p in enumerate(paragraphs) if p['id']==target)
 # Complete neighboring sentences, never an arbitrary truncated tail.
 g=paragraphs[max(0,i-1):i+1] if i else paragraphs[:1]
 lo=max(120,g[0]['first']-12);hi=min((plan['finalFrames']-600),g[-1]['last']+12)
 windows.append({'label':'context-'+target,'mode':'independent-sequential-long-form','fromFrame':lo,'toFrame':hi,'expectedKo':[p['ko'] for p in g],'paragraphIds':[p['id'] for p in g],'scope':'Complete semantic context at a repaired/critical join; independent recognition, current Nimbus mix.'})
request={'preparedAt':stamp(),'mixSha256':settings['wavSha256'],'planSha256':sha(PP),'windows':windows,'wholeParagraphCount':77,'wholeRegionCount':len(windows)-len(targets),'independentContextCount':len(targets),'wholeBodyFramesCoveredOnce':plan['bodyFrames'],'device':'cpu','cpuThreads':2,'gpuJobs':0,'expectedTextUsedAsPrompt':False,'automaticApproval':False,'allWholeAndIndependentTextsDirectlyCompared':False,'finalMixedAsrApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending'}
RP=P/'part1-final-mixed-asr-request-v243.json'
if RP.exists():
 old=read(RP);assert old['windows']==windows and old['mixSha256']==request['mixSha256'] and old['planSha256']==request['planSha256']
else:save(RP,request)
if args.plan_only:
 print(json.dumps({'wholeRegions':request['wholeRegionCount'],'contexts':len(targets),'total':len(windows),'paragraphs':77,'approved':False}));raise SystemExit
SP=P/'part1-final-mixed-asr-execution-v243.json';assert not SP.exists(),'Preserve previous execution and outputs; explicit resume only'
me=psutil.Process();resources=[]
for proc in psutil.process_iter(['pid','name','cmdline','create_time']):
 d=proc.info;cmd=' '.join(d['cmdline'] or [])
 if 'python' in (d['name'] or '').lower() or 'ffmpeg' in (d['name'] or '').lower():resources.append(d)
 if 'game-lighting-history' in cmd and (d['name'] or '').lower()=='ffmpeg.exe':raise RuntimeError('Owned media worker still active')
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
state={'startedAt':stamp(),'status':'loading-local-CPU-model','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},'resources':{'processes':resources,'gpu':gpu},'results':[],'currentWindow':None,'total':len(windows),'cpuThreads':2,'gpuJobs':0,'mixSha256':settings['wavSha256'],'planSha256':sha(PP),'expectedTextUsedAsPrompt':False,'automaticApproval':False,'finalMixedAsrApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending'}
def checkpoint():
 save(SP,state);p=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(p);j['episode04Part1MixedAsrV147']={'execution':rel(SP),'status':state['status'],'worker':state['worker'],'completed':len(state['results']),'total':len(windows),'currentWindow':state['currentWindow'],'finalApproved':False};j['ownedActiveWork']={'type':'part1-final-mixed-asr','execution':rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Read all whole/independent results and current PCM before pair rendering'} if state['status']!='complete' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct current mixed-ASR comparison'};j['updatedAt']=stamp();save(p,j)
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
  opts={'generate_kwargs':{'language':'korean','task':'transcribe'},'return_timestamps':'word'}
  if w['mode'].startswith('whole'):opts.update(chunk_length_s=30,stride_length_s=5)
  result=recognizer({'raw':samples,'sampling_rate':16000},**opts)
  row={'completedAt':stamp(),'mixSha256':state['mixSha256'],'planSha256':state['planSha256'],'window':w,'windowSha256':sha(wav),'sourceSamples':len(audio),'sampleRate':48000,'expectedTextUsedAsPrompt':False,'text':result['text'],'words':result['chunks'],'directFullTextCompared':False,'wordEndingsAndTimestampsCompared':False,'contentApproved':False,'humanWholeListening':'pending','humanPronunciation':'pending'};save(dest,row)
  state['results'].append({'label':w['label'],'path':rel(dest),'sha256':sha(dest)});state['status']='between-windows';checkpoint();print(json.dumps({'done':len(state['results']),'total':len(windows),'label':w['label']},ensure_ascii=False),flush=True)
 assert sha(mix)==state['mixSha256'];state.update(status='complete',exitCode=0,completedAt=stamp(),currentWindow=None);checkpoint()
except BaseException:
 state.update(status='failed',exitCode=1,failedAt=stamp(),error=traceback.format_exc());checkpoint();raise
