"""One immutable current03/04 voice window, CPU2 only; no synthesis or approval."""
from pathlib import Path
import argparse, datetime, hashlib, json, os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/research/game-lighting-history'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):
    p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_name(p.name+'.tmp-'+str(os.getpid()))
    temp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temp,p)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slug',choices=['game-lighting-history-03','game-lighting-history-04'],required=True)
    parser.add_argument('--scene',required=True)
    parser.add_argument('--mode',choices=['whole','context'],required=True)
    args=parser.parse_args()
    completed=read(BASE/'remaining-tts-execution-v2.json')
    if completed['status']!='all-remaining-tts-produced-and-decoded': raise RuntimeError('Current TTS completion missing')
    done=next(x for x in completed['completed'] if x['slug']==args.slug)
    project=ROOT/'projects'/args.slug
    review=read(project/'production/script-input-review-v1.json')
    for lang in ['ko','en']:
        if sha(project/f'script/narration.{lang}.json')!=review['finalInputHashes'][lang]:
            raise RuntimeError('Current approved script input changed')
    audio=ROOT/done['files']['.wav']['path']
    timing_path=ROOT/done['files']['.timing.json']['path']
    for ext,p in [('.wav',audio),('.timing.json',timing_path)]:
        if sha(p)!=done['files'][ext]['sha256']: raise RuntimeError('Generated current input changed')
    script=read(project/'script/narration.ko.json')
    scene=next(s for s in script['scenes'] if s['id']==args.scene)
    entries=[e for e in read(timing_path)['entries'] if e['scene_id']==args.scene]
    if len(entries)!=len(scene['lines']): raise RuntimeError('Paragraph/timing count drift')
    start,end=entries[0]['start'],entries[-1]['end']
    if args.mode=='context': start=max(start,entries[max(0,len(entries)-3)]['start']-20)
    target=scene['lines'] if args.mode=='whole' else scene['lines'][-3:]
    folder=project/'production/local/voice-asr-v2'
    label=args.mode+'-'+args.scene
    output=folder/(label+'.json')
    execution=folder/(label+'.execution.json')
    if output.exists(): raise RuntimeError('Existing completed recognition preserved')
    import psutil
    own=psutil.Process()
    identity=dict(pid=own.pid,createTime=own.create_time(),command=own.cmdline(),executable=own.exe(),cwd=own.cwd())
    state=dict(startedAt=now(),status='loading-CPU-model',actualIdentity=identity,
               cpuThreads=2,gpuJobs=0,cudaVisibleDevices=os.environ['CUDA_VISIBLE_DEVICES'],
               slug=args.slug,label=label,audioSha256=done['files']['.wav']['sha256'],
               sourceFromSeconds=start,sourceToSeconds=end,currentNarrationApproved=False)
    write(execution,state)
    try:
        import numpy as np, soundfile as sf, torch, torchaudio
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,
            low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        with sf.SoundFile(audio) as source:
            sr=source.samplerate
            source.seek(round(start*sr))
            part=source.read(round(end*sr)-round(start*sr),dtype='float32')
        if part.ndim!=1: raise RuntimeError('Expected current mono narration')
        state.update(status='recognizing',sampleRate=sr,sourceSamples=len(part));write(execution,state)
        options=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        if args.mode=='whole': options.update(chunk_length_s=30,stride_length_s=5)
        result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(part),sr,16000).numpy(),sampling_rate=16000),**options)
        if sha(audio)!=state['audioSha256']: raise RuntimeError('Current audio changed during recognition')
        record=dict(schemaVersion=2,slug=args.slug,label=label,scene=args.scene,
            mode='chunked30s-stride5s' if args.mode=='whole' else 'independent-sequential-long-form',
            audioSha256=state['audioSha256'],timingSha256=done['files']['.timing.json']['sha256'],
            pcmSha256=hashlib.sha256(part.tobytes()).hexdigest(),sampleRate=sr,sourceSamples=len(part),
            sourceFromSeconds=start,sourceToSeconds=end,expectedKo=target,completedAt=now(),
            boundaryCaveat='Context uses provisional paragraph timing and20s leading margin; clipped neighboring text is not target omission.',
            expectedTextUsedAsPrompt=False,directFullTextCompared=False,approved=False,
            humanWholeListeningApproved=False,finalMixedAsr=False,**result)
        write(output,record)
        state.update(status='complete-awaiting-direct-review',endedAt=now(),exitCode=0,result=output.relative_to(ROOT).as_posix(),resultSha256=sha(output))
        write(execution,state)
        print('DONE '+args.slug+' '+label,flush=True)
    except BaseException as error:
        state.update(status='failed',endedAt=now(),error=repr(error));write(execution,state)
        raise
if __name__=='__main__': main()
