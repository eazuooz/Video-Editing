"""Single CPU2 worker measures only8new independent guides, never the original11."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time,traceback
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
REQUEST=BASE/'observation-guide-tts-request-v1.json';STATE=BASE/'observation-guide-tts-execution-v1.json';LOG=BASE/'observation-guide-tts-v1.log'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,d):
    t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for n in range(40):
        try:os.replace(t,p);return
        except OSError:
            if n==39:raise
            time.sleep(.15)
parser=argparse.ArgumentParser();parser.add_argument('--resource',required=True);args=parser.parse_args()
assert not STATE.exists(), 'Inspect existing worker/state; never repeat synthesis'
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<=85
request=read(REQUEST)
assert request['pairedWholeTextReview'] and request['overviewPromiseReview'] and request['allPriorScenePcmPreserved']
assert sha(ROOT/request['textReview'])==request['textReviewSha256'] and len(request['guides'])==8
for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
for g in request['guides']:assert not (ROOT/g['path']).exists(),g['path']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','familiar-game-rules','--check'],cwd=ROOT,check=True)
state=dict(schemaVersion=1,slug='familiar-game-rules',pid=os.getpid(),sessionId=None,commandLine=[sys.executable,*sys.argv],startedAt=now(),
 status='loading-approved-Qwen-CPU-two-threads',device='cpu',cpuThreads=2,cpuJobs=1,gpuJobs=0,results=[],total=8,generationComplete=False,
 request=rel(REQUEST),requestSha256=sha(REQUEST),log=rel(LOG),resourceObservation=resource,allOriginal11PcmPreserved=True,
 baselinePcmSeconds=296.72,originalExplanationSeconds=147.2,newGuidesTechnicalAsrApproved=False,finalTimingApproved=False,
 humanWholeListening='pending',humanPronunciation='pending',newGitImages=0,exitCode=None)
def checkpoint():
    sp=BASE/'observation-guide-tts-session-v1.json'
    if sp.exists():
        session=read(sp)
        if session['pid']==os.getpid():state['sessionId']=session['sessionId']
    state['updatedAt']=now();save(STATE,state)
    qp=PROOF.parent/'queue.json';q=read(qp);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
    if item.get('execution',{}).get('pid')!=os.getpid():item.setdefault('executionHistory',[]).append(item.get('execution',{}))
    running=state['exitCode'] is None
    item.update(stage='original11-preserved-only8new-guides-CPU-Qwen-measurement',updatedAt=state['updatedAt'],
       execution=dict(pid=os.getpid(),commandLine=state['commandLine'],sessionId=state['sessionId'],alive=running,state=rel(STATE),log=rel(LOG),
       status=state['status'],cpuThreads=2,gpuJobs=0,completed=len(state['results']),total=8,activeTasks=['only8new-guides-CPU-Qwen'] if running else []),
       observationGuides=dict(request=rel(REQUEST),guides=8,completed=len(state['results']),measured=state['generationComplete'],technicalAsrApproved=False,pairedWholeTextReview=True),
       nextAction='Read actual currentguide measurements after worker exit; whole8newguide ASR and independent contexts, then preservation/joins and measured native/cue60:40. Original11PCM296.72s/white147.2s retained; source mask conflicts/finalpixels/render/mix/private pending.')
    q.update(updatedAt=now(),lastProgressAt=now());save(qp,q)
    for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
        d=read(p)
        for k in ['stage','updatedAt','execution','observationGuides','nextAction']:d[k]=item[k]
        save(p,d)
original=sys.stdout
class Tee:
    def __init__(self,f):self.f=f
    def write(self,s):original.write(s);original.flush();self.f.write(s);self.f.flush();return len(s)
    def flush(self):original.flush();self.f.flush()
with LOG.open('x',encoding='utf-8') as log:
    sys.stdout=Tee(log);sys.stderr=sys.stdout
    try:
        checkpoint()
        sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as rn
        rn.configure_project('familiar-game-rules');rn.INFERENCE_DEVICE='cpu';rn.load_tts_dependencies()
        rn.torch.set_num_threads(2)
        model=rn.Qwen3TTSModel.from_pretrained(str(rn.MODEL_DIR),device_map='cpu',dtype=rn.torch.float32,attn_implementation='eager')
        prompt=model.create_voice_clone_prompt(ref_audio=str(rn.REFERENCE),ref_text=rn.REFERENCE_TEXT_PATH.read_text('utf-8').strip(),x_vector_only_mode=False)
        for g in request['guides']:
            state['status']='synthesizing-guide-'+g['id'];checkpoint();print('New independent guide '+g['id'],flush=True)
            wavs,rate=model.generate_voice_clone(text=[g['ko']],language=rn.LANGUAGE,voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=rn.MAX_NEW_TOKENS)
            assert len(wavs)==1
            p=ROOT/g['path'];p.parent.mkdir(parents=True,exist_ok=True);rn.sf.write(p,wavs[0],rate,subtype='PCM_16')
            pcm,sr=rn.sf.read(p,dtype='float32');assert sr==24000 and len(pcm)>0
            result=dict(id=g['id'],parentScene=g['parentScene'],afterOriginalParagraph=g['afterOriginalParagraph'],path=g['path'],sha256=sha(p),samples=len(pcm),sampleRate=sr,seconds=len(pcm)/sr,
                text=g['ko'],en=g['en'],tailRatio=rn._tail_ratio(pcm,sr),tailDecayMs=rn._tail_decay_ms(pcm,sr),heuristicIsApproval=False,wholeAsrDirectReview=False,humanListening='pending')
            state['results'].append(result);checkpoint();print(json.dumps({k:result[k] for k in ['id','seconds','sha256']}),flush=True)
        for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
        state.update(status='all8new-guides-measured-awaiting-whole-new-ASR',cpuJobs=0,generationComplete=True,allProtectedInputsUnchanged=True,
            totalNewGuideSeconds=sum(x['seconds'] for x in state['results']),endedAt=now(),exitCode=0);checkpoint()
    except BaseException:
        state.update(status='failed-newguide-measurement',cpuJobs=0,endedAt=now(),exitCode=1,error=traceback.format_exc());checkpoint();traceback.print_exc();raise
    finally:sys.stdout=original;sys.stderr=original
