"""New complete independent contexts for observed current-mix ASR defects."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['OMP_NUM_THREADS'] = '2'; os.environ['MKL_NUM_THREADS'] = '2'
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess, traceback, psutil
ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'projects/game-lighting-history-04/production'
OUT = ROOT / 'production/research/game-lighting-history/local/part3-artifact-contexts-v152'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
stamp = lambda: datetime.now(timezone.utc).isoformat()
rel = lambda p: p.relative_to(ROOT).as_posix()
def sha(p):
 h = hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024), b''): h.update(b)
 return h.hexdigest()
def save(p, d):
 t = p.with_name(p.name + '.writing-' + str(os.getpid()))
 t.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', 'utf-8'); os.replace(t,p)
ap = argparse.ArgumentParser(); ap.add_argument('--plan-only', action='store_true'); args=ap.parse_args()
PP = P / 'part3-final-input-plan-v145.json'; plan=read(PP)
settings=read(P/'part3-final-mix-settings-v146.json'); mix=ROOT/settings['wav']
assert sha(PP)==settings['planSha256'] and sha(mix)==settings['wavSha256']
windows=[]
for label, ids, reason in [
 ('color-reference', ['tone-highlight-reference','tone-material-distinction'], 'whole-05 contains a recognizer replacement character for 구분해 보세요; complete neighboring narration is independently recognized without expected-text prompting.'),
 ('focus-blur', ['lookup-endpoint','original-22p-4'], 'whole-06 adds zero-duration farewell at29.98s and restarts at20s, repeating already recognized material; independently recognize complete LUT-to-focus/motion-blur context and terminology.'),
 ('depth-and-gbuffer', ['original-22r-5','original-22r-6'], 'whole-09 renders 가까움과 멂의 값 관계 as 가까움 과 머데 갑 관계. Independently compare the complete depth and G-buffer paragraphs, retaining reversed-Z versus G-buffer roles and human pronunciation pending.'),
 ('resource-upload', ['resource-upload-control','resource-budget-to-measure'], 'whole-10 contains a replacement character in 안 됩니다 at84.44–85.12s. Independently compare both complete current-mix upload-budget paragraphs; do not infer corrupt PCM from the raw recognizer spelling.'),
 ('conclusion-inspection', ['original-conclusion-2','original-conclusion-3','original-conclusion-4'], 'whole-11 emits repeated zero-duration 화면에 남겨주시기 바랍니다 at49.98s and obscures the first half of conclusion-3. Compare complete neighboring conclusion paragraphs without 30s stride or expected-text prompting.'),
]:
 paragraphs=[next(p for p in plan['paragraphs'] if p['id']==i) for i in ids]
 cues=[q for p in paragraphs for q in p['koCues']]
 windows.append({'label':label, 'paragraphIds':ids, 'expectedKo':[p['ko'] for p in paragraphs],
  'fromFrame':max(120,min(c['fromFrame'] for c in cues)-12),
  'toFrame':min(plan['finalFrames']-600,max(c['toFrame'] for c in cues)+12),
  'mode':'independent-sequential-long-form-no-30-second-stride', 'reason':reason})
request={'preparedAt':stamp(), 'mixSha256':settings['wavSha256'], 'planSha256':sha(PP),
 'windows':windows,'existing23WindowsRerun':False,'expectedTextUsedAsPrompt':False,
 'cpuThreads':2,'gpuJobs':0,'automaticApproval':False,'allDirectlyCompared':False}
RP=P/'part3-artifact-context-request-v152.json'
if RP.exists():
 previous=read(RP); assert previous['mixSha256']==request['mixSha256']
 if previous['windows']!=windows:
  assert not (P/'part3-artifact-context-execution-v152.json').exists() and not OUT.exists()
  assert previous['windows']==windows[:len(previous['windows'])]
  history=P/('part3-artifact-context-prepared-'+str(len(previous['windows']))+'-request-v152.json')
  if history.exists(): assert read(history)==previous
  else: save(history,previous)
  request['previousPreparedOnlyRequest']={'path':rel(history),'sha256':sha(history)}
  save(RP,request)
else: save(RP,request)
if args.plan_only:
 print(json.dumps({'newIndependentContexts':len(windows),'existingWindowsRerun':0,'approved':False})); raise SystemExit
base=read(P/'part3-final-mixed-asr-execution-v147.json')
assert base['status']=='complete' and base['exitCode']==0 and len(base['results'])==23
SP=P/'part3-artifact-context-execution-v152.json'; assert not SP.exists() and not OUT.exists()
me=psutil.Process();ancestors={p.pid for p in me.parents()}|{me.pid};resources=[]
for proc in psutil.process_iter(['pid','cmdline','name','create_time']):
 try:
  d=proc.info;cmd=' '.join(d['cmdline'] or [])
  if any(s in (d['name'] or '').lower() for s in ['python','ffmpeg']): resources.append(d)
  if d['pid'] not in ancestors and ('game-lighting-history' in cmd) and ('ffmpeg' in (d['name'] or '').lower() or any(s in cmd for s in ['review-part3-final-mix-v147.py','build-part3-annotated-visual-v148.py','build-part3-reviewed-pair-v149.py','review-part3-chunk-artifact-contexts-v152.py'])): raise RuntimeError('Owned single CPU slot active: '+str(d))
 except (psutil.NoSuchProcess,psutil.AccessDenied): pass
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.strip()
state={'startedAt':stamp(),'status':'loading-local-CPU-model','worker':{'pid':me.pid,'createTime':me.create_time(),'commandLine':me.cmdline(),'cwd':str(ROOT)},
 'resourceObservation':{'processes':resources,'gpu':gpu},'results':[],'total':len(windows),'currentWindow':None,
 'cpuThreads':2,'gpuJobs':0,'mixSha256':settings['wavSha256'],'planSha256':sha(PP),'automaticApproval':False}
def checkpoint():
 save(SP,state);cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
 j['episode04Part3ArtifactContextsV152']={'execution':rel(SP),'worker':state['worker'],'status':state['status'],'completed':len(state['results']),'total':len(windows),'approved':False}
 j['ownedActiveWork']={'type':'part3-independent-artifact-contexts','execution':rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Read all independent full results and compare current PCM before accepting observed chunk artifacts'} if state['status']!='complete' else {'status':'no-active-owned-media-worker','execution':rel(SP),'next':'Direct artifact-context comparison, native repair and gated review pair'}
 j['updatedAt']=stamp();save(cp,j)
try:
 checkpoint();import numpy as np,soundfile as sf,torch,torchaudio
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
 processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
 recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
 OUT.mkdir(parents=True)
 for w in windows:
  wave=OUT/(w['label']+'.wav');dest=wave.with_suffix('.json')
  with sf.SoundFile(mix) as f:
   assert f.samplerate==48000 and f.channels==2;f.seek(w['fromFrame']*800)
   samples=f.read((w['toFrame']-w['fromFrame'])*800,dtype='float32',always_2d=True).mean(axis=1)
  sf.write(wave,samples,48000,subtype='FLOAT');state.update(status='transcribing-'+w['label'],currentWindow=w['label']);checkpoint()
  result=recognizer({'raw':torchaudio.functional.resample(torch.from_numpy(samples),48000,16000).numpy(),'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  save(dest,{'completedAt':stamp(),'mixSha256':state['mixSha256'],'planSha256':state['planSha256'],'window':w,'windowSha256':sha(wave),'sourceSamples':len(samples),'sampleRate':48000,'text':result['text'],'words':result['chunks'],'expectedTextUsedAsPrompt':False,'directFullTextCompared':False,'contentApproved':False,'humanPronunciation':'pending'})
  state['results'].append({'label':w['label'],'path':rel(dest),'sha256':sha(dest)});checkpoint();print(json.dumps({'done':len(state['results']),'total':len(windows),'label':w['label']}),flush=True)
 assert sha(mix)==state['mixSha256'];state.update(status='complete',exitCode=0,completedAt=stamp(),currentWindow=None);checkpoint()
except BaseException:
 state.update(status='failed',exitCode=1,error=traceback.format_exc(),failedAt=stamp());checkpoint();raise
