"""Render only two reviewed clarity candidates; leave every original PCM intact."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, sys, traceback

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
PROOF = ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
QUEUE = ROOT/'production/batches/sakurai-planning-game-design/queue.json'
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
STATE = BASE/'targeted-clarity-execution.json'
REQUEST = BASE/'targeted-clarity-request.json'
LOG = BASE/'targeted-clarity.log'

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):
    temp=p.with_name(p.name+f'.{os.getpid()}.writing')
    temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(p)

request=read(REQUEST)
assert request['directBilingualTextReview'] and request['voiceAndModelUnchanged']
subprocess.run([NODE,'scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check'],cwd=ROOT,check=True)
for item in request['protectedInputs']: assert sha(ROOT/item['path'])==item['sha256'],item['path']
assert not STATE.exists(), 'Inspect an existing run instead of overwriting or repeating it.'
for item in request['repairs']: assert not (ROOT/item['candidatePath']).exists()
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='loading-approved-Qwen-on-CPU',device='cpu',cpuThreads=8,cpuJobs=1,gpuJobs=0,renderJobs=0,uploads=0,request=REQUEST.relative_to(ROOT).as_posix(),requestSha256=sha(REQUEST),log=LOG.relative_to(ROOT).as_posix(),originalPCMChanged=False,results=[],candidateGenerationCompleted=False,candidatesApproved=False,finalNarrationApproved=False,fullAsrReview=False,humanWholeListening='pending',humanPronunciation='pending')

def checkpoint():
    launch=BASE/'targeted-clarity-session.json'
    if launch.exists():
        d=read(launch)
        if d.get('pid')==os.getpid():state['sessionId']=d.get('sessionId')
    state['updatedAt']=now();save(STATE,state)
    queue=read(QUEUE);task=next(x for x in queue['items'] if x['slug']=='avoid-game-comparisons')
    task['stage']='CPU-targeted-clarity-and-unique-source-expansion'
    execution=dict(task.get('execution',{}))
    execution.update(observedAt=now(),phase='targeted06-10-approved-voice-CPU-TTS',status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive=state['cpuJobs']>0,gpuSynthesisJobs=0,primaryCpuProductionJobs=state['cpuJobs'],cpuProductionJobs=state['cpuJobs']+len([x for x in execution.get('secondaryTasks',[]) if x.get('kind')=='full-decode']),renderJobs=0,uploads=0,state=STATE.relative_to(ROOT).as_posix(),log=state['log'],activeTasks=[] if state['cpuJobs']==0 else [{'kind':'two-paragraph-CPU-Qwen-clarity-candidates','pid':os.getpid(),'sessionId':state['sessionId']}])
    task.update(execution=execution,updatedAt=now(),targetedClarity={'state':STATE.relative_to(ROOT).as_posix(),'status':state['status'],'candidateGenerationCompleted':state['candidateGenerationCompleted'],'candidatesApproved':False,'originalPCMChanged':False},nextAction='Independently ASR/direct-review two candidate paragraphs before adoption; preserve all original PCM. Continue unique native source comparison and acquire related actions as needed; full timing/mix/captioned render/private upload remain pending.')
    queue.update(updatedAt=now(),lastProgressAt=now());save(QUEUE,queue)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','execution','updatedAt','targetedClarity','nextAction']:d[k]=task[k]
        save(p,d)

checkpoint()
original_stdout=sys.stdout; original_stderr=sys.stderr
class Tee:
    def __init__(self,f):self.f=f
    def write(self,s): original_stdout.write(s);original_stdout.flush();self.f.write(s);self.f.flush();return len(s)
    def flush(self):original_stdout.flush();self.f.flush()
with LOG.open('a',encoding='utf-8') as log:
    sys.stdout=Tee(log);sys.stderr=sys.stdout
    try:
        sys.path.insert(0,str(ROOT/'qwen3-tts'))
        import render_narration as rn
        rn.configure_project('avoid-game-comparisons');rn.INFERENCE_DEVICE='cpu';rn.load_tts_dependencies()
        items=[]
        for entry in request['repairs']:
            path=ROOT/entry['candidatePath'];path.parent.mkdir(parents=True,exist_ok=True)
            items.append(rn.RenderItem(entry['id'],entry['replacementKo'],path))
        state['status']='synthesizing-two-CPU-clarity-candidates';checkpoint()
        rn.render_chunks(items,batch_size=1)
        for item in request['protectedInputs']:assert sha(ROOT/item['path'])==item['sha256'],item['path']
        for item in items:
            audio,rate=rn._read_mono(item.path)
            state['results'].append(dict(id=item.key,path=item.path.relative_to(ROOT).as_posix(),sha256=sha(item.path),samples=len(audio),sampleRate=rate,seconds=len(audio)/rate,text=item.text,tailRatio=rn._tail_ratio(audio,rate),tailDecayMs=rn._tail_decay_ms(audio,rate),heuristicIsApproval=False,independentAsrReviewed=False))
        state.update(status='candidates-rendered-awaiting-independent-ASR-direct-review',cpuJobs=0,endedAt=now(),exitCode=0,candidateGenerationCompleted=True,allProtectedInputsUnchanged=True)
        checkpoint();print(json.dumps({'status':state['status'],'results':[{k:v for k,v in x.items() if k in ['id','seconds','sha256']} for x in state['results']]}),flush=True)
    except BaseException:
        state.update(status='failed',cpuJobs=0,endedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally:sys.stdout=original_stdout;sys.stderr=original_stderr
