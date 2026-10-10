"""Six full two-paragraph contexts from the current AAC, without ASR chunk merging.

Prepared follow-up only until the owned six-pilot renderer has actually exited.
Expected text is never a prompt; the immutable original AAC/PCM is retained.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, os, hashlib, wave, ctypes, traceback
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/adaptive-complete-audio-v2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--render-outer-exit-code',required=True,type=int);args=ap.parse_args()
    assert args.render_outer_exit_code==0
    render=read(OUT/'six-moving-pilots-execution-v4.json');assert render['status']=='completed' and render['exitCode']==0
    resource=read(ROOT/args.resource)
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    prior=read(OUT/'current-whole-audio-asr-execution-v1.json');assert prior['exitCode']==0 and prior['completed']==38
    assert read(OUT/'current-whole-aac-direct-review-v1.json')['all19WholeAnd19IndependentFullExpectedAndActualTextsDirectlyRead']
    wav=ROOT/prior['wav'];assert sha(wav)==prior['wavSha256']
    assert sha(ROOT/prior['aac'])==prior['aacSha256']
    snapshot=read(OUT/'baseline-protected-sha-v1.json');assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
    timeline=read(ROOT/'projects/game-math-polar-3d/production/timeline.json')
    windows=[]
    for sid,i,j,reason in [('03',0,1,'initial word and three components'),('05',3,4,'world-plane height versus ground clearance'),('07',1,2,'three axis names and pitch sign'),('08',3,4,'world-up versus projected tilted horizon'),('09',3,4,'reference directions and world units'),('11',2,3,'world-to-relative vector origin')]:
        s=next(s for s in timeline['scenes'] if s['id']==sid);c=s['cues'][i:j+1]
        windows.append({'label':'adaptive-full-context-'+sid,'scene':sid,'reason':reason,
          'fromSample':round((s['start']+c[0]['start'])*48000),
          'toSample':round((s['start']+c[-1]['end'])*48000),
          'expectedKo':[v['text'] for v in c],'padSamplesEachSide':28800,
          'completeParagraphs':len(c),'expectedWasRecognizerPrompt':False})
    assert all((w['toSample']-w['fromSample'])/48000+1.2<30 for w in windows)
    statefile=OUT/'adaptive-complete-audio-execution-v2.json';assert not statefile.exists() and not LOCAL.exists()
    for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='2'
    os.environ.update(CUDA_VISIBLE_DEVICES='',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    os.environ['PATH']='C:/ProgramData/HP/LCDDisplayHelper/bin'+os.pathsep+os.environ.get('PATH','')
    if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
    import psutil
    assert not psutil.pid_exists(render['pid']) or psutil.Process(render['pid']).create_time()!=render['createTime']
    p=psutil.Process();LOCAL.mkdir(parents=True)
    state={'startedAt':now(),'pid':p.pid,'createTime':p.create_time(),'commandLine':p.cmdline(),'cwd':str(ROOT),
      'resourceEvidence':args.resource,'priorRenderOuterExitCode':args.render_outer_exit_code,
      'cpuThreads':2,'gpuJobs':0,'status':'loading-local-model','completed':0,'total':6,'exitCode':None,
      'aacSha256':prior['aacSha256'],'wavSha256':prior['wavSha256'],
      'expectedWasRecognizerPrompt':False,'currentWholeMixedAsrApproved':False,
      'humanListeningApproved':False,'publicRightsApproved':False,'researchControlChanges':0}
    def save():state['observedAt']=now();statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save();print(json.dumps({'pid':p.pid,'createTime':p.create_time(),'total':6}),flush=True)
    try:
        import torch
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        modelpath=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
        transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        results=[]
        for window in windows:
            with wave.open(str(wav),'rb') as w:
                params=w.getparams();assert (params.framerate,params.nchannels,params.sampwidth)==(48000,2,2)
                w.setpos(window['fromSample']);pcm=w.readframes(window['toSample']-window['fromSample'])
            assert len(pcm)==(window['toSample']-window['fromSample'])*4
            dest=LOCAL/(window['label']+'.wav')
            with wave.open(str(dest),'wb') as w:w.setparams(params);w.writeframes(bytes(28800*4)+pcm+bytes(28800*4))
            state.update(status='transcribing-'+window['label'],activeWindow=window['label']);save()
            raw=transcriber(str(dest),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            row={**window,'windowPath':rel(dest),'windowSha256':sha(dest),'exactCurrentAacSliceSha256':hashlib.sha256(pcm).hexdigest(),
              'text':raw['text'],'words':raw['chunks'],'chunkLengthSeconds':None,'directlyCompared':False}
            results.append(row);(LOCAL/(window['label']+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            (LOCAL/'asr.json').write_text(json.dumps({'results':results,'complete':len(results)==6,'automaticApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            state['completed']=len(results);save();print(json.dumps({'label':window['label'],'text':row['text']},ensure_ascii=False),flush=True)
        assert sha(wav)==prior['wavSha256'] and all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
        state.update(status='completed-await-direct-comparison',exitCode=0,finishedAt=now(),activeWindow=None);save()
    except Exception:
        state.update(status='failed',exitCode=1,error=traceback.format_exc(),finishedAt=now());save();raise
if __name__=='__main__':main()
