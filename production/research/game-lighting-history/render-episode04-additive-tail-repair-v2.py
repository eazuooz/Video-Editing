"""Cooperative exclusive TTS of observed failed additions, preserving all24."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-04/production'
REQUEST=(ROOT/sys.argv[sys.argv.index('--request')+1]).resolve() if '--request' in sys.argv else BASE/'additive-tail-repair-request-v2.json'
REQUEST.relative_to(BASE)
EXECUTION=BASE/'additive-tail-repair-execution-v2.json'
request=json.loads(REQUEST.read_text('utf-8'));dry='--dry-run' in sys.argv
sys.path.insert(0,str(ROOT/'qwen3-tts'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 if not request['scenes'] or len(request['scenes'])>=24:raise RuntimeError('Scoped observed failed takes only')
 for x in [request['sourceRequest'],request['sourceExecution'],*request['protectedInputs'],*request['original24TakeFiles']]:
  if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Protected input changed: '+x['path'])
 for s in request['scenes']:
  if (ROOT/s['path']).exists():raise RuntimeError('Preserve completed retake '+s['id'])
def duplicate():
 r=subprocess.run(['node','scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
 print(r.stdout,end='',flush=True)
 if r.returncode:print(r.stderr,file=sys.stderr);raise SystemExit(r.returncode)
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
 def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return loader(cls,*a,**kw)
 Qwen3TTSModel.from_pretrained=classmethod(load)
 # Gate the exact PCM16 representation written to each WAV, not just the
 # unquantized inference buffer. The threshold itself is unchanged.
 ratio=render_narration._tail_ratio;decay=render_narration._tail_decay_ms
 def pcm16(a,sr):
  f=io.BytesIO();sf.write(f,a,sr,format='WAV',subtype='PCM_16');f.seek(0);return sf.read(f,dtype='float32')[0]
 render_narration._tail_ratio=lambda a,sr:ratio(pcm16(a,sr),sr)
 render_narration._tail_decay_ms=lambda a,sr:decay(pcm16(a,sr),sr)
 badness=render_narration._badness
 def passing(t,d):return badness(t,d) if render_narration._passes_quality(t,d) else 1000000+badness(t,d)
 render_narration._badness=passing
 me=psutil.Process();lease=json.loads((ROOT/'shared/output/GPU_HANDOFF.json').read_text('utf-8-sig'))
 state=dict(schemaVersion=1,startedAt=time.time(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd(),exe=me.exe()),status='scoped-failed-addition-takes-synthesizing',requestSha256=sha(REQUEST),leaseToken=lease['token'],cpuThreads=2,gpuJobs=1,results=[],generationComplete=False,original24Preserved=False,wholeAsrApproved=False,independentContextAsrApproved=False,finalMixedAsrApproved=False)
 def save():
  p=EXECUTION.with_name(EXECUTION.name+'.writing-'+str(os.getpid()));p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(p,EXECUTION)
 if EXECUTION.exists():raise RuntimeError('Preserve existing retake execution')
 save()
sys.argv=[sys.argv[0],'--project','game-lighting-history-04','--manifest',request['manifestOverride'],'--device','cuda:0','--batch-size','1']+(['--dry-run'] if dry else [])
try:
 render_narration.main()
 if not dry:
  import soundfile as sf
  for s in request['scenes']:
   p=ROOT/s['path'];data,sr=sf.read(p,dtype='float32');t=render_narration._tail_ratio(data,sr);d=render_narration._tail_decay_ms(data,sr)
   state['results'].append(dict(id=s['id'],path=s['path'],sha256=sha(p),samples=len(data),sampleRate=sr,seconds=len(data)/sr,tailRatio=t,tailDecayMs=d,technicalTailGatePassed=render_narration._passes_quality(t,d),asrDirectlyReviewed=False))
  for x in request['original24TakeFiles']:
   if sha(ROOT/x['path'])!=x['sha256']:raise RuntimeError('Original take changed')
  bad=[r['id'] for r in state['results'] if not r['technicalTailGatePassed']]
  if bad:raise RuntimeError('Preserve scoped retakes for ending review: '+','.join(bad))
  state.update(status='scoped-additive-retakes-generated-awaiting-ASR-and-research-restoration',generationComplete=True,original24Preserved=True,exitCode=0,endedAt=time.time(),gpuJobs=0);save()
except BaseException as e:
 if not dry:state.update(status='failed-preserving-all-original-and-scoped-takes',error=repr(e),exitCode=1,endedAt=time.time(),gpuJobs=0);save()
 raise
