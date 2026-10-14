"""One CPU2/GPU0 recognizer following completed episodes, never rerunning TTS."""
from pathlib import Path
import datetime,hashlib,json,os,time
import psutil
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'production/research/game-lighting-history'
STATE=BASE/'remaining-voice-asr-execution-v1.json'
PRODUCER=BASE/'remaining-tts-execution-v1.json'
SLUGS=[f'game-lighting-history-0{x}' for x in [2,3,4]]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,j):
    p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+'.tmp-'+str(os.getpid()))
    t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(t,p)
def main():
    if STATE.exists(): raise RuntimeError('Inspect live/completed recognition; never repeat complete work.')
    ancestors={os.getpid(),*[p.pid for p in psutil.Process().parents()]}
    for p in psutil.process_iter(['pid','name','cmdline']):
        cmd=' '.join(p.info['cmdline'] or []).replace('\\','/')
        if p.info['pid'] not in ancestors and (p.info['name'] or '').lower()=='python.exe' and 'review-remaining-voice-v1.py' in cmd:
            raise RuntimeError('Another owned recognizer exists.')
    state=dict(schemaVersion=1,status='waiting-for-complete-episode',startedAt=now(),
               actualIdentity=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline()),
               cpuThreads=2,gpuJobs=0,expectedTextUsedAsPrompt=False,expectedWindows=90,completed=0,
               episodes=[],humanWholeListeningApproved=False,currentNarrationApproved=False,finalMixedAsr=False)
    write(STATE,state)
    asr=None
    for slug in SLUGS:
        deadline=time.monotonic()+43200
        while True:
            prod=read(PRODUCER)
            done=next((x for x in prod['completed'] if x['slug']==slug),None)
            if done: break
            if prod['status'] in ['child-failed','input-preparation-timeout']:
                raise RuntimeError('Producer failed; preserve completed recognition and inspect.')
            if time.monotonic()>deadline: raise RuntimeError('Producer wait exceeded12hours.')
            time.sleep(5)
        path=ROOT/done['files']['.wav']['path'];assert sha(path)==done['files']['.wav']['sha256']
        timing=read(ROOT/done['files']['.timing.json']['path'])
        project=ROOT/'projects'/slug;review=read(project/'production/script-input-review-v1.json')
        for lang in ['ko','en']:
            assert sha(project/f'script/narration.{lang}.json')==review['finalInputHashes'][lang]
        script=read(project/'script/narration.ko.json')
        if asr is None:
            state.update(status='loading-CPU-model');write(STATE,state)
            import numpy as np,soundfile as sf,torch,torchaudio
            from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
            torch.set_num_threads(2);torch.set_num_interop_threads(1)
            model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
            model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
            processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
            asr=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        pcm,sr=sf.read(path,dtype='float32');out=project/'production/local/voice-asr-v1'
        episode=dict(slug=slug,audioSha256=sha(path),timingSha256=done['files']['.timing.json']['sha256'],
                     sampleRate=sr,samples=len(pcm),durationSeconds=len(pcm)/sr,windows=[])
        state['episodes'].append(episode)
        for scene in script['scenes']:
            entries=[x for x in timing['entries'] if x['scene_id']==scene['id']]
            assert len(entries)==len(scene['lines'])
            start,end=entries[0]['start'],entries[-1]['end']
            # Paragraph boundaries are provisional. Include a wide leading margin;
            # clipped neighboring text never counts as a omitted target paragraph.
            context_start=max(start,entries[max(0,len(entries)-3)]['start']-20)
            for mode,a,target in [('whole',start,scene['lines']),('context',context_start,scene['lines'][-3:])]:
                label=mode+'-'+scene['id'];f=out/(label+'.json')
                if f.exists(): raise RuntimeError('Preserve existing recognition: '+str(f))
                state.update(status='recognizing',currentEpisode=slug,currentWindow=label);write(STATE,state)
                part=pcm[round(a*sr):round(end*sr)]
                options=dict(generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
                if mode=='whole':options.update(chunk_length_s=30,stride_length_s=5)
                result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(part),sr,16000).numpy(),sampling_rate=16000),**options)
                record=dict(label=label,scene=scene['id'],mode='chunked30s-stride5s' if mode=='whole' else 'independent-sequential-long-form',
                            audioSha256=episode['audioSha256'],pcmSha256=hashlib.sha256(part.tobytes()).hexdigest(),
                            sourceFromSeconds=a,sourceToSeconds=end,expectedKo=target,completedAt=now(),
                            boundaryCaveat='Context starts from provisional paragraph timing with20s margin; compare target completion, not clipped preceding margin.',
                            directFullTextCompared=False,approved=False,**result)
                write(f,record);episode['windows'].append(dict(label=label,file=f.relative_to(ROOT).as_posix(),sha256=sha(f)))
                state['completed']+=1;write(STATE,state);print('DONE '+slug+' '+label,flush=True)
        assert sha(path)==episode['audioSha256']
        episode.update(status='complete-awaiting-direct-review',humanListeningApproved=False)
        write(STATE,state)
    state.update(status='all90-windows-complete-awaiting-direct-review',endedAt=now(),exitCode=0,currentEpisode=None,currentWindow=None)
    write(STATE,state)
if __name__=='__main__':main()
