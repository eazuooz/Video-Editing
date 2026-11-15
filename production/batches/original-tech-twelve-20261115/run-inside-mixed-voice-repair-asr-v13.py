"""Blind word ASR and unchanged numerical level review of the exact new lock-on voice.

Default reads bindings. --execute runs one finite guarded job; model failures
are preserved, not retried. --levels only reads completed ASR and original PCM.
"""
from pathlib import Path
import argparse,ast,datetime,difflib,hashlib,importlib.util,json,os,re,subprocess,sys,time,wave
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
native=module('ot12_asr_native_guard',HERE/'run-camera-native-v1.py')
read,sha,pin,save,digest=native.read,native.sha,native.pin,native.save,native.digest
PROTOCOL='original-tech-twelve-camera-mixed-asr-v5';OWNER='original-tech-twelve-camera-asr'
P=ROOT/'projects/shorts-journey-sand-sparkle';BASE=native.MEDIA/P.name/'mixed-asr-v13';BOOTSTRAP_PINS={}
LEASE=native.LEASE;runtime=native.runtime;runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
native.guard.qualifier.BASE=BASE/'resource-observations'
LEGACY=ROOT/'production/batches/architectural-111-20261106'
approved_tree=ast.parse((LEGACY/'run-selected-voice-qa.py').read_text(encoding='utf-8-sig'))
APPROVED=next(ast.literal_eval(x.value)for x in approved_tree.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='APPROVED'for t in x.targets))
TRUSTED=ROOT/APPROVED['trusted'];MODEL=Path(APPROVED['model']);LEVEL=LEGACY/'first-level-continuity-review.py'
def pcm(path,a=0,b=None):
    # Recognizer-only projection. The produced stereo float mix is preserved.
    import soundfile as sf,numpy as np
    x,rate=sf.read(str(path),dtype='float32',always_2d=True);assert rate==24000 and x.shape[1]==2
    end=len(x)if b is None else b;assert 0<=a<end<=len(x)
    mono=x[a:end].mean(axis=1);assert np.isfinite(mono).all() and np.max(np.abs(mono))<1
    return np.rint(mono*32767).astype('<i2').tobytes()

def immutable(p,d):
    if p.exists():assert read(p)==d,'Existing immutable evidence differs: '+str(p)
    else:save(p,d)
def prepare():
    native.authority();selection=read(P/'production/accepted-voice-selection-v10.json');mixpath=ROOT/'shared/output/original-tech-twelve-20261115'/P.name/'audio-mix-v13/audio-build.json'
    if not mixpath.exists():return None
    mix=read(mixpath);assert mix['bodyOnly'] and mix['voiceOffsetSamples']==0 and mix['voiceGain']==1 and not mix['voiceDsp'] and not mix['knownStemResidual']['exceedsKnownStemTolerance']
    assert sha(mix['mix']['path'])==mix['mix']['sha256']
    voicepath=Path(selection['voice']['path']);assert pin(voicepath)==selection['voice'];voice=read(voicepath);assert mix['identity']['voice']==pin(voicepath)
    locked=Path(selection['narration']['path']);assert pin(locked)==selection['narration'];narration=read(locked)
    assert sha(TRUSTED)==APPROVED['trustedSHA256'] and sha(LEVEL)==APPROVED['firstLevelPrimitiveSHA256']
    for row in mix['identity'].values():
        if isinstance(row,dict)and 'path'in row and 'sha256'in row:assert sha(row['path'])==row['sha256']
    entries=read(voice['paragraphTiming']['path'])['entries'];tasks=[]
    for e,p in zip(entries,narration['paragraphs']):
        assert e['id']==p['id'] and e['text']==p['ko']
        tasks.append(dict(key='take-'+p['id'],kind='take',paragraph=p['id'],path=mix['mix']['path'],sha256=mix['mix']['sha256'],startSample=e['startSample'],endSample=e['endSample'],offsetSample=e['startSample'],expected=p['ko']))
    isolated=list(tasks)
    for left,right in zip(isolated,isolated[1:]):
        k=right['offsetSample'];a=max(0,k-4*24000);b=min(mix['frames'],k+4*24000)
        tasks.append(dict(key='join-'+left['paragraph']+'-'+right['paragraph'],kind='join',path=mix['mix']['path'],sha256=mix['mix']['sha256'],startSample=a,endSample=b,offsetSample=a,boundarySample=k))
    assert len(tasks)==2*len(entries)-1
    identity=dict(protocol=PROTOCOL,adapter=pin(__file__),mixProof=pin(mixpath),voiceProof=pin(voicepath),lockedNarration=pin(locked),trusted=pin(TRUSTED),modelPins=APPROVED['modelPins'],profile=APPROVED['profile'],recognizerProjection='stereoFloat24k mean to mono int16 only for ASR; production mix is unmodified',tasks=tasks)
    fp=digest(identity);return dict(fingerprint=fp,identity=identity,output=str(BASE/fp[:24]))

def busy(token=None):
    reason=native.busy(token)
    if reason:return reason
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=native.CREATE)
    free,use=map(int,raw.splitlines()[0].replace(' ','').split(','))
    return 'ASR requires9216MiB and utilization below15%'if free<9216 or use>=15 else None
