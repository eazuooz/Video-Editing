"""Blind word ASR and unchanged numerical level review of the exact selected original-tech lesson voice.

Default reads bindings. --execute runs one finite guarded job; model failures
are preserved, not retried. --levels only reads completed ASR and original PCM.
"""
from pathlib import Path
import argparse,ast,datetime,difflib,hashlib,importlib.util,json,os,re,subprocess,sys,time,wave
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
native=module('ot12_selected_asr_native_guard',HERE/'run-camera-native-v1.py')
P=native.PROJECT
read,sha,pin,save,digest=native.read,native.sha,native.pin,native.save,native.digest
PROTOCOL='original-tech-twelve-selected-master-asr-v110';OWNER='original-tech-twelve-camera-asr'
BASE=native.MEDIA/native.PROJECT.name/'asr-master-v110';VOICE=BASE.parent/'voice-master-v110/voice-generation-complete-proof.json'
SLUGS=['shorts-journey-sand-sparkle', 'shorts-inside-temporal-antialiasing', 'shorts-spiderman-swing-anchor', 'shorts-control-destruction-pipeline', 'shorts-returnal-particle-tentacles', 'shorts-doom-push-forward-healing', 'shorts-botw-chemistry-rules', 'shorts-mariokart8-spin-boost']
COUNT=0
LEASE=native.LEASE;runtime=native.runtime;runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER
native.guard.qualifier.BASE=BASE/'resource-observations'
LEGACY=ROOT/'production/batches/architectural-111-20261106'
approved_tree=ast.parse((LEGACY/'run-selected-voice-qa.py').read_text(encoding='utf-8-sig'))
APPROVED=next(ast.literal_eval(x.value)for x in approved_tree.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='APPROVED'for t in x.targets))
TRUSTED=ROOT/APPROVED['trusted'];MODEL=Path(APPROVED['model']);LEVEL=LEGACY/'first-level-continuity-review.py'
_policy_spec=importlib.util.spec_from_file_location('exact12_cooperative_policy',HERE/'cooperative-resource-policy-v19.py');_policy=importlib.util.module_from_spec(_policy_spec);_policy_spec.loader.exec_module(_policy);_policy.install(native)

def pcm(path,a=0,b=None):
    with wave.open(str(path),'rb')as w:
        assert(w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())==(1,2,24000,'NONE')
        end=w.getnframes()if b is None else b;assert 0<=a<end<=w.getnframes();w.setpos(a);data=w.readframes(end-a);assert len(data)==(end-a)*2;return data
def immutable(p,d):
    if p.exists():assert read(p)==d,'Existing immutable evidence differs: '+str(p)
    else:save(p,d)
def prepare():
    batch=native.authority();assert P.name in SLUGS and P.name in[x['slug']for x in batch['projects']]
    if not VOICE.exists():return None
    proof=read(VOICE);locked=P/'planning/narration-master-v110.json';narration=read(locked)
    assert proof['identity']['slug']==P.name
    assert proof['modelCompleted'] and len(proof['rawChunks'])==len(narration['units'])==COUNT
    assert sha(TRUSTED)==APPROVED['trustedSHA256'] and sha(LEVEL)==APPROVED['firstLevelPrimitiveSHA256']
    for p in proof['identity']['sourceInputs']:assert sha(p['path'])==p['sha256']
    canon=proof['canonical'];assert sha(canon['path'])==canon['sha256'];data=pcm(canon['path']);assert hashlib.sha256(data).hexdigest()==canon['pcmSHA256']
    assert sha(proof['unitTiming']['path'])==proof['unitTiming']['sha256']
    assert sha(proof['paragraphTiming']['path'])==proof['paragraphTiming']['sha256']
    entries=read(proof['unitTiming']['path'])['entries'];tasks=[];position=0;gap=round(proof['identity']['unitGapSeconds']*24000)
    for i,(raw,e,u)in enumerate(zip(proof['rawChunks'],entries,narration['units'])):
        assert sha(raw['path'])==raw['sha256'];chunk=pcm(raw['path']);assert hashlib.sha256(chunk).hexdigest()==raw['pcmSHA256']
        assert e['text']==u['ko'] and abs(e['start']-position/24000)<.0001 and data[2*position:2*(position+raw['frames'])]==chunk
        tasks.append(dict(key='unit-'+u['id'],kind='unit',unit=u['id'],paragraph=u['paragraph'],path=raw['path'],sha256=raw['sha256'],startSample=0,endSample=raw['frames'],offsetSample=position,expected=e['text']))
        position+=raw['frames']
        if i<COUNT-1:assert data[2*position:2*(position+gap)]==bytes(gap*2);position+=gap
    assert position==canon['frames']
    isolated=list(tasks)
    for left,right in zip(isolated,isolated[1:]):
        k=right['offsetSample'];a=max(0,k-4*24000);b=min(position,k+4*24000)
        tasks.append(dict(key='join-'+left['unit']+'-'+right['unit'],kind='join',path=canon['path'],sha256=canon['sha256'],startSample=a,endSample=b,offsetSample=a,boundarySample=k))
    for e,p in zip(read(proof['paragraphTiming']['path'])['entries'],narration['paragraphs']):
        assert e['id']==p['id'] and e['text']==p['ko']
        tasks.append(dict(key='paragraph-'+p['id'],kind='paragraph',paragraph=p['id'],path=canon['path'],sha256=canon['sha256'],startSample=e['startSample'],endSample=e['endSample'],offsetSample=e['startSample'],expected=e['text']))
    assert len(tasks)==2*COUNT-1+len(narration['paragraphs'])
    identity=dict(executionResourcePolicy=native.cooperative_policy_proof,protocol=PROTOCOL,adapter=pin(__file__),bootstrap=pin(HERE/'bootstrap-parent-identity-v1.py'),voiceProof=pin(VOICE),lockedNarration=pin(locked),trusted=pin(TRUSTED),modelPins=APPROVED['modelPins'],profile=APPROVED['profile'],tasks=tasks)
    fp=digest(identity);return dict(fingerprint=fp,identity=identity,output=str(BASE/fp[:24]))
