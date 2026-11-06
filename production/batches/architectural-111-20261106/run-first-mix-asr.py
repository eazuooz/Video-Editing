"""Finite blind ASR of actual03.02 normalized+BGM mix; no raw-ASR substitution.

Default is CPU readiness only. --execute runs one bounded future GPU worker,
after exact raw voice/audio-build validation. No PCM, project, metadata or
platform changes. Its six contiguous paragraph windows cover every mix sample.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, subprocess, sys, time, uuid
from pathlib import Path
from initialize import HERE, ROOT, MEDIA, read, save


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


raw=module('first_mixed_asr_trusted_helpers',HERE/'run-first-asr.py')
SLUG=raw.SLUG;BASE=MEDIA/SLUG
STATE=MEDIA/'first-mix-asr-progress.json';WORKER=MEDIA/'first-mix-asr-worker.json'
PROFILE=dict(raw.PROFILE,inputKind='actual-normalized-plus-BGM-final-mix',stereoDownmix='arithmetic mean of actual left/right channels',
    coverage='six contiguous original paragraph sample ranges; all quiet lead/tail retained',boundaryWindows=0)
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)


def coverage(evidence,levels,mix):
    rate=mix['sampleRate'];voice=evidence['aggregateWav'];rows=levels['paragraphs']
    assert rate==48000 and mix['channels']==2 and voice['sampleRate']==24000
    assert len(rows)==len(evidence['sceneWavs'])==6 and levels['frames']==voice['frames']
    assert levels['rawVoiceSha256']==voice['sha256'] and levels['voiceFingerprint']==evidence['fingerprint']
    assert levels['allRawPcmPreserved'] and levels['allOriginalWordBoundariesPreserved']
    assert levels['rawRate']==voice['sampleRate'] and mix['frames']==voice['frames']*2
    position=0;tasks=[]
    for i,(row,chunk) in enumerate(zip(rows,evidence['sceneWavs']),1):
        a,b=row['destinationSampleRange'];assert row['sceneId']==f's{i:02}' and a==position and b-a==chunk['frames']
        assert row['trimmedSamples']==row['insertedSamples']==0 and row['rawTakeSha256']==chunk['sha256']
        assert row['rate']==voice['sampleRate']
        tasks.append(dict(key=f'mixed-paragraph-s{i:02}',sceneId=row['sceneId'],beginSample=a*2,endSample=b*2,
            offsetSeconds=a/voice['sampleRate'],durationSeconds=(b-a)/voice['sampleRate'],expected=row['text']))
        position=b
    assert position==voice['frames'] and tasks[0]['beginSample']==0 and tasks[-1]['endSample']==mix['frames']
    return tasks


def prepare_job(path):
    _,evidence,_=raw.exact_voice()  # Exact selected authorization and immutable current raw voice only.
    path=Path(path).resolve();assert path.is_relative_to((BASE/'audio-preparation-v1').resolve())
    build=read(path);folder=path.parent
    assert build['status']=='audio-prepared-final-mix-review-pending' and Path(build['output']).resolve()==folder
    assert build['rawVoiceFingerprint']==evidence['fingerprint'] and build['rawVoiceSha256']==evidence['aggregateWav']['sha256']
    assert build['voiceOffsetSeconds']==0 and build['insertedSamples']==build['trimmedSamples']==0 and build['rawPcmModified'] is False
    line_pin=build['artifacts']['line-levels.json'];mix_pin=build['artifacts']['final-mix.wav']
    levels_path=(folder/line_pin['file']).resolve();mix_path=(folder/mix_pin['file']).resolve()
    assert levels_path.parent==folder and mix_path.parent==folder and raw.voice.sha(levels_path)==line_pin['sha256']
    assert raw.voice.sha(mix_path)==mix_pin['sha256'],'Current actual mixed PCM differs from audio-build'
    import soundfile as sf
    info=sf.info(mix_path);mix=dict(path=str(mix_path),sha256=mix_pin['sha256'],sampleRate=info.samplerate,channels=info.channels,frames=info.frames,subtype=info.subtype)
    assert (mix['sampleRate'],mix['frames'])==(build['mixRate'],build['mixFrames'])
    levels=read(levels_path);tasks=coverage(evidence,levels,mix)
    assert [t['expected'] for t in tasks]==[x.strip() for x in read(raw.PROJECT/'narration-draft.json')['narrationKo']]
    raw_review=build['rawVoiceAsr'];assert raw.voice.sha(raw_review['path'])==raw_review['sha256']
    recognized=read(raw_review['path'])
    assert recognized['voiceFingerprint']==evidence['fingerprint'] and recognized['aggregateSHA256']==evidence['aggregateWav']['sha256']
    assert len(recognized['paragraphs'])==6,'Complete raw ASR prerequisite missing; it is never reused as mixed recognition'
    model_pins=[dict(path=p.name,sha256=raw.voice.sha(p)) for p in sorted(raw.MODEL.iterdir())
                if p.is_file() and (p.suffix=='.safetensors' or p.name.endswith('.json') or p.name in ('merges.txt','vocab.json'))]
    assert any(p['path']=='model.safetensors' for p in model_pins)
    identity=dict(protocol='architectural111-first-mix-asr-v1',audioBuildFingerprint=build['fingerprint'],audioBuildSHA256=raw.voice.sha(path),
        lineLevelsSHA256=line_pin['sha256'],mix=mix,voiceFingerprint=evidence['fingerprint'],profile=PROFILE,tasks=tasks,
        modelPins=model_pins,trustedRecognizerSHA256=raw.voice.sha(raw.TRUSTED))
    fp=raw.digest(identity)
    return dict(fingerprint=fp,identity=identity,output=str(folder/'review/mixed-asr-v1'/fp[:24]),
        audioBuildPath=str(path),rawVoiceAsr=dict(path=raw_review['path'],sha256=raw_review['sha256'],reusedAsMixedRecognition=False),
        modelPath=str(raw.MODEL),processorSHA256=raw.voice.sha(__file__),expectedPrompt=None,aliasesApplied=False,pcmModified=False,humanListening=False)


def cached(job,task):
    path=Path(job['output'])/(task['key']+'.json')
    if not path.exists():return None
    row=read(path)
    assert row['fingerprint']==job['fingerprint'] and row['task']==task and row['mixSHA256']==job['identity']['mix']['sha256']
    assert row['expectedPrompt'] is None and row['aliasesApplied'] is False and row['inputKind']=='actual-normalized-plus-BGM-final-mix'
    return row


def summary(job):
    rows=[cached(job,t) for t in job['identity']['tasks']]
    if any(r is None for r in rows):return None
    mix=job['identity']['mix'];tasks=job['identity']['tasks']
    assert tasks[0]['beginSample']==0 and tasks[-1]['endSample']==mix['frames']
    assert all(a['endSample']==b['beginSample'] for a,b in zip(tasks,tasks[1:]))
    result=dict(status='mixed-asr-complete-literal-review-pending',fingerprint=job['fingerprint'],mixSHA256=mix['sha256'],
        audioBuildFingerprint=job['identity']['audioBuildFingerprint'],voiceFingerprint=job['identity']['voiceFingerprint'],
        mixedAudioPath=mix['path'],sampleRate=mix['sampleRate'],frames=mix['frames'],durationSeconds=mix['frames']/mix['sampleRate'],
        fullActualMixCoverage=True,coveredSamples=sum(t['endSample']-t['beginSample'] for t in tasks),paragraphs=rows,
        rawRecognitionsReused=False,expectedPrompt=None,hotwords=None,aliasesApplied=False,pcmModified=False,
        automaticSpeechPass=False,humanListening=False,finalApproval=False,
        note='Independent mixed-audio recognition only. Literal differences, including 메트릭스/매트릭스, remain review items; spelling display is not proof of pronunciation.')
    save(Path(job['output'])/'review.json',result);return result


def recognize_job(path):
    path=Path(path).resolve();job=read(path);folder=Path(job['output']).resolve()
    assert path.parent==folder and folder.is_relative_to((BASE/'audio-preparation-v1').resolve())
    assert raw.digest(job['identity'])==job['fingerprint'] and job['identity']['profile']==PROFILE
    assert prepare_job(job['audioBuildPath'])['fingerprint']==job['fingerprint']
    pending=[t for t in job['identity']['tasks'] if cached(job,t) is None]
    if not pending:return
    reason=raw.resource_reason()
    if reason:raise raw.PreModelResourceDeclined(reason,'mixed-child-resource-check')
    os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    sys.path.insert(0,str(ROOT/'qwen3-tts'));guard=module('first_mix_existing_gpu_guard',raw.GUARD)
    raw.acquire_guard_before_model(guard)  # Same existing owner/token guard; no wrapper lease.
    trusted=module('first_mix_trusted_recognizer',raw.TRUSTED);assert trusted.MODEL==raw.MODEL
    recognizer=trusted.load_recognizer('cuda')  # Actual model errors stay outside the temporary-resource catch.
    import numpy as np
    import soundfile as sf
    mix=job['identity']['mix']
    for task in pending:
        assert raw.voice.sha(mix['path'])==mix['sha256']
        stereo,rate=sf.read(mix['path'],start=task['beginSample'],stop=task['endSample'],dtype='float32',always_2d=True)
        assert rate==mix['sampleRate'] and stereo.shape==(task['endSample']-task['beginSample'],2) and np.isfinite(stereo).all()
        mono=stereo.mean(axis=1,dtype=np.float64).astype(np.float32)
        recognized=trusted.recognize(recognizer,mono,rate)  # No target words or source transcript passed to the model.
        words=[];flags=[]
        for item in recognized.get('chunks',[]):
            a,b=item['timestamp']
            if a is None or b is None:flags.append('unknown-word-boundary')
            elif a<0 or b>len(mono)/rate+.08 or b<a:flags.append('word-timestamp-outside-mixed-PCM')
            words.append(dict(text=item['text'],timestamp=[None if a is None else task['offsetSeconds']+float(a),None if b is None else task['offsetSeconds']+float(b)]))
        save(folder/(task['key']+'.json'),dict(fingerprint=job['fingerprint'],task=task,mixSHA256=mix['sha256'],
            inputKind='actual-normalized-plus-BGM-final-mix',rawRecognition=recognized,globalWords=words,
            comparison=raw.comparison(task['expected'],recognized['text']),boundaryFlags=sorted(set(flags)),
            stereoDownmix=PROFILE['stereoDownmix'],expectedPrompt=None,aliasesApplied=False,pcmModified=False,humanListening=False))
        print('Recognized actual mix',task['key'],flush=True)
    assert prepare_job(job['audioBuildPath'])['fingerprint']==job['fingerprint']


def recognize_entry(path,decline):
    try:recognize_job(path);return 0
    except raw.PreModelResourceDeclined as error:
        job=read(path);destination=Path(decline).resolve()
        assert destination.parent==Path(job['output']).resolve() and destination.name.startswith('resource-decline-')
        row=dict(protocol='architectural111-first-asr-resource-decline-v1',fingerprint=job['fingerprint'],temporary=True,
            phase='before-model',modelLoaded=False,origin=error.origin,reason=str(error),checkedAt=time.time())
        save(destination,row);print(json.dumps(row,ensure_ascii=False),flush=True);return 75


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audio-build');ap.add_argument('--execute',action='store_true')
    ap.add_argument('--wait-hours',type=float,default=6);ap.add_argument('--recognize',action='store_true');ap.add_argument('--job');ap.add_argument('--resource-decline')
    args=ap.parse_args()
    if args.recognize:
        assert args.job and args.resource_decline;raise SystemExit(recognize_entry(args.job,args.resource_decline))
    if not args.audio_build:
        assert not args.execute;print(json.dumps(dict(ready=False,reason='Exact completed audio-build.json required',modelLoaded=False)));return
    if not args.execute:
        try:
            job=prepare_job(args.audio_build);print(json.dumps(dict(ready=True,fingerprint=job['fingerprint'],mixSHA256=job['identity']['mix']['sha256'],
                coveredSamples=job['identity']['mix']['frames'],paragraphs=6,modelLoaded=False,output=job['output'])))
        except (raw.Pending,FileNotFoundError) as error:print(json.dumps(dict(ready=False,reason=str(error),modelLoaded=False)))
        return
    worker=raw.native.SingleWorker(WORKER).acquire();worker.update(stage='mixed-asr',topicId='03.02')
    child=None;log=None;state=dict(**raw.native.identity(),stage='mixed-asr',topicId='03.02',status='waiting-for-resources',child=None,completed=False)
    try:
        old=read(STATE) if STATE.exists() else {}
        assert not (old.get('pid')!=os.getpid() and (raw.native.alive(old) or raw.native.alive(old.get('child')))),'Prior mixed recognizer remains alive'
        deadline=time.monotonic()+max(0,args.wait_hours)*3600
        while True:
            try:
                job=prepare_job(args.audio_build);folder=Path(job['output']);folder.mkdir(parents=True,exist_ok=True)
                path=folder/'job.json'
                if path.exists():assert read(path)['identity']==job['identity']
                else:save(path,job)
                if summary(job):break
                raw_state=read(raw.STATE) if raw.STATE.exists() else {}
                if raw.native.alive(raw_state) or raw.native.alive(raw_state.get('child')):raise raw.Pending('Existing raw ASR worker/child must finish first')
                reason=raw.resource_reason()
                if reason:raise raw.Pending(reason)
                if time.monotonic()>=deadline:raise RuntimeError('Finite mixed-ASR wait ended; other work preserved')
                attempt=uuid.uuid4().hex[:8];log_path=folder/('recognition-'+attempt+'.log');decline=folder/('resource-decline-'+attempt+'.json')
                log=log_path.open('ab')
                child=subprocess.Popen([str(raw.PYTHON),'-u','-X','utf8',str(Path(__file__).resolve()),'--recognize','--job',str(path),
                    '--resource-decline',str(decline)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=CREATE)
                ident=raw.native.identity(child.pid);worker.update(child=ident);state.update(status='mixed-ASR-running',child=ident,job=str(path),log=str(log_path),fingerprint=job['fingerprint'])
                save(STATE,state);code=child.wait();log.close();log=None
                raw.accept_child_exit(code,decline,job,log_path)
                assert prepare_job(args.audio_build)['fingerprint']==job['fingerprint']
                if not summary(job):raise RuntimeError('Mixed recognition omitted part of the actual complete mix')
                break
            except raw.Pending as error:
                if isinstance(error,raw.ResourceRetry):
                    assert child and child.poll() is not None
                    state.setdefault('resourceDeclines',[]).append(dict(child=state.get('child'),receipt=str(decline),log=str(log_path),diagnostic=error.record))
                    child=None;worker.update(child=None);state.update(child=None,childStillAlive=False)
                state.update(status='waiting-for-resources',reason=str(error),checkedAt=time.time());save(STATE,state)
                if time.monotonic()>=deadline:raise RuntimeError('Finite mixed-ASR wait ended; foreign state untouched')
                time.sleep(10)
        state.update(status='mixed-asr-complete-literal-review-pending',completed=True,review=str(folder/'review.json'),
            mixSHA256=job['identity']['mix']['sha256'],humanListening=False,automaticSpeechPass=False)
    except BaseException as error:state.update(status='failed-or-resource-blocked',error=repr(error));raise
    finally:
        live=bool(child and child.poll() is None);state.update(childStillAlive=live,finishedOrYieldedAt=time.time())
        if live:state['status']='mixed-asr-worker-yielded-child-still-running'
        save(STATE,state)
        if log:log.close()
        worker.close(remove=not live)


if __name__=='__main__':main()