def execute(wait_minutes):
    worker=runtime.SingleWorker(path=BASE/'worker.json');owned=None;started=False
    try:
        worker.acquire();argv=native.guard.psutil.Process().cmdline();worker.update(project=P.name,stage='targeted-source',argv=argv,commandSHA256=native.digest(argv),**BOOTSTRAP_PINS);deadline=time.monotonic()+wait_minutes*60;last=None
        while True:
            job=prepare();reason='Exact accepted-voice mix is not complete'if job is None else busy()
            if job is not None:
                folder=Path(job['output']);review=folder/'review.json'
                if review.exists():assert read(review)['fingerprint']==job['fingerprint'];return dict(reusedExisting=True,review=pin(review))
                assert not(folder/'model-failure.json').exists(),'Prior failure preserved; inspect before any repair'
                assert not list(folder.glob('take-*.json'))and not list(folder.glob('join-*.json')),'Partial ASR results preserved; review before resuming'
            if reason is None:
                token=worker.record['token']
                try:
                    with LEASE.open('x',encoding='utf8')as h:json.dump(dict(protocol=PROTOCOL,owner=OWNER,token=token,**native.identity(),phase='reserved',fingerprint=job['fingerprint']),h)
                except FileExistsError:reason='Concurrent foreign lease preserved'
                else:
                    owned=token;reason=busy(token)
                    if reason:
                        if read(LEASE).get('token')==owned:LEASE.unlink()
                        owned=None
                    else:break
            state=dict(status='finite-voice-ASR-resource-wait',reason=reason,modelStarted=False,**native.identity(),updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(BASE/'status.json',state)
            if reason!=last:print(json.dumps(state),flush=True);last=reason
            if time.monotonic()>=deadline:return dict(started=False,reason=reason,boundedWaitExpired=True)
            time.sleep(min(30,max(0,deadline-time.monotonic())))
        assert prepare()['fingerprint']==job['fingerprint']
        # Hash the complete previously approved local model before loading it.
        for model in APPROVED['modelPins']:assert sha(MODEL/model['path'])==model['sha256']
        folder=Path(job['output']);immutable(folder/'job.json',job)
        os.environ.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
        trusted=module('ot12_approved_blind_recognizer',TRUSTED);assert trusted.MODEL==MODEL
        started=True;save(BASE/'status.json',dict(status='blind-ASR-running',fingerprint=job['fingerprint'],modelStarted=True,**native.identity()))
        pipe=trusted.load_recognizer('cuda');import numpy as np
        results=[]
        for task in job['identity']['tasks']:
            assert sha(task['path'])==task['sha256'];samples=np.frombuffer(pcm(task['path'],task['startSample'],task['endSample']),dtype='<i2').astype(np.float32)/32768
            raw=trusted.recognize(pipe,samples,24000);record=dict(fingerprint=job['fingerprint'],task=task,rawRecognition=raw,expectedPrompt=None,humanListening=False)
            immutable(folder/(task['key']+'.json'),record);results.append(record);print('Recognized '+task['key'],flush=True)
        review=dict(fingerprint=job['fingerprint'],job=pin(folder/'job.json'),results=results,wordTimestamps=True,automaticSpeechPass=False,humanListening=False,voiceAcceptedForFilm=False)
        immutable(folder/'review.json',review);save(BASE/'status.json',dict(status='blind-ASR-complete-content-and-level-review-pending',review=pin(folder/'review.json'),modelCompleted=True));return dict(completed=True,review=pin(folder/'review.json'))
    except Exception as e:
        if started:save(Path(job['output'])/'model-failure.json',dict(error=type(e).__name__,message=str(e),fingerprint=job['fingerprint'],resultsPreserved=True))
        raise
    finally:
        if owned and LEASE.exists():
            d=read(LEASE)
            if d.get('protocol')==PROTOCOL and d.get('token')==owned:LEASE.unlink()
        if worker.handle is not None:worker.close()
def main():
    global P,BASE,PROTOCOL,OWNER,BOOTSTRAP_PINS
    p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--execute',action='store_true');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();assert a.project=='shorts-inside-temporal-antialiasing';assert 0<=a.wait_minutes<=180
    P=ROOT/'projects'/a.project;BASE=native.MEDIA/P.name/'mixed-asr-v13';PROTOCOL='original-tech-twelve-'+P.name+'-mixed-asr-v13';OWNER='original-tech-twelve-'+P.name+'-mixed-asr';runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER;native.guard.qualifier.BASE=BASE/'resource-observations'
    if a.execute:
        assert a.wait_minutes==15;bootstrap=module('own_mixed_asr_bootstrap',HERE/'bootstrap-parent-identity-v1.py');BOOTSTRAP_PINS=bootstrap.install(native,__file__,P.name,BASE,PROTOCOL,OWNER);result=execute(a.wait_minutes)
    else:
        job=prepare();result=dict(sourceReady=job is not None,fingerprint=None if job is None else job['fingerprint'],guardReason=busy(),modelStarted=False)
    print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
