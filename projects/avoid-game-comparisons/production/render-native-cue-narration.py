"""Render only new15 with the approved model/reference; preserve current14 PCM."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,traceback
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
QUEUE=PROOF.parent/'queue.json'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
STATE=BASE/'native-cue-narration-tts-execution.json';REQUEST=BASE/'native-cue-narration-request.json';LOG=BASE/'native-cue-narration-tts.log'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
request=read(REQUEST)
assert request['pairedWholeTextReview'] and request['overviewPromiseReview'] and request['allPriorScenePcmPreserved'] and request['device']=='cpu'
assert not STATE.exists(),'Inspect an existing execution instead of repeating it.'
subprocess.run([NODE,'scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check'],cwd=ROOT,check=True)
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
for x in request['scenes']:assert not (ROOT/x['path']).exists(),x['path']
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='loading-approved-Qwen-on-CPU',device='cpu',cpuThreads=8,cpuJobs=1,gpuJobs=0,renderJobs=0,uploads=0,request=REQUEST.relative_to(ROOT).as_posix(),requestSha256=sha(REQUEST),log=LOG.relative_to(ROOT).as_posix(),originalPCMChanged=False,results=[],generationComplete=False,wholeNewAsrDirectReview=False,finalNarrationApproved=False,humanWholeListening='pending',humanPronunciation='pending')
def checkpoint():
    launch=BASE/'native-cue-narration-tts-session.json'
    if launch.exists():
        d=read(launch)
        if d.get('pid')==os.getpid():state['sessionId']=d.get('sessionId')
    state['updatedAt']=now();save(STATE,state)
    queue=read(QUEUE);task=next(x for x in queue['items'] if x['slug']=='avoid-game-comparisons')
    task.update(stage='native-cue15-approved-voice-CPU-measurement',updatedAt=now())
    execution=dict(task.get('execution',{}));execution.update(observedAt=now(),phase='one-new-scene-CPU-TTS',status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive=state['cpuJobs']>0,gpuSynthesisJobs=0,cpuProductionJobs=state['cpuJobs'],primaryCpuProductionJobs=state['cpuJobs'],renderJobs=0,uploads=0,state=STATE.relative_to(ROOT).as_posix(),log=state['log'],activeTasks=[] if not state['cpuJobs'] else [{'kind':'one-new-scene-CPU-Qwen-narration','pid':os.getpid(),'sessionId':state['sessionId']}]);task['execution']=execution
    task.update(nativeCueNarration={'state':STATE.relative_to(ROOT).as_posix(),'newSceneIds':['15'],'generationComplete':state['generationComplete'],'wholeNewAsrDirectReview':False,'originalAll14PcmPreserved':True,'scriptScenes':15,'paragraphs':60},nextAction='Read full current-hash ASR of new15 and any ambiguous independent contexts; preserve current14 approved PCM. Final native-cue framing/body60:40, mix, subtitles, render, QA, collection and private save remain pending.')
    queue.update(updatedAt=now(),lastProgressAt=now());save(QUEUE,queue)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for key in ['stage','updatedAt','execution','nativeCueNarration','nextAction']:d[key]=task[key]
        save(p,d)
checkpoint();original_stdout=sys.stdout;original_stderr=sys.stderr
class Tee:
    def __init__(self,f):self.f=f
    def write(self,s):original_stdout.write(s);original_stdout.flush();self.f.write(s);self.f.flush();return len(s)
    def flush(self):original_stdout.flush();self.f.flush()
with LOG.open('a',encoding='utf-8') as log:
    sys.stdout=Tee(log);sys.stderr=sys.stdout
    try:
        sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as rn
        rn.configure_project('avoid-game-comparisons');rn.INFERENCE_DEVICE='cpu';rn.load_tts_dependencies()
        items=[]
        for entry in request['scenes']:
            p=ROOT/entry['path'];p.parent.mkdir(parents=True,exist_ok=True);items.append(rn.RenderItem(entry['id'],entry['text'],p))
        state['status']='synthesizing-one-new-CPU-scenes';checkpoint();rn.render_chunks(items,batch_size=1)
        for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
        for item in items:
            audio,rate=rn._read_mono(item.path)
            state['results'].append(dict(id=item.key,path=item.path.relative_to(ROOT).as_posix(),sha256=sha(item.path),samples=len(audio),sampleRate=rate,seconds=len(audio)/rate,text=item.text,tailRatio=rn._tail_ratio(audio,rate),tailDecayMs=rn._tail_decay_ms(audio,rate),heuristicIsApproval=False,wholeAsrDirectReview=False))
        state.update(status='one-new-scenes-measured-awaiting-full-ASR-direct-review',cpuJobs=0,endedAt=now(),exitCode=0,generationComplete=True,allProtectedInputsUnchanged=True)
        checkpoint();print(json.dumps({'status':state['status'],'results':[{k:v for k,v in x.items() if k in ['id','seconds','sha256']} for x in state['results']]}),flush=True)
    except BaseException:
        state.update(status='failed',cpuJobs=0,endedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally:sys.stdout=original_stdout;sys.stderr=original_stderr
