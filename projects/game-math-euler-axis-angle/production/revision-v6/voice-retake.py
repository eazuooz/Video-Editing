"""Two same-text opening retakes only; original41 PCM/ASR remain immutable.

Root grants each GPU stage after Unity's bounded sample. No automatic next
stage, cache replacement, script changes or promotion to the effective map.
"""
from pathlib import Path
import argparse,importlib.util,json,subprocess,sys,time,uuid
import psutil
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v6_asr_settings',H/'voice-review.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
v=a.v;R,P,V,LEASE=a.R,a.P,a.O,a.LEASE;D=V/'retakes/openings-v1';PLAN=H/'voice-retake-plan.json'
IDS=('v6-10','v6-32')
def prepare():
 original_plan=v.validate();done=v.read(V/'tts-current.json');assert done['status']=='complete-source-ASR-pending' and done['sceneCount']==41
 assert v.read(V/'source-asr-execution.json')['status']=='ASR-ready-for-direct-full-text-review'
 script=v.read(H/'voice-input.ko.json');spoken={x['id']:x for x in script['scenes']};preserved=[];jobs=[]
 for item in done['scenes']:
  source=R/item['file'];asr=V/'asr'/f'{item["id"]}.json';assert v.sha(source)==item['sha256'] and v.read(asr)['audio_sha256']==item['sha256']
  preserved.append(dict(id=item['id'],file=item['file'],sha256=item['sha256'],originalAsrFile=asr.relative_to(R).as_posix(),originalAsrSha256=v.sha(asr)))
  if item['id'] in IDS:
   text=' '.join(spoken[item['id']]['lines']);assert v.hashlib.sha256(text.encode('utf8')).hexdigest()==item['textSha256']
   jobs.append(dict(id=item['id'],text=text,textSha256=item['textSha256'],seed=2026102000+int(item['id'][-2:]),file=(D/'chunks'/f'{item["id"]}-scene.wav').relative_to(R).as_posix()))
 assert len(jobs)==2 and len(preserved)==41
 plan=dict(schemaVersion=1,revision='article-flow-v6',scope='Root-selected same-text retakes10/32 only. Preserve39 unchanged PCM and all original41PCM/ASR plus six contextual ASR results. No KO/EN/prepared text/reference/sampling changes.',
  inputs=dict(koSha256=original_plan['inputs']['koSha256'],voicePlanSha256=v.sha(H/'voice-plan.json'),preparedInputSha256=v.sha(H/'voice-input.ko.json'),originalReceiptSha256=v.sha(V/'tts-current.json'),originalFullAsrSha256=v.sha(V/'euler-article-flow-v6.asr-review.json')),
  jobs=jobs,preservedOriginal41=preserved,ttsConfiguration=v.read(H/'voice-tts-manifest.json')['tts'],
  seedPolicy='Explicit per-scene seed affects this new take only; same approved voice/model/reference/sampling.',
  ttsCapMiB=6144,ttsMinimumFreeMiB=7168,asrCapMiB=a.ASR_CAP_MIB,asrMinimumFreeMiB=a.ASR_MIN_FREE_MIB,effectiveMapPromotion='only after direct review of both new full-source ASR texts; original receipt is not overwritten',humanListening='pending')
 D.mkdir(parents=True,exist_ok=True);(D/'chunks').mkdir(exist_ok=True);(D/'asr').mkdir(exist_ok=True)
 if PLAN.exists():assert v.read(PLAN)==plan,'Existing different retake specification must be preserved/reviewed'
 else:v.save(PLAN,plan)
 return plan
def preserved(plan):
 for item in plan['preservedOriginal41']:
  assert v.sha(R/item['file'])==item['sha256'] and v.sha(R/item['originalAsrFile'])==item['originalAsrSha256'],'Original source/ASR must remain immutable'
def validate_worker(token):
 v.validate();me=psutil.Process();lease=v.read(LEASE);owner=lease['coordinator']
 assert lease['token']==token and lease['project']==P.name and any(x.pid==owner['pid'] and abs(x.create_time()-owner['createTime'])<.02 for x in [me,*me.parents()])
 plan=v.read(PLAN);preserved(plan);return plan
