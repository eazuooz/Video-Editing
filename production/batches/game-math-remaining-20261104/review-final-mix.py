"""One finite final-file speech and local-level review. No human-listening claim."""
from pathlib import Path
from datetime import datetime,timezone
from difflib import SequenceMatcher
import argparse,hashlib,importlib.util,json,os,subprocess,time,uuid
import psutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
MODEL=Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots/41f01f3fe87f28c78e2fbf8b568835947dd65ed9')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--queue',required=True);ap.add_argument('--wait-hours',type=float,default=12)
 ap.add_argument('--device',choices=('cuda','cpu'),default='cuda');a=ap.parse_args()
 q=Path(a.queue).resolve();queue=read(q);P=R/'projects'/queue['project'];assert q.is_relative_to(P/'production/local')
 G=module('guard',R/'projects/game-math-shading-lights/production/run-capture-queue.py')
 N=module('normalize',R/'projects/game-math-shading-lights/production/align-captions-and-cues.py')
 W=q.parent/'final-mix-review';W.mkdir(exist_ok=True);statefile=W/'worker.json';lease=R/'shared/output/GPU_HANDOFF.json'
 if statefile.exists():
  previous=read(statefile)
  try:assert abs(psutil.Process(previous['pid']).create_time()-previous['createTime'])>.1,'Existing final-mix review active'
  except psutil.NoSuchProcess:pass
  assert previous['status']!='evidence-ready-direct-content-review-pending','Preserve unchanged completed evidence'
 state=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting',startedAt=now(),device=a.device,humanListening=False,automation=False)
 owned=None;deadline=time.monotonic()+a.wait_hours*3600
 try:
  while owned is None:
   c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow'] and P.name in c['projectSlugs']
   reason='Waiting for final media technical report'
   if (q.parent/'final-qa/report.json').exists():reason=G.idle_reason() if a.device=='cuda' else None
   state.update(reason=reason,checkedAt=now());save(statefile,state)
   if reason is None:
    if a.device=='cpu':break
    candidate=str(uuid.uuid4())
    try:
     with lease.open('x',encoding='utf-8') as f:json.dump(dict(owner=P.name+'-final-mix-review',id=candidate,pid=os.getpid(),createdAt=now()),f)
    except FileExistsError:pass
    else:owned=candidate;break
   if time.monotonic()>deadline:raise RuntimeError('Bounded wait ended, other jobs preserved')
   time.sleep(15)
  state.update(status='checking-final-mix');save(statefile,state)
  report=read(q.parent/'final-qa/report.json');master=Path(report['files']['captioned']['path']);master_hash=sha(master);assert master_hash==report['files']['captioned']['sha256']
  audio_dir=Path(queue.get('audioDirectory',P/'production/local/audio-v1'));timing=read(audio_dir/'narration.timing.json')
  ff=Path(read(Path(queue['jobs'][0]))['ffmpeg']);pcm=W/'actual-final-body-mono.wav'
  if not pcm.exists():subprocess.run([str(ff),'-v','error','-nostdin','-n','-i',str(master),'-ss','2','-t',str(timing['duration_seconds']),'-vn','-ar','48000','-ac','1','-c:a','pcm_f32le',str(pcm)],check=True,creationflags=G.CREATE)
  os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
  import soundfile as sf,numpy as np
  from scipy.signal import resample_poly
  final,sr=sf.read(pcm,dtype='float32');reference,rr=sf.read(q.parent/'composite/narration-normalized.wav',dtype='float32');assert sr==rr==48000
  # ffmpeg's default stereo-to-mono decode uses sqrt(1/2) per channel.
  # Match that matrix rather than comparing it against an arithmetic mean,
  # which would manufacture a +3.0103 dB "gain anomaly" in every paragraph.
  if reference.ndim>1:
   assert reference.shape[1]==2
   reference=reference.sum(axis=1)*(2**-.5)
  # The compositor pads the body to a whole 60fps frame; this extraction uses
  # the unchanged measured PCM duration. At most one silent video-frame tail
  # is legitimate, never missing or trimmed speech.
  difference=len(reference)-len(final)
  assert 0<=difference<=sr/60+2,(len(final),len(reference),sr)
  tail_peak=float(np.max(np.abs(reference[len(final):]))) if difference else 0
  assert tail_peak<1e-6,'Non-silent narration omitted at the final body boundary'
  save(W/'frame-tail-check.json',dict(finalBodySamples=len(final),normalizedSamples=len(reference),silentFramePaddingSamples=difference,normalizedPaddingPeak=tail_peak,sampleRate=sr))
  import torch
  from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
  torch.set_num_threads(2);torch.set_num_interop_threads(1)
  dtype=torch.float32 if a.device=='cpu' else torch.float16
  if a.device=='cuda':
   free,total=torch.cuda.mem_get_info();assert free>=9*1024**3
   torch.cuda.set_per_process_memory_fraction(7*1024**3/total)
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(MODEL),dtype=dtype,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager').to(a.device).eval()
  processor=AutoProcessor.from_pretrained(str(MODEL));pipe=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=dtype,device=a.device)
  entries=[]
  for e in timing['entries']:
   target=W/'paragraphs'/f"{e['scene_id']}-{e['paragraph']:02}.json"
   if target.exists():
    d=read(target);assert d['masterSha256']==master_hash and d['entry']==e;entries.append(d);continue
   begin=round(e['start']*sr);end=round(e['end']*sr);x=final[begin:end];ref=reference[begin:end]
   with torch.inference_mode():result=pipe({'array':resample_poly(x,1,3).astype(np.float32),'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word',chunk_length_s=28,stride_length_s=4)
   expected=N.normalized(e['text']);observed=N.normalized(result['text']);match=SequenceMatcher(None,expected,observed,autojunk=False)
   windows=[]
   for start in range(0,max(0,min(len(x),len(ref))-4800),4800):
    r=ref[start:start+4800].astype(np.float64);y=x[start:start+4800].astype(np.float64);power=float(np.mean(r*r))
    if power<10**(-35/10):continue
    gain=float(np.sum(y*r)/(np.sum(r*r)+1e-12));residual=y-gain*r
    windows.append(dict(time=e['start']+start/sr,referenceDb=10*np.log10(power),projectedVoiceGainDb=20*np.log10(max(abs(gain),1e-9)),residualDb=10*np.log10(max(float(np.mean(residual*residual)),1e-12))))
   d=dict(masterSha256=master_hash,entry=e,text=result['text'],chunks=result.get('chunks',[]),similarity=match.ratio(),coverage=sum(n for _,_,n in match.get_matching_blocks())/max(1,len(expected)),recognizedExpansion=len(observed)/max(1,len(expected)),opcodes=match.get_opcodes(),localWindows=windows,humanListening=False)
   d['suspectLevelWindows']=[w for w in windows if abs(w['projectedVoiceGainDb'])>3]
   save(target,d);entries.append(d);state.update(completed=len(entries),total=len(timing['entries']),last=e['scene_id']);save(statefile,state)
   print(f"Final mix {len(entries)}/{len(timing['entries'])}: {e['scene_id']} {d['coverage']:.3f}",flush=True)
  save(W/'report.json',dict(masterSha256=master_hash,normalizedNarrationSha256=sha(q.parent/'composite/narration-normalized.wav'),extractedActualMixSha256=sha(pcm),status='measured-evidence-direct-review-pending',humanListening=False,paragraphs=[{k:v for k,v in d.items() if k not in ('chunks','localWindows','opcodes')} for d in entries],method='Each full actual encoded paragraph, no expected-text prompt; 100ms correlation against identical normalized narration to identify local gain anomalies. Game-audio residuals and ASR discrepancies require content review, not automatic failure or approval.'))
  state.update(status='evidence-ready-direct-content-review-pending',finishedAt=now());save(statefile,state)
 except BaseException as exc:state.update(status='failed-or-blocked',error=repr(exc),finishedAt=now());save(statefile,state);raise
 finally:G.release_lease(owned)
if __name__=='__main__':main()
