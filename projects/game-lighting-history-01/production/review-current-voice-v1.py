"""CPU read-back of the frozen episode1 voice, after its existing producer exits.

Expected text is saved for direct review, never passed as a recognizer prompt.
No model/GPU allocation until the owned handoff confirms producer exit0 and
restoration of the research queue. Both chunked whole-scene and independent
long-form ending-context results stay unapproved until their text is read.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-01'
OUT=BASE/'production/local/current-voice-asr-v1'
EXECUTION=BASE/'production/current-voice-asr-execution-v1.json'
TOKEN='9d36bf53-8298-4783-89c4-6171897133b1'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_name(p.name+'.tmp-'+str(os.getpid()))
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(p)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wait-for-existing-tts',action='store_true')
    ap.add_argument('--plan-only',action='store_true')
    args=ap.parse_args()
    if EXECUTION.exists():
        raise SystemExit('Existing ASR execution preserved. Inspect/resume explicit remaining windows; do not repeat completed ASR.')
    frozen=read(BASE/'production/script-source-wording-review-v4.json')
    for lang in ['ko','en']:
        if sha(BASE/f'script/narration.{lang}.json')!=frozen['finalInputHashes'][lang]:
            raise SystemExit('Reviewed narration changed before ASR')
    manifest=read(BASE/'project.json')
    audio=ROOT/manifest['paths']['narration']
    timing=audio.with_suffix('.timing.json')
    # The shared renderer uses <stem>.timing.json; no guessed scene times.
    state=dict(schemaVersion=1,project='game-lighting-history-01',startedAt=now(),pid=os.getpid(),device='cpu',cpuThreads=2,gpuJobs=0,status='prepared' if args.plan_only else 'waiting-for-existing-tts',expectedScenes=13,expectedWindows=26,completed=0,ttsSessionId=53583,handoffToken=TOKEN,handoffHistory='shared/output/gpu-handoff/'+TOKEN+'.json',expectedTextUsedAsPrompt=False,automaticApproval=False,currentNarrationApproved=False,humanWholeListening='pending',resultDirectory=str(OUT.relative_to(ROOT)).replace('\\','/'),commandLine=sys.argv)
    if args.plan_only:
        write(BASE/'production/current-voice-asr-plan-v1.json',state);print(json.dumps(state,ensure_ascii=False));return
    write(EXECUTION,state)
    history=ROOT/state['handoffHistory']
    while True:
        handoff=read(history) if history.exists() else {}
        if handoff.get('ttsExitCode') not in [None,0]:
            state.update(status='producer-failed-ASR-not-started',failureObservedAt=now(),producerExit=handoff['ttsExitCode']);write(EXECUTION,state);raise SystemExit('Producer failed; preserve voice checkpoints before starting ASR')
        ready=handoff.get('ttsExitCode')==0 and handoff.get('state') in ['research_resume_verified','original_queue_continues','research_already_complete_or_failed'] and audio.exists() and timing.exists()
        if ready: break
        if not args.wait_for_existing_tts:
            state.update(status='prerequisite-not-ready-ASR-not-started');write(EXECUTION,state);raise SystemExit('Existing TTS has not completed/restored research yet')
        time.sleep(10)
    import psutil
    import numpy as np
    import soundfile as sf
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    import torchaudio
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    ko=read(BASE/'script/narration.ko.json'); times=read(timing)
    if len(ko['scenes'])!=13 or len(times['entries'])!=108:
        raise RuntimeError('Incomplete actual voice/timing input')
    data,sr=sf.read(audio,dtype='float32')
    if data.ndim!=1 or not np.isfinite(data).all(): raise RuntimeError('Current voice must be finite mono PCM')
    audio_sha=sha(audio)
    state.update(status='loading-CPU-recognizer',actualPythonIdentity=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline()),audioSha256=audio_sha,actualDurationSeconds=len(data)/sr,sampleRate=sr,timingSha256=sha(timing),scriptHashes=frozen['finalInputHashes'],ttsCompletion=handoff)
    write(EXECUTION,state)
    windows=[]
    for scene in ko['scenes']:
        entries=[e for e in times['entries'] if e['scene_id']==scene['id']]
        a,b=entries[0]['start'],entries[-1]['end']
        if len(entries)!=len(scene['lines']): raise RuntimeError('Scene lines/timing mismatch')
        windows.append(dict(label='whole-'+scene['id'],scene=scene['id'],fromSeconds=a,toSeconds=b,expectedKo=scene['lines'],recognitionMode='chunked30s-stride5s',scope='All current scene speech'))
    for scene in ko['scenes']:
        entries=[e for e in times['entries'] if e['scene_id']==scene['id']]
        entry=entries[max(0,len(entries)-3)]
        a=max(entries[0]['start'],entry['start']-2)
        b=entries[-1]['end']
        windows.append(dict(label='context-'+scene['id'],scene=scene['id'],fromSeconds=a,toSeconds=b,expectedKo=scene['lines'],focusKo=scene['lines'][-3:],recognitionMode='independent-sequential-long-form',boundaryMethod='Measured PCM scene and quiet-valley paragraph estimate; completeness of first paragraph requires direct read-back',scope='Independent ending context; previous audible text is retained, not misclassified as extra speech'))
    write(OUT/'request.json',dict(audioSha256=audio_sha,timingSha256=sha(timing),windows=windows,expectedTextUsedAsPrompt=False,currentNarrationApproved=False))
    model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
    model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
    processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
    asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
    state.update(status='running',model=str(model_path),recognizerStartedAt=now());write(EXECUTION,state)
    for item in windows:
        path=OUT/(item['label']+'.json')
        if path.exists(): raise RuntimeError('Unexpected existing result; do not overwrite')
        pcm=data[round(item['fromSeconds']*sr):round(item['toSeconds']*sr)]
        resampled=torchaudio.functional.resample(torch.from_numpy(pcm),sr,16000).numpy()
        state.update(currentWindow=item['label'],windowStartedAt=now());write(EXECUTION,state)
        print('START '+item['label'],flush=True)
        settings=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
        if item['recognitionMode']=='chunked30s-stride5s': settings.update(chunk_length_s=30,stride_length_s=5)
        result=asr(dict(raw=resampled,sampling_rate=16000),**settings)
        write(path,dict(**item,audioSha256=audio_sha,completedAt=now(),directFullTextCompared=False,approved=False,**result))
        state['completed']+=1;state.update(lastResult=str(path.relative_to(ROOT)).replace('\\','/'));write(EXECUTION,state)
        print('DONE '+item['label'],flush=True)
    if sha(audio)!=audio_sha: raise RuntimeError('Audio changed during read-back')
    state.update(status='complete-awaiting-direct-whole-and-context-review',currentWindow=None,endedAt=now(),exitCode=0);write(EXECUTION,state)
    print(json.dumps(dict(completed=26,approved=False,actualDurationSeconds=len(data)/sr)),flush=True)

if __name__=='__main__': main()
