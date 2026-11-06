"""Finite S03 two-semantic-take level repair; same voice singleton/state.

Default prepares nothing. --execute may synthesize only missing s03-a/b items
with the unchanged approved profile. Other five canonical WAVs are read-only.
All component/old versions survive; source-text, ASR, level and human QA stay
separate. The shared Qwen engine is never edited or imported here.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, io, json, os, shutil, subprocess, sys, time, uuid, wave
from pathlib import Path
import numpy as np
import soundfile as sf
from initialize import HERE, ROOT, read, save


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


voice=module('s03_repair_voice_tools',HERE/'run-first-voice.py')
audio=module('s03_repair_scalar_levels',HERE/'prepare-first-audio.py')
OTHERS=('s01','s02','s04','s05','s06');PARTS=('s03-a','s03-b')
PROTOCOL='architectural111-first-s03-two-take-level-repair-v1'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)


def validate(prov):
    scenes=prov['identity']['scenes'];assert [s['id'] for s in scenes]==[f's{i:02}' for i in range(1,7)]
    lines=scenes[2]['lines'];assert len(lines)==2 and lines[0].endswith('거죠.') and lines[1].startswith('이 틈보다')
    assert all(len(s['lines'])==1 for s in scenes if s['id']!='s03')
    assert ' '.join(lines)==prov['spokenLines'][2]
    assert prov['sceneGapSeconds']==0 and prov['identity']['tts']['edgeFadeSeconds']==0
    identity=dict(protocol=PROTOCOL,canonicalFingerprint=prov['fingerprint'],nonSceneSynthesisIdentity={k:v for k,v in prov['identity'].items() if k!='scenes'},
        items=[dict(id=sid,lines=[text]) for sid,text in zip(PARTS,lines)],engineSHA256=prov['audit']['engineSHA256'],
        scalarProfile=audio.PROFILE,scalarProcessorSHA256=voice.sha(HERE/'prepare-first-audio.py'),
        numpyVersion=np.__version__,soundfileVersion=sf.__version__,libsndfileVersion=sf.__libsndfile_version__,processorSHA256=voice.sha(__file__))
    return dict(fingerprint=audio.digest(identity),identity=identity,lines=lines)


def other_pins(prov,output):
    receipt=read(output/'voice-inputs.json');assert receipt['fingerprint']==prov['fingerprint']
    reused=receipt.get('verifiedSceneReuse',{}).get('reusedScenes',[])
    pins={r['sceneId']:r for r in reused if r['sceneId'] in OTHERS}
    assert set(pins)==set(OTHERS),'Only S03 may change; all five others require old-evidence reuse proof'
    for sid,row in pins.items():
        actual=voice.wav_info(output/'chunks'/f'{sid}-scene.wav')
        assert all(actual[k]==row[k] for k in ('sha256','pcmSHA256','sampleRate','frames')),'Unchanged canonical chunk differs: '+sid
    return {sid:dict(sha256=pins[sid]['sha256'],pcmSHA256=pins[sid]['pcmSHA256']) for sid in OTHERS}


def components(base,job):
    path=base/'component-progress.json'
    if not path.exists():return {}
    record=read(path);assert record['fingerprint']==job['fingerprint'] and record['identity']==job['identity']
    rows=record['components']
    assert set(rows)<=set(PARTS)
    for sid,pin in rows.items():
        source=Path(pin['path']).resolve();assert source.is_relative_to(base.resolve())
        actual=voice.wav_info(source)
        assert all(actual[k]==pin[k] for k in ('sha256','pcmSHA256','sampleRate','channels','sampleWidthBytes','frames'))
        assert actual['sampleRate']==24000 and actual['channels']==1 and actual['sampleWidthBytes']==2
    return rows


def subrequest(prov,job,base,missing):
    assert missing and set(missing)<=set(PARTS)
    attempt=base/'attempts'/('generation-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True,exist_ok=False)
    script=attempt/'script.json';manifest=attempt/'manifest.json';generated=attempt/'generated'
    mapping=dict(zip(PARTS,job['lines']))
    save(script,dict(scenes=[dict(id=sid,title='S03 semantic take '+sid[-1],lines=[mapping[sid]]) for sid in PARTS if sid in missing]))
    document=copy.deepcopy(read(voice.MANIFEST));document['paths']['script']=script.relative_to(ROOT).as_posix()
    document['tts']['outputDir']=generated.relative_to(ROOT).as_posix()
    assert document['tts']['renderMode']=='scene'  # Two distinct IDs, never two lines grouped back into one take.
    save(manifest,document)
    assert voice.sha(voice.ENGINE)==prov['audit']['engineSHA256'],'Shared engine changed before scoped component request'
    save(attempt/'request.json',dict(fingerprint=job['fingerprint'],identity=job['identity'],missing=missing,
        scriptSHA256=voice.sha(script),manifestSHA256=voice.sha(manifest),engineSHA256=voice.sha(voice.ENGINE),
        scriptPath=str(script),manifestPath=str(manifest),generatedDir=str(generated),
        nestedAggregateAdopted=False,otherFiveCanonicalWavsWritable=False))
    return attempt,manifest,generated


def capture_completed_components(base,job,generated,missing):
    records=components(base,job)
    for sid in missing:
        path=generated/'chunks'/f'{sid}-scene.wav'
        if not path.exists():continue
        actual=voice.wav_info(path)
        assert (actual['sampleRate'],actual['channels'],actual['sampleWidthBytes'])==(24000,1,2)
        if sid in records:
            assert all(records[sid][k]==actual[k] for k in ('sha256','pcmSHA256','sampleRate','frames')),'Attempt conflicts with a preserved verified component'
            continue
        records[sid]=dict(actual,spokenText=job['lines'][PARTS.index(sid)],structuralOnly=True,asrReview='pending',humanListening=False)
        # Commit each independently valid WAV before inspecting the next one.
        save(base/'component-progress.json',dict(fingerprint=job['fingerprint'],identity=job['identity'],components=records,
            literalContentVerified=False,automaticSpeechPass=False,humanListening=False))
    return records


def pending_attempt(base,job,attempt):
    request=attempt/'request.json'
    record=dict(protocol=PROTOCOL,fingerprint=job['fingerprint'],identity=job['identity'],requestPath=str(request),
        requestSHA256=voice.sha(request),owner=voice.native.identity(),child=None,phase='prepared-not-launched')
    path=base/'pending-attempt.json';assert not path.exists(),'Previous pending attempt must be recovered or inspected first'
    save(path,record);return record


def recover_pending(base,job):
    path=base/'pending-attempt.json'
    if not path.exists():return components(base,job)
    pending=read(path);assert pending['protocol']==PROTOCOL and pending['fingerprint']==job['fingerprint'] and pending['identity']==job['identity']
    child=pending.get('child');assert isinstance(child,dict) and child.get('pid') and child.get('createTime'),'Unverifiable pending launch; preserve and inspect, never duplicate it'
    if voice.native.alive(child):raise voice.PreparationPending('Previous S03 component child is still alive; preserve it')
    request_path=Path(pending['requestPath']).resolve();assert request_path.is_relative_to((base/'attempts').resolve())
    assert voice.sha(request_path)==pending['requestSHA256'],'Pending request changed; preserve unverified outputs'
    request=read(request_path);assert request['fingerprint']==job['fingerprint'] and request['identity']==job['identity']
    assert request['engineSHA256']==job['identity']['engineSHA256']==voice.sha(voice.ENGINE)
    assert job['identity']['scalarProcessorSHA256']==voice.sha(HERE/'prepare-first-audio.py')
    for field,pin in [('scriptPath','scriptSHA256'),('manifestPath','manifestSHA256')]:
        source=Path(request[field]).resolve();assert source.parent==request_path.parent and voice.sha(source)==request[pin]
    script=read(request['scriptPath']);mapping=dict(zip(PARTS,job['lines']))
    assert [s['id'] for s in script['scenes']]==request['missing'] and set(request['missing'])<=set(PARTS)
    assert all(s['lines']==[mapping[s['id']]] for s in script['scenes'])
    manifest=read(request['manifestPath']);generated=Path(request['generatedDir']).resolve()
    assert generated==request_path.parent/'generated' and (ROOT/manifest['tts']['outputDir']).resolve()==generated
    assert (ROOT/manifest['paths']['script']).resolve()==Path(request['scriptPath']).resolve() and manifest['slug']==voice.SLUG
    records=capture_completed_components(base,job,generated,request['missing'])
    save(request_path.parent/'recovered-components.json',dict(fingerprint=job['fingerprint'],requestSHA256=pending['requestSHA256'],
        provenDeadChild=child,registeredComponents=list(records),asrReview='pending',humanListening=False))
    # Preserve the exact launch pointer beside its attempt; never delete history.
    saved=request_path.parent/('resolved-pending-'+uuid.uuid4().hex[:8]+'.json');os.replace(path,saved)
    return records


def new_bytes(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==value,'Different derived output preserved; inspect rather than overwrite';return
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');temp.write_bytes(value)
    assert not path.exists();os.replace(temp,path)


def pcm16_bytes(samples,rate):
    stream=io.BytesIO();sf.write(stream,samples,rate,format='WAV',subtype='PCM_16');return stream.getvalue()


def normalized_copy(path,samples,rate):
    if path.exists():
        actual,sr=sf.read(path,dtype='float32')
        assert sr==rate and np.array_equal(actual,samples),'Existing normalized component differs; preserve and inspect'
        return
    stream=io.BytesIO();sf.write(stream,samples,rate,format='WAV',subtype='FLOAT');new_bytes(path,stream.getvalue())


def join_s03(output,base,job):
    records=components(base,job);assert set(records)==set(PARTS)
    prepared=[];rows=[];position=0
    for sid in PARTS:
        source=records[sid];samples,rate=sf.read(source['path'],dtype='float32');assert rate==24000
        matched,levels=audio.match_paragraph(samples,rate)
        normalized=base/(sid+'-normalized.wav');normalized_copy(normalized,matched,rate)
        start=position;position+=len(samples);prepared.append(matched)
        rows.append(dict(componentId=sid,spokenText=job['lines'][PARTS.index(sid)],raw=source,normalization=levels,
            normalizedPath=str(normalized),normalizedSHA256=voice.sha(normalized),destinationSampleRange=[start,position],
            insertedSamples=0,trimmedSamples=0,rawComponentPreserved=True))
    canonical=output/'chunks/s03-scene.wav';new_bytes(canonical,pcm16_bytes(np.concatenate(prepared),24000))
    actual=voice.wav_info(canonical);assert actual['frames']==position
    report=dict(protocol=PROTOCOL,fingerprint=job['fingerprint'],identity=job['identity'],canonicalScene=actual,
        pcmOrigin='derived from two independently synthesized semantic takes, each uniformly level-matched then PCM16-quantized',
        components=rows,frames=position,sampleRate=24000,insertedSamples=0,trimmedSamples=0,
        oldS03PreservedByVoiceArchive=True,nestedEngineAggregateAdopted=False,sharedEngineChanged=False,
        originalComponentPcmModified=False,canonicalS03IsUnprocessedRaw=False,asrReview='pending',wordAndBodyLevelQA='pending',humanListening=False)
    path=output/'s03-components.json'
    if path.exists():assert read(path)==report
    else:save(path,report)
    return report


def assemble_exact(prov,output,component_report):
    payload=[];entries=[];position=0;rate=24000
    for i,(sid,text) in enumerate(zip(prov['sceneIds'],prov['spokenLines']),1):
        path=output/'chunks'/f'{sid}-scene.wav';info=voice.wav_info(path)
        assert (info['sampleRate'],info['channels'],info['sampleWidthBytes'])==(rate,1,2)
        with wave.open(str(path),'rb') as source:data=source.readframes(info['frames'])
        payload.append(data);start=position;position+=info['frames']
        entries.append(dict(index=i,scene_id=sid,scene_title=sid,text=text,start=start/rate,end=position/rate))
    data=b''.join(payload);stream=io.BytesIO()
    with wave.open(stream,'wb') as target:
        target.setparams((1,2,rate,position,'NONE','not compressed'));target.writeframes(data)
    new_bytes(output/'narration.wav',stream.getvalue())
    timing=dict(sample_rate=rate,duration_seconds=position/rate,render_mode='scene',example_seconds=0.,
        narration_placement='continuous-across-example-and-explanation',entries=entries)
    new_bytes(output/'narration.timing.json',(json.dumps(timing,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    def stamp(seconds):
        n=round(seconds*1000);sec,ms=divmod(n,1000);minute,sec=divmod(sec,60);hour,minute=divmod(minute,60)
        return f'{hour:02}:{minute:02}:{sec:02},{ms:03}'
    text='\n\n'.join(f"{e['index']}\n{stamp(e['start'])} --> {stamp(e['end'])}\n{e['text']}" for e in entries)+'\n'
    new_bytes(output/'narration.srt',text.encode('utf-8'))
    proof=voice.verify_voice(prov);assert proof['aggregateWav']['pcmSHA256']==hashlib.sha256(data).hexdigest()
    proof['sceneWavs'][2].update(pcmOrigin=component_report['pcmOrigin'],derivedComponentReport=str(output/'s03-components.json'),canonicalUnprocessedRaw=False)
    proof['s03LevelRepair']=dict(report=str(output/'s03-components.json'),sha256=voice.sha(output/'s03-components.json'),
        componentSources=[r['raw'] for r in component_report['components']],otherFiveCanonicalPcmUnchanged=True,
        aggregateIsExactCanonicalChunkPcmConcatenation=True,hiddenEdgeFadesApplied=False,asrReview='pending',humanListening=False)
    return proof


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6);args=parser.parse_args()
    if not args.execute:
        try:
            prov=voice.preparation();job=validate(prov);print(json.dumps(dict(ready=True,fingerprint=job['fingerprint'],parts=PARTS,modelStarted=False)))
        except (voice.PreparationPending,AssertionError) as error:print(json.dumps(dict(ready=False,reason=str(error),modelStarted=False)))
        return
    worker=voice.native.SingleWorker(voice.WORKER).acquire();worker.update(stage='voice',stageOwner=PROTOCOL,topicId='03.02')
    child=None;log=None;state=dict(protocol=PROTOCOL,stage='voice',topicId='03.02',**voice.native.identity(),child=None,completed=False,gpuStarted=False)
    try:
        old=read(voice.STATE) if voice.STATE.exists() else {}
        assert not (old.get('pid')!=os.getpid() and (voice.native.alive(old) or voice.native.alive(old.get('child')))),'Prior voice worker/child remains alive'
        assert not voice.same_project_children(),'Existing Qwen child must finish first'
        deadline=time.monotonic()+max(0,args.wait_hours)*3600
        while True:
            try:
                prov=voice.preparation();job=validate(prov);output=voice.prepare_output(prov);pinned=other_pins(prov,output)
                base=output/'subtakes-v3';base.mkdir(parents=True,exist_ok=True)
                records=recover_pending(base,job);missing=[sid for sid in PARTS if sid not in records]
                if missing:
                    reason=voice.native.busy_reason()
                    if reason:raise voice.PreparationPending(reason)
                    assert not voice.same_project_children()
                    if time.monotonic()>=deadline:raise RuntimeError('Finite repair wait ended before launch; other work preserved')
                    attempt,manifest,generated=subrequest(prov,job,base,missing)
                    pending=pending_attempt(base,job,attempt)
                    log_path=attempt/'engine.log';log=log_path.open('ab')
                    command=[str(voice.PYTHON),'-u','-X','utf8',str(voice.ENGINE),'--project',voice.SLUG,'--manifest',manifest.relative_to(ROOT).as_posix(),'--batch-size','1','--device','cuda:0']
                    child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=CREATE)
                    ident=voice.native.identity(child.pid);pending.update(child=ident,phase='launched');save(base/'pending-attempt.json',pending);worker.update(child=ident)
                    state.update(status='s03-components-generating',child=ident,gpuStarted=True,fingerprint=prov['fingerprint'],repairFingerprint=job['fingerprint'],log=str(log_path))
                    save(voice.STATE,state);code=child.wait();log.close();log=None
                    assert validate(voice.preparation())['fingerprint']==job['fingerprint'];assert other_pins(prov,output)==pinned
                    records=recover_pending(base,job)
                    if code!=0:raise RuntimeError('S03-only Qwen child failed; every partial component/attempt remains preserved')
                    assert set(records)==set(PARTS),'Two component WAVs not completed'
                report=join_s03(output,base,job);assert other_pins(prov,output)==pinned
                proof=assemble_exact(prov,output,report);assert other_pins(prov,output)==pinned
                voice.complete_record(proof);state.update(status='voice-generated-review-pending',completed=True,fingerprint=prov['fingerprint'],repairFingerprint=job['fingerprint'],
                    output=str(output),otherFiveUnchanged=pinned,componentReport=str(output/'s03-components.json'),asrReview='pending',humanListening=False)
                break
            except voice.PreparationPending as error:
                state.update(status='waiting-for-preparation-or-resources',reason=str(error),checkedAt=time.time());save(voice.STATE,state)
                if time.monotonic()>=deadline:raise RuntimeError('Finite S03-only repair wait ended; foreign jobs preserved')
                time.sleep(10)
    except BaseException as error:state.update(status='failed-or-resource-blocked',error=repr(error));raise
    finally:
        live=bool(child and child.poll() is None) or voice.native.alive(state.get('child'));state.update(childStillAlive=live,finishedOrYieldedAt=time.time())
        if live:state['status']='voice-worker-yielded-child-still-running'
        save(voice.STATE,state)
        if log:log.close()
        worker.close(remove=not live)  # Engine alone owns/releases its exact GPU guard lease.


if __name__=='__main__':main()
