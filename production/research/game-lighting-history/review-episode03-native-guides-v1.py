"""Review new guide PCM only, one CPU2 recognizer; never approve or resynthesize.

Each guide is recognized with both chunked30/stride5 and independent sequential
long-form decoding. Both inputs contain the complete guide. Actual assembly
joins and the final Nimbus mix remain separate review gates.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, time
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'projects/game-lighting-history-03'
BASE=PROJECT/'production'
STATE=BASE/'native-guides-asr-execution-v1.json'
REQUEST=BASE/'native-guides-tts-request-v1.json'
TTS=BASE/'native-guides-tts-execution-v1.json'
QUEUE=Path('C:/Users/eazuo/renderformer/tmp/placement_focus_20261008/status.json')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,j):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.writing-'+str(os.getpid()))
    tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
    os.replace(tmp,p)
def research_live(psutil):
    q=read(QUEUE)
    try:
        done=read(TTS);handoff=read(ROOT/'shared/output/gpu-handoff'/(done['leaseToken']+'.json'))
        resumed=handoff['resumedQueue'];owner=psutil.Process(q['owner_pid'])
        live=(handoff['state']=='research_resume_verified' and handoff['ttsExitCode']==0
          and owner.pid==resumed['pid'] and abs(owner.create_time()-resumed['createTime'])<.1
          and owner.cmdline()==resumed['command'] and owner.cwd().lower()==resumed['cwd'].lower()
          and q['status'] in ['running','waiting_for_resources']
          and not (ROOT/'shared/output/GPU_HANDOFF.json').exists())
        if live and q['status']=='running':
            child=psutil.Process(q['child_pid']);live=child.ppid()==owner.pid
    except (psutil.NoSuchProcess,KeyError):live=False
    return live,q
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
    request=read(REQUEST)
    assert len(request['scenes'])==20 and request['pairedWholeTextReview']
    if args.dry_run:
        print('Prepared20whole+20independent complete-guide decodes. GPU0/model0; completed PCM and exact verified resumed research owner required before execution.',flush=True)
        return
    assert not STATE.exists(),'Preserve existing recognition execution; inspect its actual identity first'
    done=read(TTS)
    assert done['generationComplete'] and done['exitCode']==0 and len(done['results'])==20
    assert sha(REQUEST)==done['requestSha256']
    for x in request['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
    sources={x['id']:x for x in done['results']}
    for s in request['scenes']:assert sha(ROOT/s['path'])==sources[s['id']]['sha256'],s['path']
    import psutil
    own=psutil.Process()
    competing=[];ancestors={p.pid for p in own.parents()}
    for p in psutil.process_iter(['pid','name','cmdline']):
        if p.pid==own.pid or p.pid in ancestors:continue
        cmd=' '.join(p.info['cmdline'] or [])
        name=(p.info['name'] or '').lower()
        if ('ffmpeg' in name and 'game-lighting-history' in cmd) or ('python' in name and 'review-' in cmd and ('voice-window' in cmd or 'current-assembly-window' in cmd or 'review-episode03-native-guides-v1.py' in cmd)):
            competing.append(dict(pid=p.pid,command=cmd))
    assert not competing,competing
    live,q=research_live(psutil)
    assert live,'Actual exact resumed research owner and running/resource-wait state required; no active TTS lease'
    state=dict(schemaVersion=1,startedAt=now(),stage='loading-CPU2-recognizer',actualPid=own.pid,createTime=own.create_time(),commandLine=own.cmdline(),cwd=own.cwd(),
        cpuThreads=2,gpuJobs=0,expectedWindows=40,results=[],active=None,requestSha256=sha(REQUEST),ttsExecutionSha256=sha(TTS),
        researchObservation=q,expectedTextUsedAsPrompt=False,allDirectlyCompared=False,approved=False,finalMixedAsr=False,assembledJoinReview=False,
        humanWholeListening='pending',humanPronunciation='pending',original84AsrRepeated=False)
    def update():state['updatedAt']=now();save(STATE,state)
    update()
    try:
        import numpy as np,soundfile as sf,torch,torchaudio
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        folder=BASE/'local/native-guides-asr-v1'
        for s in request['scenes']:
            audio=ROOT/s['path'];source=sources[s['id']]
            data,sr=sf.read(audio,dtype='float32')
            assert data.ndim==1 and len(data)==source['samples'] and sr==source['sampleRate']
            raw=torchaudio.functional.resample(torch.from_numpy(data),sr,16000).numpy()
            for mode in ['whole','context']:
                label=mode+'-'+s['id'];out=folder/(label+'.json')
                assert not out.exists(),'Preserve existing result '+label
                state.update(stage='recognizing-guide-CPU2',active=label);update()
                opts=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
                if mode=='whole':opts.update(chunk_length_s=30,stride_length_s=5)
                result=asr(dict(raw=raw,sampling_rate=16000),**opts)
                assert sha(audio)==source['sha256'],'Guide PCM changed during recognition'
                record=dict(schemaVersion=1,completedAt=now(),label=label,guideId=s['id'],afterOriginalParagraph=s['after'],
                    mode='chunked30s-stride5s' if mode=='whole' else 'independent-sequential-long-form',
                    input=dict(path=s['path'],sha256=source['sha256'],samples=len(data),sampleRate=sr,seconds=len(data)/sr,pcmSha256=hashlib.sha256(data.tobytes()).hexdigest()),
                    expectedKo=[s['text']],expectedEn=[s['en']],expectedTextUsedAsPrompt=False,
                    directWholeTextCompared=False,approved=False,finalMixedAsr=False,humanWholeListeningApproved=False,
                    caveat='Complete standalone guide decoded independently; actual guide-to-original PCM joins and final mix require additional separate review.',**result)
                save(out,record);state['results'].append(dict(label=label,path=rel(out),sha256=sha(out)));update()
                print('DONE '+label+' '+str(len(state['results']))+'/40',flush=True)
            state.update(stage='returning-CPU-between-guides',active=None);update()
            time.sleep(30)
            live,q=research_live(psutil)
            state['researchObservation']=q;update()
            assert live,'Research queue no longer live; preserve completed recognitions and inspect before continuing'
        state.update(stage='40-guide-windows-complete-awaiting-direct-text-review',finishedAt=now(),exitCode=0,active=None);update()
    except BaseException as error:
        state.update(stage='failed-preserving-guide-PCM-and-completed-recognitions',finishedAt=now(),exitCode=1,error=repr(error));update();raise
if __name__=='__main__':main()
