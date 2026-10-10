"""Current decoded-AAC whole14 then direct-reviewed independent66 contexts, CPU2."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,subprocess,sys,traceback,wave
for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='2'
os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
os.environ['PATH']='C:/ProgramData/HP/LCDDisplayHelper/bin;'+os.environ['PATH']
import psutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,o):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--mode',choices=['whole','contexts'],required=True);ap.add_argument('--recover-prepared-v1',action='store_true');args=ap.parse_args()
    mode=args.mode;recover=args.recover_prepared_v1;version='v2' if recover else 'v1'
    assert not recover or mode=='contexts'
    sp=R/f'current-mixed-{mode}-asr-execution-{version}.json'
    dest=R/f'current-mixed-{mode}-asr-v1';audiofolder=ROOT/f'shared/output/unpublished-teaching-clarity-revision/motion/current-mixed-{mode}-asr-v1'
    logpath=R/f'current-mixed-{mode}-asr-{version}.log'
    assert not any(p.exists() for p in [sp,logpath]),'Inspect completed/running work; no duplicate model.'
    failed=None
    if recover:
        failed=read(R/'current-mixed-contexts-asr-execution-v1.json')
        failed_session=read(R/'current-mixed-contexts-asr-execution-v1.session.json')
        assert failed['exitCode']==1 and failed['completed']==0 and not failed['results']
        assert 'ModuleNotFoundError' in failed['error'] and failed_session['actualOuterExitCode']==1 and failed_session['workerCurrentlyAlive']==False
        assert not psutil.pid_exists(failed['pid']) or abs(psutil.Process(failed['pid']).create_time()-failed['createTime'])>.01
        assert dest.exists() and audiofolder.exists() and not (dest/'asr.json').exists()
        assert sorted(x.name for x in dest.iterdir())==['pcm-slices.json']
    else:
        assert not dest.exists() and not audiofolder.exists(),'Preserve completed/running slices.'
    resource=read(ROOT/args.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    subprocess.run([NODE,'scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],cwd=ROOT,check=True)
    mix=read(R/'current-mix-execution-v1.json');mixsession=read(R/'current-mix-execution-v1.session.json')
    assert mix['actualExitCode']==0 and mixsession['actualOuterExitCode']==0 and mixsession['workerCurrentlyAlive']==False
    assert mix['all14RawPcmPlacementsExact'] and mix['all26ProtectedInputsUnchanged']
    for v in mix['protectedInputs']:assert sha(ROOT/v['path'])==v['sha256']
    source=ROOT/mix['decodedAac'];assert sha(source)==mix['decodedAacSha256']
    plan=read(R/'measured-additive-plan-v1.json');assert sha(R/'measured-additive-plan-v1.json')==mix['planSha256']
    with wave.open(str(source),'rb') as w:
        wp=w.getparams();assert wp.framerate==48000 and wp.nchannels==2 and wp.sampwidth==2
        count=w.getnframes();assert count==plan['totalFrames']*800
    inputs=[]
    if mode=='whole':
        for s in plan['scenes']:
            a=s['startFrame']*800;b=a+round(s['voiceSeconds']*48000)
            assert a<b<=(s['startFrame']+s['frames'])*800
            inputs.append(dict(id=s['id'],scene=s['id'],sourcePath=rel(source),sourceSha256=sha(source),
              startSample=a,endSample=b,zeroPaddingSamplesEachSide=14400,
              expectedKo=[p['ko'] for p in plan['paragraphs'] if p['scene']==s['id']],
              sourceOriginalPcmSha256=s['audioSha256']))
        assert len(inputs)==14
    else:
        context=read(R/'current-mixed-independent-context-plan-v1.json')
        review=read(ROOT/context['wholeReview']);assert sha(ROOT/context['wholeReview'])==context['wholeReviewSha256']
        assert review['all14WholeTextsDirectlyCompared'] and context['currentWholeWordsAndPcmBoundariesDirectlyCompared']
        assert context['sourceSha256']==sha(source);inputs=context['contexts'];assert len(inputs)==66
    me=psutil.Process()
    if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
    if not recover:dest.mkdir();audiofolder.mkdir(parents=True)
    state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
      mode=mode,startedAt=now(),status=f'preparing-current-mixed-{mode}-slices',resource=resource,
      total=len(inputs),completed=0,results=[],cpuThreads=2,cpuJobs=1,gpuJobs=0,exitCode=None,
      mixWavSha256=mix['mixWavSha256'],mixAacSha256=mix['mixAacSha256'],decodedAacSha256=sha(source),
      expectedWasRecognizerPrompt=False,automaticallyApproved=False,currentMixedAudioApproved=False,
      humanListeningApproved=False,humanPronunciationApproved=False,researchManipulations=0,
      recoveryOf='current-mixed-contexts-asr-execution-v1.json' if recover else None,
      preparedSlicesReusedWithoutReextraction=recover)
    def checkpoint():
        ss=sp.with_name(sp.stem+'.session.json')
        if ss.exists():
            v=read(ss);assert v['pid']==me.pid and abs(v['createTime']-me.create_time())<.01;state['sessionId']=v['sessionId']
        state['updatedAt']=now();save(sp,state)
        cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],currentMixedAudioApproved=False,
          ownedJob=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],
            state=rel(sp),log=rel(logpath),completed=state['completed'],total=len(inputs),cpuThreads=2,gpuJobs=0,exitCode=state['exitCode']),
          next='Read every expected/recognized whole and complete independent current-AAC context, then retime KOEN captions and assemble final pair; human hearing/rights remain pending.')
        save(R/'latest-checkpoint.json',cp)
        qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
        q['execution'].update(currentSlug='motion-sickness-games',stage=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next'])
        next(x for x in q['items'] if x['slug']=='motion-sickness-games').update(status=cp['stage'],currentExecution=cp['ownedJob'])
        q['updatedAt']=now();assert qp.read_text('utf-8-sig')==raw;save(qp,q)
    class Tee:
        def __init__(self,out,file):self.out=out;self.file=file
        def write(self,s):self.out.write(s);self.out.flush();self.file.write(s);self.file.flush();return len(s)
        def flush(self):self.out.flush();self.file.flush()
    with logpath.open('x',encoding='utf-8') as log:
        original=sys.stdout;sys.stdout=Tee(original,log);olderr=sys.stderr;sys.stderr=sys.stdout
        try:
            checkpoint();sliced=[]
            if recover:
                prepared=read(dest/'pcm-slices.json');assert prepared['sourceSha256']==sha(source)
                assert len(prepared['slices'])==len(inputs)==66
                with wave.open(str(source),'rb') as w:
                    for row,expected in zip(prepared['slices'],inputs):
                        for k,v in expected.items():assert row[k]==v,(row['id'],k)
                        target=ROOT/row['contextPath'];assert sha(target)==row['contextSha256']
                        a,b=row['startSample'],row['endSample'];w.setpos(a);pcm=w.readframes(b-a)
                        assert hashlib.sha256(pcm).hexdigest()==row['sourceSlicePcmSha256']
                        pad=row['zeroPaddingSamplesEachSide'];data=b'\0'*(pad*4)+pcm+b'\0'*(pad*4)
                        with wave.open(str(target),'rb') as x:
                            assert x.getframerate()==48000 and x.getnchannels()==2 and x.getsampwidth()==2
                            assert x.readframes(x.getnframes())==data
                        assert row['exactSourceStereoPcmBytesMatched'];sliced.append(row)
            with wave.open(str(source),'rb') as w:
                for row in ([] if recover else inputs):
                    a,b=row['startSample'],row['endSample'];assert 0<=a<b<=count
                    w.setpos(a);pcm=w.readframes(b-a);assert len(pcm)==(b-a)*4
                    pad=row['zeroPaddingSamplesEachSide'];data=b'\0'*(pad*4)+pcm+b'\0'*(pad*4)
                    target=audiofolder/(row['id']+'.wav')
                    with wave.open(str(target),'wb') as x:x.setparams(wp);x.writeframes(data)
                    with wave.open(str(target),'rb') as x:assert x.readframes(x.getnframes())==data
                    sliced.append({**row,'contextPath':rel(target),'contextSha256':sha(target),
                      'sourceSlicePcmSha256':hashlib.sha256(pcm).hexdigest(),'exactSourceStereoPcmBytesMatched':True})
            assert sha(source)==mix['decodedAacSha256']
            if not recover:save(dest/'pcm-slices.json',dict(slices=sliced,sourceSha256=sha(source)))
            import torch
            from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
            torch.set_num_threads(2);torch.set_num_interop_threads(1)
            modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
            state['status']='loading-current-mixed-CPU2-whisper';checkpoint()
            model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,
              low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
            processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
            transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
              feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
            for row in sliced:
                state['status']='transcribing-current-mixed-'+row['id'];checkpoint()
                p=ROOT/row['contextPath'];assert sha(p)==row['contextSha256']
                raw=transcriber(str(p),generate_kwargs={'language':'korean','task':'transcribe'},chunk_length_s=30,return_timestamps='word')
                result={**row,'text':raw['text'],'words':raw['chunks'],'expectedWasRecognizerPrompt':False,'directReview':False,'approved':False}
                assert sha(p)==row['contextSha256'];save(dest/(row['id']+'.json'),result);state['results'].append(result)
                state['completed']=len(state['results']);save(dest/'asr.json',dict(complete=len(state['results'])==len(inputs),results=state['results'],
                  decodedAacSha256=sha(source),mixAacSha256=mix['mixAacSha256'],automaticApproval=False))
                checkpoint();print(json.dumps(dict(id=row['id'],text=result['text']),ensure_ascii=False),flush=True)
            for v in mix['protectedInputs']:assert sha(ROOT/v['path'])==v['sha256']
            assert sha(source)==mix['decodedAacSha256']
            state.update(status=f'current-mixed-{mode}-ASR-closed-awaiting-direct-review',exitCode=0,cpuJobs=0,finishedAt=now());checkpoint()
        except BaseException:
            state.update(status=f'failed-current-mixed-{mode}-ASR-preserve-files',exitCode=1,cpuJobs=0,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
        finally:sys.stdout=original;sys.stderr=olderr
if __name__=='__main__':main()