def tts_worker(token):
 plan=validate_worker(token)
 import torch,numpy as np,soundfile as sf
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['ttsCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
 receipt=D/'retake-current.json';old=v.read(receipt) if receipt.exists() else {'scenes':[]};by={x['id']:x for x in old['scenes']};model=None;rows=[];settings=plan['ttsConfiguration']
 for job in plan['jobs']:
  v.selected();file=R/job['file']
  if job['id'] in by:
   item=by[job['id']];assert item['textSha256']==job['textSha256'] and item['seed']==job['seed'] and v.sha(file)==item['sha256'];rows.append(item);continue
  assert not file.exists(),'Unreceipted retake must be inspected, never replaced'
  if model is None:
   model=Qwen3TTSModel.from_pretrained(str(R/settings['model']),device_map='cuda:0',dtype=torch.bfloat16)
   prompt=model.create_voice_clone_prompt(ref_audio=str(R/settings['reference']),ref_text=(R/settings['referenceText']).read_text(encoding='utf8').strip(),x_vector_only_mode=False)
  torch.manual_seed(job['seed']);torch.cuda.manual_seed_all(job['seed']);np.random.seed(job['seed'])
  print('Same-text approved-voice retake',job['id'],'seed',job['seed'],flush=True)
  audio,rate=model.generate_voice_clone(text=[job['text']],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=settings['maxNewTokens'])
  pcm=np.asarray(audio[0],dtype=np.float32);assert pcm.ndim==1 and len(pcm)>0 and np.isfinite(pcm).all();sf.write(file,pcm,rate,subtype='PCM_16')
  item=dict(id=job['id'],file=job['file'],sha256=v.sha(file),textSha256=job['textSha256'],seed=job['seed'],sampleRate=rate,samples=len(pcm),seconds=len(pcm)/rate,sourceUntrimmed=True,peakAllocatedMiB=torch.cuda.max_memory_allocated()/1048576,peakReservedMiB=torch.cuda.max_memory_reserved()/1048576,createdAt=time.time(),humanListening='pending')
  rows.append(item);v.save(receipt,dict(status='retake2-generated-ASR-direct-review-pending' if len(rows)==2 else 'partial',scenes=rows,planSha256=v.sha(PLAN),original41Preserved=True));del pcm,audio;torch.cuda.empty_cache()
 preserved(plan)
def asr_worker(token):
 plan=validate_worker(token);done=v.read(D/'retake-current.json');assert done['status']=='retake2-generated-ASR-direct-review-pending' and len(done['scenes'])==2
 model=None;pipe=None;rows=[]
 for item in done['scenes']:
  v.selected();source=R/item['file'];assert v.sha(source)==item['sha256'];cache=D/'asr'/f'{item["id"]}.json'
  if cache.exists():
   result=v.read(cache);assert result['audio_sha256']==item['sha256'];rows.append(result);continue
  if pipe is None:
   import torch
   from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
   torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(a.ASR_CAP_MIB*1048576/torch.cuda.get_device_properties(0).total_memory)
   mid=str(a.model_path());model=AutoModelForSpeechSeq2Seq.from_pretrained(mid,dtype=torch.float16,attn_implementation='eager',local_files_only=True).to('cuda:0');proc=AutoProcessor.from_pretrained(mid,local_files_only=True)
   pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
  print('Once-only changed-source ASR',item['id'],flush=True);raw=pipe(str(source),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
  result=dict(scene=item['id'],audio_sha256=item['sha256'],text=raw['text'],words=raw['chunks'],configuration=dict(chunkLengthSeconds=25,strideSeconds=3,batchSize=1,prompt=None),humanListening='pending');assert result['text'].strip() and result['words'];v.save(cache,result);rows.append(result);del raw;torch.cuda.empty_cache()
 v.save(D/'asr-review.json',dict(complete=True,sceneCount=2,scenes=rows,planSha256=v.sha(PLAN),humanListening='pending',directFullTextComparison='pending'));preserved(plan)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--gpu-approved',action='store_true');ap.add_argument('--stage',choices=['tts','asr'],default='tts');ap.add_argument('--worker');args=ap.parse_args()
 if args.worker:return tts_worker(args.worker) if args.stage=='tts' else asr_worker(args.worker)
 plan=prepare();preserved(plan)
 if args.prepare_only:print('Prepared2 same-text retakes;41original PCM/ASR hashes verified; GPU not started');return
 assert args.gpu_approved,'Root GPU handoff after Unity sample required';control=v.read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name and control['newProductionAuthorization']['fullProductionAuthorized']
 assert not LEASE.exists(),'Preserve another GPU stage';free,total,util=v.gpu();minimum=plan['ttsMinimumFreeMiB'] if args.stage=='tts' else a.ASR_MIN_FREE_MIB;assert free>=minimum
 family={x.pid for x in [psutil.Process(),*psutil.Process().parents()]};clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True);assert not any('python' in line.lower() and int(line.split(',')[0]) not in family for line in clients.splitlines())
 me=psutil.Process();token=str(uuid.uuid4());state=dict(token=token,project=P.name,state='tts_running',purpose='two same-text source retakes' if args.stage=='tts' else 'changed-two-source ASR only',coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=time.time(),foreignProcessesPaused=[],gpuBefore=dict(freeMiB=free,totalMiB=total),planSha256=v.sha(PLAN),implementationSha256=v.sha(Path(__file__)),stage=args.stage)
 with LEASE.open('x',encoding='utf8') as f:json.dump(state,f)
 code=1
 try:
  with (D/(args.stage+'-worker.log')).open('ab') as log:
   proc=subprocess.Popen([sys.executable,'-u','-X','utf8',str(Path(__file__).resolve()),'--stage',args.stage,'--worker',token],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);state.update(workerPid=proc.pid,status='running');v.save(D/(args.stage+'-execution.json'),state);code=proc.wait()
 finally:
  state.update(status='complete' if code==0 else 'failed',returnCode=code,endedAt=time.time());v.save(D/(args.stage+'-execution.json'),state)
  if LEASE.exists() and v.read(LEASE).get('token')==token:LEASE.unlink()
 preserved(plan);assert code==0,'Preserve successful retakes/caches; inspect worker log before a bounded retry'
if __name__=='__main__':main()
