"""Exactly five full takes and five complete adjacent contexts, CPU2/GPU0."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, sys
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'projects/game-lighting-history-04/production'
STATE = BASE/'native-followup-asr-execution-v124.json'
FOLDER = BASE/'local/native-followup-asr-v124'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name+'.writing-'+str(os.getpid()))
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n','utf-8')
    os.replace(tmp,path)
def main():
    selected_path = BASE/'native-followup-selected-v126.json'
    selected = read(selected_path)
    if STATE.exists(): raise RuntimeError('Preserve existing scoped recognition')
    ids = {'focus-scale-edit','focus-layers-entry','debugger-command-submit','focus-to-frame-inspection','resource-name-limits'}
    if len(selected['results']) != 5 or {r['id'] for r in selected['results']} != ids:
        raise RuntimeError('Scope must remain exactly five takes')
    for binding in selected['bindings']:
        if sha(ROOT/binding['path']) != binding['sha256']: raise RuntimeError('Changed selection input '+binding['path'])
    for evidence in selected['researchHistories']:
        h = read(ROOT/evidence['path'])
        if h.get('state') != 'research_resume_verified': raise RuntimeError('Research restoration required')
        lease = ROOT/'shared/output/GPU_HANDOFF.json'
        if lease.exists() and read(lease).get('token') == h['token']: raise RuntimeError('Own GPU lease remains active')
    script = read(ROOT/'projects/game-lighting-history-04/script/native-followup.koen.v120.json')
    old_script = read(ROOT/'projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json')
    old_tts = read(BASE/'part3-guided-actions-selected-execution-v84.json')
    assembly = read(BASE/'additive-unmixed-review-assembly-v2.json')
    fresh = {}
    for s in script['scenes']:
        r = next(r for r in selected['results'] if r['id'] == s['id'])
        if not r['technicalTailGatePassed'] or sha(ROOT/r['path']) != r['sha256']:
            raise RuntimeError('Unaccepted/changed take '+s['id'])
        fresh[s['id']] = dict(id=s['id'], path=r['path'], sha256=r['sha256'], sampleRange=[0,r['samples']],ko=s['ko'],en=s['en'])
    def previous(identifier):
        if identifier in fresh: return fresh[identifier]
        s = next((s for s in old_script['scenes'] if s['id']==identifier),None)
        if s:
            r = next(r for r in old_tts['results'] if r['id']==identifier)
            return dict(id=identifier,path=r['path'],sha256=r['sha256'],sampleRange=[0,r['samples']],ko=s['ko'],en=s['en'])
        e = next(e for e in assembly['entries'] if e['id']==identifier)
        return dict(id=identifier,path=assembly['audio']['path'],sha256=assembly['audio']['sha256'],sampleRange=[e['startSample'],e['endSample']],ko=e['text'],en=e['en'])
    jobs = []
    for s in script['scenes']:
        jobs.extend([
            dict(label='whole-'+s['id'],mode='whole',sources=[fresh[s['id']]]),
            dict(label='context-'+s['id'],mode='independent-complete-join',sources=[previous(s['insertAfter']),fresh[s['id']]],gapSamples=6720)
        ])
    plan = dict(preparedAt=stamp(),selected=dict(path=rel(selected_path),sha256=sha(selected_path)),jobs=jobs,expectedWindows=10,cpuThreads=2,gpuJobs=0,expectedTextUsedAsPrompt=False,prior86Repeated=False,finalMixedAsr=False)
    if '--plan-only' in sys.argv:
        path=BASE/'native-followup-asr-plan-v124.json'
        if path.exists(): raise RuntimeError('Preserve existing plan')
        write(path,plan); print('Prepared10; model/recognition0');return
    import psutil
    me=psutil.Process(); ancestors={p.pid for p in me.parents()}|{me.pid}
    if psutil.virtual_memory().available < 6*1024**3: raise RuntimeError('Less than6GiB free')
    for p in psutil.process_iter(['pid','cmdline']):
        if p.pid in ancestors: continue
        try:
            c=' '.join(p.info['cmdline'] or []).lower()
            if 'game-lighting-history' in c and any(x in c for x in ['render-native-followup-v121.py','render-native-tail-v126.py','review-native-followup-v124.py','review-guided-selected-v107.py']):
                raise RuntimeError('Owned exclusive worker still live')
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    state=dict(schemaVersion=1,startedAt=stamp(),actualIdentity=dict(pid=me.pid,createTime=me.create_time(),command=me.cmdline(),cwd=me.cwd()),status='loading-one-CPU-model',plan=plan,completed=[],expectedWindows=10,cpuThreads=2,gpuJobs=0,allDirectlyReviewed=False,humanWholeListeningApproved=False,finalMixedAsr=False,uploaded=False)
    write(STATE,state)
    try:
        import numpy as np,soundfile as sf,torch,torchaudio
        from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        model_path=ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model=AutoModelForSpeechSeq2Seq.from_pretrained(str(model_path),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu')
        processor=AutoProcessor.from_pretrained(str(model_path),local_files_only=True)
        recognize=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float32,device='cpu')
        for job in jobs:
            target=FOLDER/(job['label']+'.json')
            if target.exists(): raise RuntimeError('Preserve existing result')
            parts=[];ranges=[];offset=0
            for source in job['sources']:
                path=ROOT/source['path'];first,last=source['sampleRange']
                if sha(path)!=source['sha256']:raise RuntimeError('PCM changed before ASR')
                with sf.SoundFile(path) as f:
                    if f.samplerate!=24000 or f.channels!=1:raise RuntimeError('PCM format changed')
                    f.seek(first);part=f.read(last-first,dtype='float32')
                if len(part)!=last-first:raise RuntimeError('Truncated PCM')
                if parts:
                    gap=job.get('gapSamples',0);parts.append(np.zeros(gap,dtype=np.float32));offset+=gap
                ranges.append(dict(source=source,windowSampleRange=[offset,offset+len(part)],pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest()))
                parts.append(part);offset+=len(part)
            signal=np.concatenate(parts);state.update(status='recognizing-one-window',current=job['label']);write(STATE,state)
            result=recognize(dict(raw=torchaudio.functional.resample(torch.from_numpy(signal),24000,16000).numpy(),sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
            for source in job['sources']:
                if sha(ROOT/source['path'])!=source['sha256']:raise RuntimeError('PCM changed during ASR')
            record=dict(completedAt=stamp(),job=job,sourceRanges=ranges,sampleRate=24000,samples=len(signal),pcmFloat32Sha256=hashlib.sha256(signal.tobytes()).hexdigest(),expectedTextUsedAsPrompt=False,directFullTextCompared=False,narrationApproved=False,humanWholeListeningApproved=False,finalMixedAsr=False,**result)
            write(target,record);state['completed'].append(dict(label=job['label'],result=rel(target),sha256=sha(target)))
            state.update(current=None,status='window-complete-awaiting-direct-review');write(STATE,state)
            print('DONE '+job['label']+' '+str(len(state['completed']))+'/10',flush=True)
        state.update(status='ten-windows-complete-awaiting-direct-review',endedAt=stamp(),exitCode=0,current=None);write(STATE,state)
    except BaseException as exc:
        state.update(status='failed-preserve-completed',endedAt=stamp(),exitCode=1,error=repr(exc));write(STATE,state);raise
if __name__=='__main__':main()
