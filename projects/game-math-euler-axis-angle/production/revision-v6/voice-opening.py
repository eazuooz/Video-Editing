"""Two short connected opening contexts; GPU only after root capture handoff.

Prefix is the actual previous lesson sentence, used as synthesis context only.
It must be excluded at a verified whole-sentence quiet seam before final use.
All original and earlier take PCM/ASR stay unchanged. No source text edits.
"""
from pathlib import Path
import argparse,importlib.util,json,re,subprocess,sys,time,uuid
import psutil
import soundfile as sf
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v6_same_voice_retake',H/'voice-retake.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
v,a=r.v,r.a;R,P,V,LEASE=r.R,r.P,r.V,r.LEASE
D=V/'retakes/opening-context-v1';PLAN=H/'voice-opening-plan.json'
r.D=D;r.PLAN=PLAN
def prepare():
 v.validate();original=v.read(V/'tts-current.json');spoken=v.read(H/'voice-input.ko.json');by={x['id']:x for x in spoken['scenes']}
 baseline=v.read(H/'voice-retake-plan.json');jobs=[];artifacts=[]
 spec=importlib.util.spec_from_file_location('v6_seam_wave',H/'voice-pacing.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
 for sid,previous,end,next_start in [('v6-10','v6-09',15.64,15.86),('v6-32','v6-31',18.20,18.50)]:
  prefix=re.split(r'(?<=[.!?])\s+',by[previous]['lines'][-1].strip())[-1]
  target=' '.join(by[sid]['lines'][:2]);text=prefix+' '+target;item=next(x for x in original['scenes'] if x['id']==sid)
  pcm,rate=sf.read(R/item['file'],dtype='float32',always_2d=True);assert rate==24000
  quiet=p.quiet_seam(pcm[:,0],rate,end,next_start)
  jobs.append(dict(id=sid,text=text,textSha256=v.hashlib.sha256(text.encode('utf8')).hexdigest(),seed=2026103000+int(sid[-2:]),file=(D/'chunks'/f'{sid}-scene.wav').relative_to(R).as_posix(),
   contextOnlyPrefix=dict(scene=previous,text=prefix,repeatInFinal=False),targetSpeechLines=[1,2],targetText=target,targetTextSha256=v.hashlib.sha256(target.encode('utf8')).hexdigest(),
   originalScene=item,originalRestSeam=dict(afterLine=2,observedAsrWordGap=[end,next_start],quietCandidate=quiet,status='verified-quiet-candidate' if quiet else 'pending-physical-seam-review'),
   targetSelection='Use only verified full target opening, exclude previous-sentence prefix at actual word-safe quiet seam. No filler/no source script change.'))
 for directory in [V/'retakes/openings-v1',V/'ambiguities']:
  for file in sorted(directory.rglob('*')):
   if file.is_file() and file.suffix in ['.json','.wav']:artifacts.append(dict(file=file.relative_to(R).as_posix(),sha256=v.sha(file)))
 plan=dict(schemaVersion=1,revision='article-flow-v6',scope='Two short existing-previous-sentence+unchanged-first2paragraph synthesis contexts, no full-scene random retries; final excludes prefix.',
  inputs=baseline['inputs'],jobs=jobs,preservedOriginal41=baseline['preservedOriginal41'],preservedPriorArtifacts=artifacts,
  ttsConfiguration=baseline['ttsConfiguration'],ttsCapMiB=6144,ttsMinimumFreeMiB=7168,asrCapMiB=a.ASR_CAP_MIB,asrMinimumFreeMiB=a.ASR_MIN_FREE_MIB,
  sourceScriptChanged=False,wholeSourcePcmPreserved=True,effectiveMapPromotion='only after entire new context ASR/direct review, verified target/old-rest quiet joins and exact fragment proof',humanListening='pending')
 D.mkdir(parents=True,exist_ok=True);(D/'chunks').mkdir(exist_ok=True);(D/'asr').mkdir(exist_ok=True)
 if PLAN.exists():assert v.read(PLAN)==plan,'Preserve an existing different context plan'
 else:v.save(PLAN,plan)
 return plan
def preserve_all(plan):
 r.preserved(plan)
 for item in plan['preservedPriorArtifacts']:assert v.sha(R/item['file'])==item['sha256'],'Earlier raw take/context evidence changed'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--gpu-approved',action='store_true');ap.add_argument('--stage',choices=['tts','asr'],default='tts');ap.add_argument('--worker');args=ap.parse_args()
 if args.worker:
  plan=v.read(PLAN);preserve_all(plan)
  (r.tts_worker if args.stage=='tts' else r.asr_worker)(args.worker)
  preserve_all(plan);return
 plan=prepare();preserve_all(plan)
 if args.prepare_only:
  print('Prepared2 short original-text contexts; GPU not started; prefix excluded from eventual final.',[(x['id'],x['originalRestSeam']['status']) for x in plan['jobs']]);return
 assert args.gpu_approved,'Root handoff after fullUnity capture required';control=v.read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name and control['newProductionAuthorization']['fullProductionAuthorized']
 assert not LEASE.exists();free,total,util=v.gpu();assert free>=plan['ttsMinimumFreeMiB']
 family={x.pid for x in [psutil.Process(),*psutil.Process().parents()]};clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True);assert not any('python' in line.lower() and int(line.split(',')[0]) not in family for line in clients.splitlines())
 me=psutil.Process();token=str(uuid.uuid4());state=dict(token=token,project=P.name,state='tts_running',purpose='two bounded opening-context '+args.stage,coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=time.time(),foreignProcessesPaused=[],gpuBefore=dict(freeMiB=free,totalMiB=total),planSha256=v.sha(PLAN),implementationSha256=v.sha(Path(__file__)),stage=args.stage)
 with LEASE.open('x',encoding='utf8') as f:json.dump(state,f)
 code=1
 try:
  with (D/(args.stage+'-worker.log')).open('ab') as log:
   proc=subprocess.Popen([sys.executable,'-u','-X','utf8',str(Path(__file__).resolve()),'--stage',args.stage,'--worker',token],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state.update(workerPid=proc.pid,status='running');v.save(D/(args.stage+'-execution.json'),state);code=proc.wait()
 finally:
  state.update(status='complete' if code==0 else 'failed',returnCode=code,endedAt=time.time());v.save(D/(args.stage+'-execution.json'),state)
  if LEASE.exists() and v.read(LEASE).get('token')==token:LEASE.unlink()
 preserve_all(plan);assert code==0,'Preserve successful context takes/caches and inspect explicit log'
if __name__=='__main__':main()
