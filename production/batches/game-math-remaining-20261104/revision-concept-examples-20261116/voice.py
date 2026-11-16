"""Generate only the explicitly requested new example bridges, using the approved voice."""
import os,sys,time,atexit,subprocess,json,hashlib,math,argparse
from pathlib import Path
from prepare import HERE,ROOT,FF,read,save,sha
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--force',nargs='*',default=[]);ap.add_argument('--attempts',type=int,default=4);args=ap.parse_args()
 import psutil
 control=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['conceptExamplesRevision20261116']
 assert control['ttsAuthorized'] and control['scope']==[f'M{i}' for i in range(21,34)]
 lease=ROOT/'shared/output/GPU_HANDOFF.json';lease.parent.mkdir(parents=True,exist_ok=True)
 if lease.exists():raise RuntimeError('A foreign cooperative GPU lease exists. Preserve it.')
 for p in psutil.process_iter(['pid','name','cmdline','exe']):
  try:
   if p.pid==os.getpid():continue
   name=p.info['name'].lower();cmd=' '.join(p.info['cmdline'] or []).lower();exe=(p.info['exe'] or '').lower().replace('\\','/')
   gpu_ffmpeg=name=='ffmpeg.exe' and any(k in cmd for k in ('nvenc','-hwaccel cuda','-hwaccel d3d','scale_cuda','scale_npp','-hwaccel qsv','h264_amf','hevc_amf'))
   if '/steamapps/common/' in exe or name=='unrealeditor.exe' or gpu_ffmpeg or (name=='unity.exe' and ('-projectpath' in cmd or '-batchmode' in cmd)):
    raise RuntimeError(f'Active game/render/editor must be retained: {p.pid} {name}')
  except (psutil.AccessDenied,psutil.NoSuchProcess):pass
 samples=[]
 for _ in range(2):
  a=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW)
  free,total,util=[int(x.strip()) for x in a.strip().split(',')];samples.append(dict(freeMiB=free,totalMiB=total,utilization=util));assert free>=8192 and util<=40,samples;time.sleep(1)
 me=psutil.Process();state=dict(project='math-concept-examples-20261116',state='gpu_granted_to_tts',coordinator=dict(pid=me.pid,createTime=me.create_time()),scope=control['scope'],samples=samples,paidApi=False)
 with open(lease,'x',encoding='utf8') as f:json.dump(state,f)
 def release():
  if lease.exists() and read(lease).get('coordinator')==state['coordinator']:lease.unlink()
 atexit.register(release)
 sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as q
 q.load_tts_dependencies();q.torch.set_num_threads(4);q.torch.cuda.set_per_process_memory_fraction(.47)
 q.CHUNK_DIR=HERE/'local/voice/raw';q.CHUNK_DIR.mkdir(parents=True,exist_ok=True)
 q.MODEL_DIR=ROOT/'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base';q.REFERENCE=ROOT/'shared/voice-reference/reference-15-35s.wav';q.REFERENCE_TEXT_PATH=ROOT/'shared/voice-reference/reference-15-35s.ko.txt'
 q.MAX_NEW_TOKENS=1536;q.MAX_RENDER_ATTEMPTS=args.attempts;q.INFERENCE_DEVICE='cuda:0'
 rows=[s for e in read(HERE/'plan.json')['episodes'] for s in e['inserts']]
 items=[q.RenderItem(s['key'],' '.join(s['ko']),q.CHUNK_DIR/(s['key']+'.wav')) for s in rows]
 previous={x['key']:x for x in read(HERE/'voice.json')['items']} if (HERE/'voice.json').exists() else {}
 history=HERE/'local/voice/history';history.mkdir(exist_ok=True)
 for item in items:
  changed=previous.get(item.key,{}).get('sourceText',item.text)!=item.text
  if item.path.exists() and (changed or item.key in args.force or q.needs_render(item.path)):
   target=history/(item.key+'-'+sha(item.path)[:16]+'.wav');assert target.resolve().is_relative_to(HERE.resolve()) and item.path.resolve().is_relative_to(HERE.resolve())
   if not target.exists():item.path.rename(target)
   else:item.path.unlink()
 q.render_chunks(items,1)
 import numpy as np,soundfile as sf
 quality=[]
 for s,item in zip(rows,items):
  x,sr=sf.read(item.path,dtype='float32');assert x.ndim==1
  # Retain the natural ending. Remove only excess leading/trailing digital silence.
  n=max(1,int(sr*.02));rms=np.sqrt(np.array([np.mean(x[i:i+n]**2) for i in range(0,len(x),n)]));active=np.flatnonzero(rms>max(.0005,float(rms.max())*.025));assert len(active)
  a=max(0,int(active[0]*n-.10*sr));z=min(len(x),int((active[-1]+1)*n+.22*sr));x=x[a:z]
  rms=np.sqrt(np.array([np.mean(x[i:i+n]**2) for i in range(0,len(x),n)]));speech=rms[rms>rms.max()*.0562];median=20*np.log10(np.median(speech)+1e-12);gain=min(10,max(-10,-22-float(median)));x*=10**(gain/20)
  x=np.pad(x,(round(.12*sr),round(.18*sr)))
  out=HERE/'local/voice'/(s['key']+'.wav');stage=out.with_suffix('.float.wav');sf.write(stage,x,sr,subtype='FLOAT')
  subprocess.run([str(FF),'-v','error','-nostdin','-y','-i',str(stage),'-af',f'aresample=192000,alimiter=limit=0.78:level=false:latency=true,aresample={sr}','-c:a','pcm_s16le',str(out)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  x,sr=sf.read(out,dtype='float32');peak=float(abs(x).max());assert peak<.85
  assert stage.resolve().is_relative_to(HERE.resolve());stage.unlink()
  raw=sf.read(item.path)[0];tail=float(q._tail_ratio(raw,sr));decay=float(q._tail_decay_ms(raw,sr));passed=q._passes_quality(tail,decay)
  quality.append(dict(key=s['key'],file=str(out),sha256=sha(out),seconds=len(x)/sr,sampleRate=sr,sourceText=' '.join(s['ko']),gainDb=gain,peakDbfs=float(20*np.log10(peak+1e-12)),rawTailRatio=tail,rawTailDecayMs=decay if math.isfinite(decay) else None,qualityPassed=bool(passed),originalLectureVoiceUntouched=True,humanListening=False))
 save(HERE/'voice.json',dict(status='generated-awaiting-ASR-and-boundary-QA',model=str(q.MODEL_DIR),referenceSha256=sha(q.REFERENCE),referenceTextSha256=sha(q.REFERENCE_TEXT_PATH),gpuPeakMiB=q.torch.cuda.max_memory_allocated()/2**20,items=quality,paidApi=False))
 release();bad=[x['key'] for x in quality if not x['qualityPassed']]
 if bad:raise RuntimeError('Ending checks still require repair: '+','.join(bad))
 print('New bridges rendered; all original lecture PCM retained.',flush=True)
if __name__=='__main__':main()
