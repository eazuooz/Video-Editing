"""One guarded, source-locked selected-lesson Qwen job, no automatic retries.

Default is read-only. --execute may wait for resources within the active finite
task, then generate exactly this input once. Existing partial audio is preserved
for review, never silently overwritten. Voice acceptance requires separate QA.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sys,time,wave
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=ROOT/'projects/shorts-journey-sand-sparkle'
COUNT=6
SLUGS=['shorts-journey-sand-sparkle','shorts-horizon-gpu-placement','shorts-inside-temporal-antialiasing','shorts-spiderman-swing-anchor','shorts-control-destruction-pipeline','shorts-returnal-particle-tentacles','shorts-ratchet-dimension-streaming','shorts-doom-push-forward-healing','shorts-botw-chemistry-rules','shorts-mariokart8-spin-boost']
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
BASE=MEDIA/P.name/'voice-v1';LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
PROTOCOL='original-tech-twelve-selected-voice-v1';OWNER='original-tech-twelve-selected-voice'
spec=importlib.util.spec_from_file_location('ot12_selected_voice_native_guard',HERE/'run-camera-native-v1.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
runtime=native.runtime;runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
native.guard.qualifier.BASE=BASE/'resource-observations'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def save(p,d):native.save(p,d)
def inputs():
    native.authority();batch=read(HERE/'batch.json');assert [x['slug'] for x in batch['projects'][2:]]==SLUGS and P.name in SLUGS
    locked=read(P/'planning/narration-locked-v1.json')
    assert locked['narrationLocked'] and locked['approvedForTts'] and len(locked['paragraphs'])==COUNT
    for k in ['sourceDraft','sourceOrderMap','sourceActionReview','nativeModelCpuReview']:
        row=locked[k];assert sha(row['path'])==row['sha256'],k
    action=read(locked['sourceActionReview']['path']);assert action['sourceAndNarrationSemanticsReady']
    for source in action['sourceInputs']:assert sha(source['path'])==source['sha256'],'Source-action pin changed'
    assert read(locked['nativeModelCpuReview']['path'])['staticCompilationPassed'] and read(locked['nativeModelCpuReview']['path'])['modelChecks']>=10
    manifest=P/'production/tts-manifest-v1.json';d=read(manifest)
    approved=read(ROOT/'projects/shorts-mario-one-action/production/local/tts-execution.json')
    for key,path in [('reference',ROOT/d['tts']['reference']),('referenceText',ROOT/d['tts']['referenceText'])]:
        assert sha(path)==approved['inputs'][key],'Approved voice/reference changed'
    assert d['tts']['model']=='qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base'
    assert d['tts']['renderMode']=='scene' and d['tts']['maxRenderAttempts']==1 and d['tts']['edgeFadeSeconds']==0
    sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as engine
    engine.configure_project(P.name,str(manifest.relative_to(ROOT)))
    jobs=engine.load_jobs();items=engine.build_render_items(jobs)
    assert len(jobs)==len(items)==COUNT and [i.text for i in items]==[p['ko'] for p in locked['paragraphs']]
    assert not engine.narration_lead_seconds() and engine.FADE_SECONDS==0
    paths=[P/'planning/narration-locked-v1.json',manifest,engine.SCRIPT_PATH,engine.REFERENCE,engine.REFERENCE_TEXT_PATH,ROOT/'qwen3-tts/render_narration.py',Path(__file__)]
    identity=dict(slug=P.name,sourceInputs=[pin(p)for p in paths],spoken=[i.text for i in items],allocatorLimitMiB=7168,
        noGainSpeedTrimOrCompression=True,paragraphGapSeconds=engine.SCENE_GAP_SECONDS,internalSubtitleInterpolationAdopted=False)
    return engine,jobs,items,dict(fingerprint=native.digest(identity),identity=identity)
def wav(p):
    with wave.open(str(p),'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())==(1,2,24000,'NONE')
        frames=w.getnframes();assert frames>0;pcm=w.readframes(frames);assert len(pcm)==frames*2
    return dict(**pin(p),frames=frames,rate=24000,duration=frames/24000,pcmSHA256=hashlib.sha256(pcm).hexdigest())
def execute(wait_minutes):
    engine,jobs,items,prepared=inputs();proof_path=BASE/'voice-generation-complete-proof.json'
    if proof_path.exists():
        proof=read(proof_path);assert proof['fingerprint']==prepared['fingerprint']
        for item in proof['rawChunks']+[proof['canonical']]:assert sha(item['path'])==item['sha256']
        return dict(reusedExisting=True,proof=pin(proof_path))
    assert not any(i.path.exists() for i in items),'Existing partial source audio preserved; inspect before a separate repair version'
    worker=runtime.SingleWorker(path=BASE/'worker.json');owned=None
    try:
        worker.acquire();deadline=time.monotonic()+max(0,wait_minutes)*60;last=None
        while True:
            assert inputs()[3]['fingerprint']==prepared['fingerprint'],'Source changed while waiting'
            reason=native.busy()
            if reason is None:
                token=worker.record['token'];record=dict(protocol=PROTOCOL,owner=OWNER,token=token,**native.identity(),phase='reserved',child=None,fingerprint=prepared['fingerprint'],output=str(engine.OUTPUT_DIR))
                try:
                    with LEASE.open('x',encoding='utf8') as h:json.dump(record,h)
                except FileExistsError:reason='Concurrent foreign GPU lease preserved'
                else:
                    owned=token;reason=native.busy(token)
                    if reason:
                        current=read(LEASE)
                        if current.get('token')==owned and current.get('protocol')==PROTOCOL:LEASE.unlink()
                        owned=None
                    else:break
            status=dict(status='finite-source-locked-voice-resource-wait',protocol=PROTOCOL,**native.identity(),reason=reason,fingerprint=prepared['fingerprint'],modelStarted=False,updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
            save(BASE/'status.json',status)
            if reason!=last:print(json.dumps(status,ensure_ascii=False),flush=True);last=reason
            if time.monotonic()>=deadline:return dict(started=False,reason=reason,boundedWaitExpired=True)
            time.sleep(min(30,max(0,deadline-time.monotonic())))
        assert not any(i.path.exists() for i in items)
        save(BASE/'voice-input-proof.json',prepared)
        save(BASE/'status.json',dict(status='qwen-generating-selected-paragraphs',protocol=PROTOCOL,**native.identity(),fingerprint=prepared['fingerprint'],modelStarted=True,voiceAcceptedForFilm=False))
        print(json.dumps(dict(started=True,fingerprint=prepared['fingerprint'],paragraphs=COUNT,output=str(engine.OUTPUT_DIR))),flush=True)
        import torch
        torch.set_num_threads(4);torch.set_num_interop_threads(2)
        torch.cuda.set_per_process_memory_fraction(7168*1048576/torch.cuda.get_device_properties(0).total_memory,0)
        engine.INFERENCE_DEVICE='cuda:0';engine.load_tts_dependencies();engine.render_chunks(items,1)
        raw=[wav(i.path) for i in items]
        # Copy the generated PCM bytes, avoiding the legacy assembler's
        # function-default edge fade. One explicit paragraph gap is retained.
        pieces=[];entries=[];position=0;gap=round(engine.SCENE_GAP_SECONDS*24000)
        for i,(item,raw_row) in enumerate(zip(items,raw)):
            with wave.open(str(item.path),'rb') as source: data=source.readframes(source.getnframes())
            pieces.append(data);entries.append(dict(index=i+1,scene_id=item.key.split('-')[0],text=item.text,start=position/24000,end=(position+raw_row['frames'])/24000));position+=raw_row['frames']
            if i+1<len(items):pieces.append(bytes(gap*2));position+=gap
        with wave.open(str(engine.FINAL_WAV),'wb') as out:out.setnchannels(1);out.setsampwidth(2);out.setframerate(24000);out.writeframes(b''.join(pieces))
        save(engine.TIMING_JSON,dict(sample_rate=24000,duration_seconds=position/24000,entries=entries,assembly='byte-exact raw PCM16 plus explicit paragraph gap'))
        engine.FINAL_SRT.write_text('\n\n'.join(f"{e['index']}\n{engine.timestamp(e['start'])} --> {engine.timestamp(e['end'])}\n{e['text']}" for e in entries)+'\n',encoding='utf8')
        canonical=wav(engine.FINAL_WAV)
        assert canonical['pcmSHA256']==hashlib.sha256(b''.join(pieces)).hexdigest()
        # The engine writes actual paragraph ranges because each scene has one
        # line. Its unreviewed SRT is never an accepted final caption source.
        timing=read(engine.TIMING_JSON);assert len(timing['entries'])==COUNT
        for a,b in zip(raw,timing['entries']):assert abs((b['end']-b['start'])-a['duration'])<.0001
        proof=dict(**prepared,rawChunks=raw,canonical=canonical,paragraphTiming=pin(engine.TIMING_JSON),
            generatedSrt=pin(engine.FINAL_SRT),peakAllocatedMiB=torch.cuda.max_memory_allocated()/1048576,
            peakReservedMiB=torch.cuda.max_memory_reserved()/1048576,modelCompleted=True,voiceAcceptedForFilm=False,
            blindAsrReviewed=False,wholeWordBoundariesReviewed=False,levelTrendReviewed=False,
            actualListening=False,humanApproval=False,finalFilmComplete=False)
        save(proof_path,proof);save(BASE/'status.json',dict(status='voice-generated-independent-content-and-level-QA-pending',fingerprint=prepared['fingerprint'],proof=pin(proof_path),modelCompleted=True,voiceAcceptedForFilm=False))
        return dict(started=True,completed=True,proof=pin(proof_path),duration=canonical['duration'],voiceAcceptedForFilm=False)
    finally:
        if owned and LEASE.exists():
            current=read(LEASE)
            if current.get('protocol')==PROTOCOL and current.get('owner')==OWNER and current.get('token')==owned:LEASE.unlink()
        if worker.handle is not None:worker.close()
def main():
    global P,BASE,COUNT,PROTOCOL,OWNER
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',choices=SLUGS,required=True);p.add_argument('--execute',action='store_true');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();assert 0<=a.wait_minutes<=180
    P=ROOT/'projects'/a.project;BASE=MEDIA/P.name/'voice-v1';COUNT=len(read(P/'planning/narration-locked-v1.json')['paragraphs']);assert 5<=COUNT<=7
    PROTOCOL='original-tech-twelve-'+P.name+'-voice-v1';OWNER='original-tech-twelve-'+P.name+'-voice';runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER;native.guard.qualifier.BASE=BASE/'resource-observations'
    if a.execute:result=execute(a.wait_minutes)
    else:
        engine,jobs,items,prepared=inputs();result=dict(sourceReady=True,paragraphs=len(items),fingerprint=prepared['fingerprint'],guardReason=native.busy(),modelStarted=False,leaseMutated=False)
    print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
