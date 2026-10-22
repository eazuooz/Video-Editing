"""Finite resumable changed-paragraph batch with one cooperative GPU lease."""
from common import *
import argparse,time,sys
def worker(plan_path):
 import psutil
 plan=read(plan_path);authorized(plan['episode'])
 for v in plan['inputs'].values():assert sha(R/v['file'])==v['sha256'],'Changed frozen input'
 O=R/plan['tts']['outputDir'];takes=O/'takes';takes.mkdir(parents=True,exist_ok=True)
 receipt=O/'paragraph-takes.json'; done=read(receipt) if receipt.exists() else dict(identitySha256=plan['identitySha256'],takes=[],status='not-started')
 assert done['identitySha256']==plan['identitySha256']
 existing={r['id']:r for r in done['takes']}
 for j in plan['jobs']:
  if j['id'] in existing:
   old=existing[j['id']];assert old['textSha256']==j['textSha256'] and sha(R/old['file'])==old['sha256']
 if len(existing)==len(plan['jobs']):print('All changed paragraphs already generated; no duplicate model job');return
 me=psutil.Process(); family={p.pid for p in [me,*me.parents()]};lease=R/'shared/output/GPU_HANDOFF.json'
 assert not lease.exists(),'Preserve existing GPU lease'
 snapshots=[];stable=0
 for _ in range(45):
  free,total,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()[0].split(','))
  clients=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
  foreign=[x for x in clients.splitlines() if 'python' in x.lower() and int(x.split(',')[0]) not in family]
  assert not foreign,'Foreign GPU Python remains untouched'
  snapshots.append(dict(freeMiB=free,totalMiB=total,utilization=util,time=now()))
  stable=stable+1 if free>=plan['resources']['minimumFreeMiB'] and util<35 else 0
  if stable>=2:break
  time.sleep(1)
 assert stable>=2,'Insufficient stable free GPU memory; nothing else stopped'
 state=dict(token=uuid.uuid4().hex,project=plan['slug'],revision=plan['revision'],coordinator=dict(pid=me.pid,createTime=me.create_time()),startedAt=now(),state='tts',gpuBefore=snapshots,identitySha256=plan['identitySha256'],foreignProcessesChanged=False)
 with lease.open('x',encoding='utf8') as f:json.dump(state,f,indent=2)
 try:
  import numpy as np,soundfile as sf,torch
  from qwen_tts import Qwen3TTSModel
  torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
  t=plan['tts'];model=Qwen3TTSModel.from_pretrained(str(R/t['model']),device_map='cuda:0',dtype=torch.bfloat16)
  prompt=model.create_voice_clone_prompt(ref_audio=str(R/t['reference']),ref_text=(R/t['referenceText']).read_text(encoding='utf8').strip(),x_vector_only_mode=False)
  for j in plan['jobs']:
   authorized(plan['episode'])
   if j['id'] in existing:continue
   path=takes/(j['id']+'.wav');assert not path.exists(),'Unreceipted take preserved'
   print('Generating',j['id'],len(j['text']),'characters',flush=True);start=time.time()
   audios,rate=model.generate_voice_clone(text=[j['text']],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=t['maxNewTokens'])
   raw=np.asarray(audios[0],dtype=np.float32);assert rate==24000 and raw.ndim==1 and len(raw)>0 and np.isfinite(raw).all()
   sf.write(path,raw,rate,subtype='FLOAT');x,rr=sf.read(path,dtype='float32');assert rr==rate and np.array_equal(x,raw)
   row=dict(id=j['id'],scene=j['scene'],line=j['line'],file=rel(path),sha256=sha(path),textSha256=j['textSha256'],seconds=len(raw)/rate,samples=len(raw),sampleRate=rate,rawFloatPeak=float(abs(raw).max()),elapsedSeconds=time.time()-start,generatedAt=now(),rawPcmPreserved=True,humanListening='pending',peakAllocatedMiB=torch.cuda.max_memory_allocated()/1048576)
   done['takes'].append(row);existing[j['id']]=row;done.update(status='partial',takeCount=len(existing));save(receipt,done)
   print('Completed',j['id'],round(row['seconds'],3),len(existing),'/',len(plan['jobs']),flush=True)
  done.update(status='complete-source-asr-pending',takeCount=len(existing));save(receipt,done);state['state']='complete'
 except BaseException as e:
  state.update(state='failed',error=str(e));raise
 finally:
  state['endedAt']=now();save(O/'voice-execution.json',state)
  if lease.exists() and read(lease).get('token')==state['token']:lease.unlink()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('plan');a=p.parse_args();worker(R/a.plan)
