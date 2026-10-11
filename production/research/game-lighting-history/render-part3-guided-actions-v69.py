"""Synthesize only the new37 paired paragraphs through an exclusive GPU handoff."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
REQUEST=BASE/'part3-guided-actions-tts-request-v69.json'
EXECUTION=BASE/'part3-guided-actions-tts-execution-v69.json'
request=json.loads(REQUEST.read_text('utf-8'));dry='--dry-run' in sys.argv
sys.path.insert(0,str(ROOT/'qwen3-tts'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def verify():
 if len(request['scenes'])!=37:raise RuntimeError('Only the prepared37 additions are authorized by this batch')
 for x in request['protectedInputs']:
  if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed: '+x['path'])
 for scene in request['scenes']:
  if (ROOT/scene['path']).exists():raise RuntimeError('Preserve already generated take '+scene['id'])
 if EXECUTION.exists():raise RuntimeError('Preserve existing execution; inspect observed failure before scoped repair')
def duplicate():
 result=subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
 print(result.stdout,end='',flush=True)
 if result.returncode:print(result.stderr,file=sys.stderr);raise SystemExit(result.returncode)
verify();duplicate()
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold('game-lighting-history-04','cuda:0',dry)
schedule_gpu_handoff('game-lighting-history-04','cuda:0',dry)
verify();duplicate()
import render_narration
if not dry:
 import psutil,torch,io,soundfile as sf
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2)
 loader=Qwen3TTSModel.from_pretrained.__func__
 def load(cls,*args,**kwargs):kwargs.setdefault('attn_implementation','sdpa');return loader(cls,*args,**kwargs)
 Qwen3TTSModel.from_pretrained=classmethod(load)
 ratio=render_narration._tail_ratio;decay=render_narration._tail_decay_ms
 def pcm16(data,sr):
  stream=io.BytesIO();sf.write(stream,data,sr,format='WAV',subtype='PCM_16');stream.seek(0);return sf.read(stream,dtype='float32')[0]
 render_narration._tail_ratio=lambda data,sr:ratio(pcm16(data,sr),sr)
 render_narration._tail_decay_ms=lambda data,sr:decay(pcm16(data,sr),sr)
 badness=render_narration._badness
 def passing(tail,decayms):return badness(tail,decayms) if render_narration._passes_quality(tail,decayms) else 1000000+badness(tail,decayms)
 render_narration._badness=passing
 me=psutil.Process();lease=json.loads((ROOT/'shared/output/GPU_HANDOFF.json').read_text('utf-8-sig'))
 state=dict(schemaVersion=1,startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),exe=me.exe()),status='new-guided-paragraphs-synthesizing',requestSha256=sha(REQUEST),leaseToken=lease['token'],cpuThreads=2,gpuJobs=1,results=[],generationComplete=False,original111AndFiveFramingPreserved=False,wholeAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,allFinalPixelsReviewed=False,uploaded=False)
 def save():
  tmp=EXECUTION.with_name(EXECUTION.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,EXECUTION)
  cp=ROOT/'production/research/game-lighting-history/checkpoint.json';c=json.loads(cp.read_text('utf-8-sig'))
  c['episode04GuidedTtsV69']=dict(execution=EXECUTION.relative_to(ROOT).as_posix(),status=state['status'],worker=state['actualIdentity'],leaseToken=state['leaseToken'],cpuThreads=2,gpuJobs=state['gpuJobs'],generationComplete=state['generationComplete'],wholeAsrApproved=False,finalMixedAsrApproved=False,next='Observe actual research restoration, then whole/independent ASR and measured current cut allocation')
  c['updatedAt']=stamp();tmp=cp.with_suffix('.tts69.tmp');tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
 save()
sys.argv=[sys.argv[0],'--project','game-lighting-history-04','--manifest',request['manifestOverride'],'--device','cuda:0','--batch-size','1']+(['--dry-run'] if dry else [])
try:
 render_narration.main()
 if not dry:
  for scene in request['scenes']:
   file=ROOT/scene['path'];data,sr=sf.read(file,dtype='float32');t=render_narration._tail_ratio(data,sr);d=render_narration._tail_decay_ms(data,sr)
   state['results'].append(dict(id=scene['id'],path=scene['path'],sha256=sha(file),samples=len(data),sampleRate=sr,seconds=len(data)/sr,tailRatio=t,tailDecayMs=d,technicalTailGatePassed=render_narration._passes_quality(t,d),asrDirectlyReviewed=False))
  for x in request['protectedInputs']:
   if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed during batch: '+x['path'])
  failed=[r['id'] for r in state['results'] if not r['technicalTailGatePassed']]
  if failed:raise RuntimeError('Preserve takes; observed tail failure requires scoped inspection: '+','.join(failed))
  state.update(status='new-guided-takes-generated-awaiting-ASR-and-research-restoration',generationComplete=True,original111AndFiveFramingPreserved=True,exitCode=0,endedAt=stamp(),gpuJobs=0);save()
except BaseException as exc:
 if not dry:state.update(status='failed-preserving-original-and-new-takes',error=repr(exc),exitCode=1,endedAt=stamp(),gpuJobs=0);save()
 raise
