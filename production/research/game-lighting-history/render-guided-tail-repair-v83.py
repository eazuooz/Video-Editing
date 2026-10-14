"""Exclusive cooperative TTS for the observed failed subset of new37 takes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
REQUEST=BASE/'guided-tail-repair-request-v83.json';EXECUTION=BASE/'guided-tail-repair-execution-v83.json'
request=json.loads(REQUEST.read_text('utf-8'));dry='--dry-run' in sys.argv
sys.path.insert(0,str(ROOT/'qwen3-tts'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def verify():
 if not 0<len(request['scenes'])<37:raise RuntimeError('Only observed failed subset of37')
 if {x['id'] for x in request['scenes']}!={x['id'] for x in request['observedFailures']}:raise RuntimeError('Observed failure scope changed')
 for x in [request['sourceRequest'],request['sourceExecution'],request['sourceResearchRestoration'],*request['protectedInputs'],*request['original37TakeFiles']]:
  if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed '+x['path'])
 if EXECUTION.exists():raise RuntimeError('Preserve existing scoped execution')
 for s in request['scenes']:
  if (ROOT/s['path']).exists():raise RuntimeError('Preserve generated retake '+s['id'])
def duplicate():
 result=subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
 print(result.stdout,end='',flush=True)
 if result.returncode:print(result.stderr,file=sys.stderr);raise SystemExit(result.returncode)
verify();duplicate()
from gpu_tts_hold import check_gpu_tts_hold
from gpu_handoff_guard import schedule_gpu_handoff
check_gpu_tts_hold('game-lighting-history-04','cuda:0',dry);schedule_gpu_handoff('game-lighting-history-04','cuda:0',dry)
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
 def passing(t,d):return badness(t,d) if render_narration._passes_quality(t,d) else 1000000+badness(t,d)
 render_narration._badness=passing
 me=psutil.Process();lease=json.loads((ROOT/'shared/output/GPU_HANDOFF.json').read_text('utf-8-sig'))
 state=dict(schemaVersion=1,startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),exe=me.exe()),requestSha256=sha(REQUEST),leaseToken=lease['token'],status='scoped-observed-guided-tail-repair-running',cpuThreads=2,gpuJobs=1,results=[],generationComplete=False,original37Preserved=False,wholeAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False,uploaded=False)
 def save():
  tmp=EXECUTION.with_name(EXECUTION.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,EXECUTION)
 save()
sys.argv=[sys.argv[0],'--project','game-lighting-history-04','--manifest',request['manifestOverride'],'--device','cuda:0','--batch-size','1']+(['--dry-run'] if dry else [])
try:
 render_narration.main()
 if not dry:
  for s in request['scenes']:
   p=ROOT/s['path'];data,sr=sf.read(p,dtype='float32');t=render_narration._tail_ratio(data,sr);d=render_narration._tail_decay_ms(data,sr)
   state['results'].append(dict(id=s['id'],path=s['path'],sha256=sha(p),samples=len(data),sampleRate=sr,seconds=len(data)/sr,tailRatio=t,tailDecayMs=d,technicalTailGatePassed=render_narration._passes_quality(t,d),asrDirectlyReviewed=False))
  for x in request['original37TakeFiles']:
   if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Original take changed '+x['path'])
  failed=[x['id'] for x in state['results'] if not x['technicalTailGatePassed']]
  if failed:raise RuntimeError('Preserve scoped failed retakes; no threshold waiver: '+','.join(failed))
  state.update(status='scoped-guided-retakes-generated-awaiting-ASR-and-research-restoration',generationComplete=True,original37Preserved=True,exitCode=0,endedAt=stamp(),gpuJobs=0);save()
except BaseException as exc:
 if not dry:state.update(status='failed-preserve-original-and-scoped-takes',error=repr(exc),exitCode=1,endedAt=stamp(),gpuJobs=0);save()
 raise