def busy(token=None):
    reason=native.busy(token)
    if reason:return reason
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=native.CREATE)
    free,use=map(int,raw.splitlines()[0].replace(' ','').split(','))
    return 'ASR requires9216MiB and utilization below35%'if free<9216 or use>=35 else None
def execute(wait_minutes):
    worker=runtime.SingleWorker(path=BASE/'worker.json');owned=None;started=False
    try:
        worker.acquire();own_argv=native.guard.psutil.Process().cmdline();worker.update(project=P.name,stage='targeted-source',argv=own_argv,commandSHA256=native.digest(own_argv),**BOOTSTRAP_PINS);deadline=time.monotonic()+wait_minutes*60;last=None
        while True:
            job=prepare();reason='Exact selected-lesson voice is not complete'if job is None else busy()
            if job is not None:
                folder=Path(job['output']);review=folder/'review.json'
                if review.exists():assert read(review)['fingerprint']==job['fingerprint'];return dict(reusedExisting=True,review=pin(review))
                assert not(folder/'model-failure.json').exists(),'Prior failure preserved; inspect before any repair'
                assert not any(list(folder.glob(pattern))for pattern in ['unit-*.json','paragraph-*.json','join-*.json']),'Partial ASR results preserved; review before resuming'
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
def levels(job):
    import numpy as np
    folder=Path(job['output']);review=read(folder/'review.json');assert review['fingerprint']==job['fingerprint'];mathqa=module('ot12_unchanged_level_primitives',LEVEL);rows=[];flags=[]
    for record in review['results']:
        task=record['task']
        if task['kind'] not in ['unit','paragraph']:continue
        samples=np.frombuffer(pcm(task['path'],task['startSample'],task['endSample']),dtype='<i2').astype(np.float32)/32768;words=[];invalid=[]
        for w in record['rawRecognition'].get('chunks',[]):
            a,b=w['timestamp']
            if a is None or b is None or not 0<=a<b<=len(samples)/24000:invalid.append(w);continue
            x,y=mathqa.sample_window(a,b,24000)
            words.append(dict(text=w['text'],startSeconds=a,endSeconds=b,durationSeconds=b-a,levels=dict(raw=mathqa.levels(samples[x:min(y,len(samples))],24000))))
        trend=mathqa.trend(words,'raw');row=dict(key=task['key'],kind=task['kind'],paragraph=task['paragraph'],expected=task['expected'],recognized=record['rawRecognition']['text'],words=words,invalidWords=invalid,trend=trend,wholeTake=mathqa.levels(samples,24000))
        if trend['suspect']:flags.append(dict(kind='sustained-word-body-decline',taskKey=task['key'],paragraph=task['paragraph'],trend=trend))
        if invalid:flags.append(dict(kind='invalid-whole-word-boundaries',taskKey=task['key'],paragraph=task['paragraph'],words=invalid))
        rows.append(row)
    result=dict(fingerprint=job['fingerprint'],asrReview=pin(folder/'review.json'),levelPrimitive=pin(LEVEL),policy=mathqa.POLICY,paragraphs=rows,flags=flags,pcmModified=False,actualListening=False,humanApproval=False,automaticSpeechPass=False)
    immutable(folder/'levels.json',result);return pin(folder/'levels.json')
def main():
    global P,COUNT,BASE,VOICE,PROTOCOL,OWNER
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',choices=SLUGS,required=True);p.add_argument('--execute',action='store_true');p.add_argument('--levels',action='store_true');p.add_argument('--wait-minutes',type=float,default=0);a=p.parse_args();assert 0<=a.wait_minutes<=180 and not(a.execute and a.levels)
    P=ROOT/'projects'/a.project;BASE=native.MEDIA/a.project/'asr-master-v110';VOICE=BASE.parent/'voice-master-v110/voice-generation-complete-proof.json';COUNT=len(read(P/'planning/narration-master-v110.json')['units']);assert 5<=COUNT<=40
    PROTOCOL='original-tech-twelve-'+a.project+'-master-asr-v110';OWNER='original-tech-twelve-'+a.project+'-sentence-asr';runtime.PROTOCOL=PROTOCOL;runtime.OWNER=OWNER;native.guard.qualifier.BASE=BASE/'resource-observations'
    global BOOTSTRAP_PINS
    if a.execute:
        assert a.wait_minutes==15,'Exact reviewed15-minute bootstrap command required'
        bootstrap=module('ot12_targeted_asr_bootstrap',HERE/'bootstrap-parent-identity-v1.py');BOOTSTRAP_PINS=bootstrap.install(native,__file__,P.name,BASE,PROTOCOL,OWNER)
        result=execute(a.wait_minutes)
    else:
        job=prepare()
        if a.levels:assert job is not None;result=levels(job)
        else:result=dict(sourceReady=job is not None,fingerprint=None if job is None else job['fingerprint'],guardReason=busy(),modelStarted=False)
    print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
