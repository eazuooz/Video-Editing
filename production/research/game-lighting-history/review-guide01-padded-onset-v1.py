"""Independent onset diagnostic on unchanged guide01 PCM, CPU2/GPU0.

Add silence only to recognizer inputs. Never edit the voice or use expected text
as a recognition prompt. Refuse until the previous 40-window worker exited.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-03/production'
OUT=BASE/'native-guide01-padded-onset-execution-v1.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def save(state):
    state['updatedAt']=now()
    tmp=OUT.with_suffix('.json.writing')
    tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
    os.replace(tmp,OUT)
def main():
    import psutil
    old=read(BASE/'native-guides-asr-execution-v1.json')
    assert old['exitCode']==0 and len(old['results'])==40
    try:
        p=psutil.Process(old['actualPid'])
        assert abs(p.create_time()-old['createTime'])>.1,'Prior exact worker still alive'
    except psutil.NoSuchProcess:pass
    assert not OUT.exists(),'Preserve existing diagnostic'
    source=read(BASE/'local/native-guides-asr-v1/whole-01-mesh-distance-field.json')
    audio=ROOT/source['input']['path']
    assert sha(audio)==source['input']['sha256']
    own=psutil.Process()
    state=dict(schemaVersion=1,startedAt=now(),actualPid=own.pid,createTime=own.create_time(),command=own.cmdline(),cwd=own.cwd(),cpuThreads=2,gpuJobs=0,
        source=source['input'],expected=source['expectedKo'],expectedTextUsedAsPrompt=False,sourceChanged=False,results=[],stage='loading-CPU2',approved=False,humanListening='pending',humanPronunciation='pending')
    save(state)
    try:
        import numpy as np,soundfile as sf,torch,torchaudio
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        data,sr=sf.read(audio,dtype='float32')
        assert sr==24000 and len(data)==source['input']['samples']
        state['initial10msRms']=[float(np.sqrt(np.mean(data[i:i+240]**2))) for i in range(0,24000,240)]
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
        proc=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float32,device='cpu')
        problem20=read(BASE/'local/native-guides-asr-v1/context-20-lumen-interior-toggle.json')
        audio20=ROOT/problem20['input']['path']
        assert sha(audio20)==problem20['input']['sha256']
        data20,sr20=sf.read(audio20,dtype='float32')
        assert sr20==sr and len(data20)==problem20['input']['samples']
        state['secondDiagnosticSource']=problem20['input']
        windows=[('guide01-first-two-complete-sentences',data,audio,source,0,10.8,1.0),
                 ('guide01-full-guide',data,audio,source,0,len(data)/sr,1.5),
                 ('guide20-first-12-seconds',data20,audio20,problem20,0,12,1.5),
                 ('guide20-middle-12-seconds',data20,audio20,problem20,12,24,1.5)]
        for label,pcm,input_path,input_record,from_s,to_s,lead in windows:
            lo=round(from_s*sr);hi=min(len(pcm),round(to_s*sr))
            raw=np.concatenate([np.zeros(round(lead*sr),dtype=np.float32),pcm[lo:hi],np.zeros(sr,dtype=np.float32)])
            raw=torchaudio.functional.resample(torch.from_numpy(raw),sr,16000).numpy()
            state.update(stage='recognizing-padded-onset',active=label);save(state)
            result=asr(dict(raw=raw,sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            state['results'].append(dict(label=label,input=input_record['input'],sourceSamples=[lo,hi],leadingSilenceSeconds=lead,trailingSilenceSeconds=1.0,actualSourceUnchanged=True,directlyRead=False,**result))
            assert sha(input_path)==input_record['input']['sha256'];save(state)
            print('DONE '+label,flush=True)
        state.update(stage='diagnostic-complete-awaiting-direct-review',exitCode=0,finishedAt=now(),active=None);save(state)
    except BaseException as error:
        state.update(stage='failed-preserving-source',exitCode=1,error=repr(error),finishedAt=now());save(state);raise
if __name__=='__main__':main()
