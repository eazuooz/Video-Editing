"""Measure only eight new guides with approved Qwen/reference, CPU two threads."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,traceback
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-making-game-sequels'
REQUEST=BASE/'guided-observation-tts-request-v3.json';STATE=BASE/'guided-observation-tts-execution-v3.json'
LOG=BASE/'guided-observation-tts-v3.log'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
assert not STATE.exists(),'Inspect existing execution; do not repeat synthesis.'
request=read(REQUEST)
assert request['pairedWholeTextReview'] and request['overviewPromiseReview'] and request['allPriorScenePcmPreserved']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','making-game-sequels','--check'],cwd=ROOT,check=True)
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
for g in request['guides']:assert not (ROOT/g['path']).exists(),g['path']
state=dict(schemaVersion=1,pid=os.getpid(),sessionId=None,startedAt=now(),status='loading-approved-Qwen-CPU-two-threads',device='cpu',cpuThreads=2,cpuJobs=1,gpuJobs=0,results=[],generationComplete=False,request=REQUEST.relative_to(ROOT).as_posix(),requestSha256=sha(REQUEST),log=LOG.relative_to(ROOT).as_posix(),allCurrent13PcmPreserved=True,baselinePcmSeconds=509.624,newGuidesTechnicalAsrApproved=False,finalTimingApproved=False,humanWholeListening='pending',humanPronunciation='pending',newGitImages=0)
def checkpoint():
    session=BASE/'guided-observation-tts-session-v3.json'
    if session.exists():
        s=read(session)
        if s.get('pid')==os.getpid():state['sessionId']=s['sessionId']
    state['updatedAt']=now();save(STATE,state)
    q=read(PROOF.parent/'queue.json');item=next(x for x in q['items'] if x['slug']=='making-game-sequels')
    item.update(stage='current13-independent-guidance-CPU-measurement',updatedAt=now())
    ex=dict(item.get('execution',{}));ex.update(observedAt=now(),phase=item['stage'],status=state['status'],pid=os.getpid(),sessionId=state['sessionId'],alive=bool(state['cpuJobs']),commandLine='render-guided-observation-v3.py --CPU2',cpuProductionJobs=state['cpuJobs'],primaryCpuProductionJobs=state['cpuJobs'],gpuSynthesisJobs=0,renderJobs=0,uploads=0,state=STATE.relative_to(ROOT).as_posix(),log=state['log'],activeTasks=[] if not state['cpuJobs'] else [{'kind':'only-new-observation-guides-CPU-Qwen','pid':os.getpid(),'sessionId':state['sessionId']}])
    item.update(execution=ex,guidedObservation={'state':STATE.relative_to(ROOT).as_posix(),'guides':8,'completedGuides':len(state['results']),'measured':state['generationComplete'],'technicalAsrApproved':False},nextAction='Read actual new-guide measurements, then whole new-guide ASR and ambiguous contexts; preserve current509.624sPCM. Final word/cut/caption/timing/mix and private delivery remain pending.')
    q.update(updatedAt=now(),lastProgressAt=now());save(PROOF.parent/'queue.json',q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','execution','guidedObservation','nextAction']:d[k]=item[k]
        save(p,d)
checkpoint();original=sys.stdout
class Tee:
    def __init__(self,f):self.f=f
    def write(self,s):original.write(s);original.flush();self.f.write(s);self.f.flush();return len(s)
    def flush(self):original.flush();self.f.flush()
with LOG.open('a',encoding='utf-8') as log:
    sys.stdout=Tee(log);sys.stderr=sys.stdout
    try:
        sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as rn
        rn.configure_project('making-game-sequels');rn.INFERENCE_DEVICE='cpu';rn.load_tts_dependencies()
        rn.torch.set_num_threads(2)
        model=rn.Qwen3TTSModel.from_pretrained(str(rn.MODEL_DIR),device_map='cpu',dtype=rn.torch.float32,attn_implementation='eager')
        prompt=model.create_voice_clone_prompt(ref_audio=str(rn.REFERENCE),ref_text=rn.REFERENCE_TEXT_PATH.read_text('utf-8').strip(),x_vector_only_mode=False)
        for g in request['guides']:
            state['status']='synthesizing-'+g['id'];checkpoint();print('New guide '+g['id'],flush=True)
            wavs,rate=model.generate_voice_clone(text=[g['ko']],language=rn.LANGUAGE,voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=rn.MAX_NEW_TOKENS)
            assert len(wavs)==1
            p=ROOT/g['path'];p.parent.mkdir(parents=True,exist_ok=True);rn.sf.write(p,wavs[0],rate,subtype='PCM_16')
            pcm,sr=rn.sf.read(p,dtype='float32')
            result=dict(id=g['id'],parentScene=g['parentScene'],afterOriginalParagraph=g['afterOriginalParagraph'],path=g['path'],sha256=sha(p),samples=len(pcm),sampleRate=sr,seconds=len(pcm)/sr,text=g['ko'],en=g['en'],tailRatio=rn._tail_ratio(pcm,sr),tailDecayMs=rn._tail_decay_ms(pcm,sr),heuristicIsApproval=False,wholeAsrDirectReview=False,humanListening='pending')
            state['results'].append(result);checkpoint();print(json.dumps({k:result[k] for k in ['id','seconds','sha256']}),flush=True)
        for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
        state.update(status='new-guides-measured-awaiting-full-new-ASR',cpuJobs=0,generationComplete=True,allProtectedInputsUnchanged=True,endedAt=now(),exitCode=0);checkpoint()
    except BaseException:
        state.update(status='failed',cpuJobs=0,endedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally:sys.stdout=original;sys.stderr=original
