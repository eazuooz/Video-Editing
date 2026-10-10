"""One CPU2 worker:13 repair sentences and4 complete joined-guide decodes.

Never recognizes the other18 guides again or promotes heuristic results.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,traceback
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/game-lighting-history-03/production'
REQUEST=BASE/'native-guide-repairs-tts-request-v2.json';TTS=BASE/'native-guide-repairs-tts-execution-v2.json';STATE=BASE/'native-guide-repairs-asr-execution-v2.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.writing-'+str(os.getpid()));tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');ap.add_argument('--resume-import-failure',action='store_true');args=ap.parse_args()
    request=read(REQUEST);assert len(request['scenes'])==2 and request['expectedSentenceChunks']==13
    if args.dry_run:print('13 sentence +2 whole +2 independent context windows planned; no model/state/GPU.',flush=True);return
    previous=None
    if STATE.exists():
        previous=read(STATE)
        assert args.resume_import_failure and previous['exitCode']==1 and not previous['results'] and "No module named 'soundfile'" in previous['error'],'Preserve completed/in-progress recognition'
        archived=BASE/'native-guide-repairs-asr-import-failure-v2.json';assert not archived.exists();save(archived,previous)
    done=read(TTS);assert done['exitCode']==0 and done['generationComplete'] and len(done['results'])==13 and len(done['joinedGuides'])==2
    assert not (ROOT/'shared/output/GPU_HANDOFF.json').exists(),'Observe exact research restoration before CPU ASR'
    lease=read(ROOT/'shared/output/gpu-handoff'/(done['leaseToken']+'.json'));assert lease['state']=='research_resume_verified' and lease['ttsExitCode']==0
    for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
    import psutil
    own=psutil.Process();owner=psutil.Process(lease['resumedQueue']['pid']);q=read(Path(lease['queueDir'])/'status.json')
    assert abs(owner.create_time()-lease['resumedQueue']['createTime'])<.1 and owner.cmdline()==lease['resumedQueue']['command'] and owner.cwd().lower()==lease['resumedQueue']['cwd'].lower()
    assert q['owner_pid']==owner.pid and q['status'] in ['running','waiting_for_resources']
    ancestors={p.pid for p in own.parents()}
    for p in psutil.process_iter(['pid','name','cmdline']):
        if p.pid==own.pid or p.pid in ancestors:continue
        name=(p.info['name'] or '').lower();cmd=' '.join(p.info['cmdline'] or [])
        assert not ('ffmpeg' in name and 'game-lighting-history' in cmd),'Another owned media worker'
        assert not ('python' in name and 'review-' in cmd and 'game-lighting-history/' in cmd),'Another owned recognition worker'
    windows=[]
    for s in request['scenes']:
        guide=next(x for x in done['joinedGuides'] if x['id']==s['id'])
        for i,x in enumerate(guide['sentences']):
            source=next(z for z in done['results'] if z['path']==x['path'])
            windows.append(dict(label=s['id']+'-sentence-'+str(i+1),guideId=s['id'],source=source,expectedKo=x['text'],expectedEn=s['enLines'][i],mode='sentence'))
        for mode in ['whole','context']:windows.append(dict(label=mode+'-'+s['id'],guideId=s['id'],source=guide,expectedKo=s['text'],expectedEn=s['en'],mode=mode))
    assert len(windows)==17
    import soundfile as sf,torch,torchaudio
    state=dict(schemaVersion=1,startedAt=now(),actualPid=own.pid,createTime=own.create_time(),commandLine=own.cmdline(),cwd=own.cwd(),stage='loading-CPU2-repair-recognizer',cpuThreads=2,gpuJobs=0,totalWindows=17,results=[],active=None,exitCode=None,requestSha256=sha(REQUEST),ttsExecutionSha256=sha(TTS),researchObservation=q,expectedTextUsedAsPrompt=False,allDirectlyCompared=False,approved=False,finalMixedAsr=False,humanListening='pending',humanPronunciation='pending',other18Repeated=False,original84Repeated=False,initialImportFailure='native-guide-repairs-asr-import-failure-v2.json' if previous else None)
    def update():
        state['updatedAt']=now();save(STATE,state)
        p=ROOT/'production/research/game-lighting-history/checkpoint.json';cp=read(p);cp.update(updatedAt=now(),stage=state['stage'],ownedJobsRunning=[] if state['exitCode'] is not None else [dict(pid=own.pid,createTime=own.create_time(),commandLine=own.cmdline(),state=rel(STATE),sessionId=cp.get('episode03GuideRepairAsrSessionId'),cpuThreads=2,gpuJobs=0,completed=len(state['results']),total=17)]);save(p,cp)
    update()
    try:
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu');processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        for w in windows:
            source=w['source'];audio=ROOT/source['path'];assert sha(audio)==source['sha256']
            data,sr=sf.read(audio,dtype='float32');assert data.ndim==1 and len(data)==source['samples'] and sr==source['sampleRate']
            raw=torchaudio.functional.resample(torch.from_numpy(data),sr,16000).numpy();opts=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            if w['mode']=='whole':opts.update(chunk_length_s=30,stride_length_s=5)
            state.update(stage='recognizing-selective-repair-CPU2',active=w['label']);update();result=asr(dict(raw=raw,sampling_rate=16000),**opts);assert sha(audio)==source['sha256']
            out=BASE/'local/native-guide-repairs-asr-v2'/(w['label']+'.json');assert not out.exists()
            record=dict(schemaVersion=1,completedAt=now(),label=w['label'],guideId=w['guideId'],mode=w['mode'],input=dict(path=source['path'],sha256=source['sha256'],samples=len(data),sampleRate=sr,seconds=len(data)/sr),expectedKo=w['expectedKo'],expectedEn=w['expectedEn'],expectedTextUsedAsPrompt=False,directlyCompared=False,approved=False,finalMixedAsr=False,humanListening='pending',humanPronunciation='pending',**result)
            save(out,record);state['results'].append(dict(label=w['label'],path=rel(out),sha256=sha(out)));update();print('DONE '+w['label']+' '+str(len(state['results']))+'/17',flush=True)
        state.update(stage='17-repair-windows-complete-awaiting-direct-comparison',active=None,exitCode=0,finishedAt=now());update()
    except BaseException:
        state.update(stage='failed-preserving-repair-PCM-and-results',active=None,exitCode=1,finishedAt=now(),error=traceback.format_exc());update();raise
if __name__=='__main__':main()
