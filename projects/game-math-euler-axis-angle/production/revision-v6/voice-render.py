"""Finite V6 TTS parent/worker. Root grants GPU; original V5 PCM stays immutable."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,sys,time,uuid
import psutil
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6/voice';LEASE=R/'shared/output/GPU_HANDOFF.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,p)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
def validate():
 selected();plan=read(H/'voice-plan.json');inputs=plan['inputs']
 for key,pathkey in [('koSha256','ko'),('ttsInputSha256','ttsInput'),('manifestSha256','manifest')]:assert sha(R/inputs[pathkey])==inputs[key],f'Stale voice preparation:{pathkey}'
 for item in plan['preservedV5Chunks']:assert sha(R/item['file'])==item['sha256'],'Approved V5 PCM changed'
 return plan
def gpu():
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True)
 return list(map(int,raw.splitlines()[0].replace(' ','').split(',')))
def worker(token):
 plan=validate();lease=read(LEASE);me=psutil.Process();ancestors=[me,*me.parents()];owner=lease['coordinator']
 assert lease['token']==token and lease['project']==P.name
 assert any(x.pid==owner['pid'] and abs(x.create_time()-owner['createTime'])<.02 for x in ancestors),'Lease owner is not a live ancestor'
 import torch,numpy as np,soundfile as sf
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(6144*1048576/torch.cuda.get_device_properties(0).total_memory)
 manifest=read(H/'voice-tts-manifest.json');tts=manifest['tts'];script=read(R/manifest['paths']['script']);chunks=O/'chunks';chunks.mkdir(parents=True,exist_ok=True)
 model=None;prompt=None;receipt=O/'tts-current.json';done=read(receipt) if receipt.exists() else {'scenes':[]}
 current={x['id']:x for x in done['scenes']}
 for scene in script['scenes']:
  selected();text=' '.join(scene['lines']);text_hash=hashlib.sha256(text.encode('utf8')).hexdigest();wav=chunks/f'{scene["id"]}-scene.wav'
  if scene['id'] in current:
   old=current[scene['id']];assert old['textSha256']==text_hash and wav.exists() and sha(wav)==old['sha256'],'Existing PCM/input mismatch: inspect, never silently replace'
   print('Reused verified PCM',scene['id'],flush=True);continue
  assert not wav.exists(),'Unreceipted PCM requires inspection before retry'
  if model is None:
   model=Qwen3TTSModel.from_pretrained(str(R/tts['model']),device_map='cuda:0',dtype=torch.bfloat16)
   prompt=model.create_voice_clone_prompt(ref_audio=str(R/tts['reference']),ref_text=(R/tts['referenceText']).read_text(encoding='utf8').strip(),x_vector_only_mode=False)
  print('Rendering',scene['id'],len(text),'characters',flush=True)
  audio,rate=model.generate_voice_clone(text=[text],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=tts['maxNewTokens'])
  samples=np.asarray(audio[0],dtype=np.float32);assert samples.ndim==1 and len(samples)>0 and np.isfinite(samples).all()
  sf.write(wav,samples,rate,subtype='PCM_16')
  rms=float(np.sqrt(np.mean(samples.astype(np.float64)**2)));tail=samples[-max(1,round(rate*.05)):]
  row=dict(id=scene['id'],file=wav.relative_to(R).as_posix(),sha256=sha(wav),textSha256=text_hash,
   sampleRate=rate,samples=len(samples),seconds=len(samples)/rate,tailRatioAdvisory=float(np.sqrt(np.mean(tail**2)))/max(rms,1e-12),
   peakAllocatedMiB=torch.cuda.max_memory_allocated()/1048576,peakReservedMiB=torch.cuda.max_memory_reserved()/1048576,
   contentReview='pending whole source ASR/direct text comparison',humanListening='pending',generatedAt=time.time())
  done['scenes'].append(row);current[scene['id']]=row;done.update(status='partial',inputSha256=plan['inputs']['ttsInputSha256']);save(receipt,done)
  print('Completed',scene['id'],row['seconds'],'seconds',flush=True)
 validate();done.update(status='complete-source-ASR-pending',sceneCount=len(done['scenes']),humanWholeListening='pending');assert len(done['scenes'])==41;save(receipt,done)
def main():
 a=argparse.ArgumentParser();a.add_argument('--gpu-approved',action='store_true');a.add_argument('--worker');args=a.parse_args()
 if args.worker:return worker(args.worker)
 assert args.gpu_approved,'Root GPU allocation required; preparation is CPU-only'
 plan=validate();assert not LEASE.exists(),'Existing GPU lease preserved'
 free,total,util=gpu();assert free>=7168,(free,total,util)
 me=psutil.Process();family={x.pid for x in [me,*me.parents()]}
 clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
 assert not any('python' in line.lower() and int(line.split(',')[0]) not in family for line in clients.splitlines()),'Foreign GPU Python compute remains untouched'
 token=str(uuid.uuid4());state=dict(token=token,project=P.name,state='gpu_granted_to_tts',purpose='one finite41-scene V6 source TTS batch',coordinator=dict(pid=me.pid,createTime=me.create_time()),gpuBeforeTts=dict(freeMiB=free,totalMiB=total,utilization=util),allocatorCapMiB=6144,minimumFreeMiB=7168,clients=clients,foreignProcessesPaused=[],startedAt=time.time())
 with LEASE.open('x',encoding='utf8') as f:json.dump(state,f)
 code=1
 try:
  with (O/'tts-worker.log').open('ab') as log:
   process=subprocess.Popen([sys.executable,'-u','-X','utf8',str(Path(__file__).resolve()),'--worker',token],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   state.update(workerPid=process.pid,status='running');save(O/'tts-execution.json',state);code=process.wait()
 finally:
  state.update(status='complete' if code==0 else 'failed',returnCode=code,endedAt=time.time(),foreignProcessesRestored=[]);save(O/'tts-execution.json',state)
  if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()
 assert code==0,f'Worker failed with {code}; inspect tts-worker.log. No other application was altered.'
if __name__=='__main__':main()
