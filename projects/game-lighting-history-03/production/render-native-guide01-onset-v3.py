"""Repair only two unapproved guide candidates as13 complete sentence chunks.

Use the existing approved Qwen1.7B/reference and cooperative research handoff.
Preserve original84 PCM, other18 guide PCM and both failed guide takes.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time,traceback
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
REQUEST=BASE/'native-guide01-onset-tts-request-v3.json';STATE=BASE/'native-guide01-onset-tts-execution-v3.json'
NODE=Path('C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,x):
    tmp=p.with_name(p.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
    for i in range(30):
        try:os.replace(tmp,p);return
        except OSError:
            if i==29:raise
            time.sleep(.15)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
    request=read(REQUEST);review=read(ROOT/request['scriptReview'])
    assert request['expectedSentenceChunks']==1 and len(request['scenes'])==1
    assert review['fullKoEnDirectlyReviewed'] and review['approvedForMeasurementOnly'] and not review['audioApproved']
    def verify():
        for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
    verify()
    subprocess.run([str(NODE),'scripts/review-video-duplicates.cjs','game-lighting-history-03','--candidate-file','production/research/game-lighting-history/candidate-03.json','--check'],cwd=ROOT,check=True)
    for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
    os.environ.update(TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    sys.path.insert(0,str(ROOT/'qwen3-tts'))
    import render_narration as rn
    rn.configure_project('game-lighting-history-03',str(ROOT/request['manifestOverride']))
    jobs=rn.load_jobs();items=rn.build_render_items(jobs)
    assert len(items)==1 and rn.RENDER_MODE=='line'
    assert [x.text for x in items]==[line for s in request['scenes'] for line in s['lines']]
    if args.dry_run:
        print('Exact single opener plus five preserved sentences; original84, all20previous guide PCM and refs verified. Currentdistinct passed. Model0/GPU0.',flush=True);return
    assert not STATE.exists(),'Preserve existing repair execution'
    assert not rn.OUTPUT_DIR.exists(),'Preserve previous repair candidate PCM'
    from gpu_tts_hold import check_gpu_tts_hold
    from gpu_handoff_guard import schedule_gpu_handoff,check_gpu_handoff
    check_gpu_tts_hold('game-lighting-history-03','cuda:0',False)
    schedule_gpu_handoff('game-lighting-history-03','cuda:0',False)
    check_gpu_handoff('game-lighting-history-03','cuda:0',False)
    verify()
    import psutil
    me=psutil.Process();lease=read(ROOT/'shared/output/GPU_HANDOFF.json')
    state=dict(schemaVersion=1,startedAt=now(),actualPid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),requestSha256=sha(REQUEST),leaseToken=lease['token'],log=lease.get('ttsLog'),cpuThreads=2,gpuJobs=1,
        stage='loading-approved-Qwen-selective-repairs',results=[],joinedGuides=[],totalSentenceChunks=1,generationComplete=False,exitCode=None,original84Regenerated=False,other18GuidesRegenerated=False,
        wholeAsrApproved=False,finalMixedAsrApproved=False,heuristicIsApproval=False,humanListening='pending',humanPronunciation='pending')
    def checkpoint():
        state['updatedAt']=now();save(STATE,state)
        cpPath=ROOT/'production/research/game-lighting-history/checkpoint.json';cp=read(cpPath)
        cp.update(updatedAt=now(),stage=state['stage'],ownedJobsRunning=[] if state['exitCode'] is not None else [dict(pid=state['actualPid'],createTime=state['createTime'],commandLine=state['commandLine'],sessionId=cp.get('episode03GuideOnsetV3SessionId'),state=rel(STATE),log=state['log'],cpuThreads=2,gpuJobs=state['gpuJobs'],completed=len(state['results']),total=1)])
        cp['episode03GuideOnsetV3Execution']={k:state[k] for k in ['actualPid','createTime','commandLine','stage','leaseToken','log','generationComplete','exitCode']}
        cp['episode03GuideOnsetV3Execution'].update(state=rel(STATE),completed=len(state['results']),total=1)
        cp['next']='Observe single-opener TTS and exact research restoration. Compare replacement sentence and complete joined guide before updating final measured timing.'
        save(cpPath,cp)
    checkpoint()
    try:
        rn.INFERENCE_DEVICE='cuda:0';rn.load_tts_dependencies();rn.torch.set_num_threads(2);rn.torch.set_num_interop_threads(1)
        loader=rn.Qwen3TTSModel.from_pretrained.__func__
        def load(cls,*a,**kw):kw.setdefault('attn_implementation','sdpa');return loader(cls,*a,**kw)
        rn.Qwen3TTSModel.from_pretrained=classmethod(load)
        original_generate=rn.Qwen3TTSModel.generate_voice_clone
        bytext={x.text:x for x in items}
        def generate(self,*a,**kw):
            item=bytext[kw['text'][0]];state.update(stage='synthesizing-single-unapproved-opener',active=item.key);checkpoint()
            current=rn.torch.cuda.current_stream(self.device);stream=rn.torch.cuda.Stream(device=self.device,priority=-1);stream.wait_stream(current)
            with rn.torch.cuda.stream(stream):result=original_generate(self,*a,**kw)
            stream.synchronize();current.wait_stream(stream);rn.torch.cuda.empty_cache();return result
        rn.Qwen3TTSModel.generate_voice_clone=generate
        badness=rn._badness;rn._badness=lambda tail,decay:badness(tail,decay) if rn._passes_quality(tail,decay) else 1000000+badness(tail,decay)
        original_write=rn.sf.write
        def write_audio(file,data,sr,*a,**kw):
            result=original_write(file,data,sr,*a,**kw);p=Path(file).resolve()
            if p.parent==rn.CHUNK_DIR.resolve():
                item=next(x for x in items if x.path.resolve()==p)
                record=dict(key=item.key,path=rel(p),text=item.text,sha256=sha(p),samples=len(data),sampleRate=sr,seconds=len(data)/sr,tailRatio=rn._tail_ratio(data,sr),tailDecayMs=rn._tail_decay_ms(data,sr),heuristicIsApproval=False,asrApproved=False)
                state['results']=[x for x in state['results'] if x['key']!=item.key]+[record];checkpoint()
            return result
        rn.sf.write=write_audio
        rn.render_chunks(items,1,set())
        assert len(state['results'])==1
        for s in request['scenes']:
            pieces=[];ranges=[];position=0;sr=24000
            selected=[x for x in jobs if x.scene_id==s['id']]+[SimpleNamespace(path=ROOT/x['path'],text=x['text']) for x in s['retainedSentences']]
            assert len(selected)==6
            for i,job in enumerate(selected):
                pcm,rate=rn.sf.read(job.path,dtype='float32');assert rate==sr
                faded=rn._apply_edge_fades(pcm,sr)
                ranges.append(dict(sentence=i+1,text=job.text,path=rel(job.path),sha256=sha(job.path),fromSample=position,toSample=position+len(pcm),samples=len(pcm),edgeFadeSeconds=rn.FADE_SECONDS))
                pieces.append(faded);position+=len(pcm)
                if i+1<len(selected):pieces.append(rn.np.zeros(round(.28*sr),dtype=rn.np.float32));position+=round(.28*sr)
            output=ROOT/s['path'];assert not output.exists()
            rn.sf.write(output,rn.np.concatenate(pieces),sr,subtype='FLOAT')
            state['joinedGuides'].append(dict(id=s['id'],path=rel(output),sha256=sha(output),samples=position,sampleRate=sr,seconds=position/sr,sentences=ranges,gapSeconds=.28,sourceSpeed=1,asrApproved=False))
            checkpoint()
        verify();state.update(stage='selective-single-opener-generated-awaiting-ASR-and-research-restoration',generationComplete=True,gpuJobs=0,exitCode=0,finishedAt=now(),active=None,allProtectedInputsUnchanged=True)
        checkpoint();print('One replacement sentence plus five retained PCM chunks joined. Actual ASR and research restoration pending.',flush=True)
    except BaseException:
        state.update(stage='failed-preserving-original84-and-guide-candidates',gpuJobs=0,exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
if __name__=='__main__':main()
