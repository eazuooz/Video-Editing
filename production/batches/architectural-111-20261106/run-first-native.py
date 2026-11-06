"""One recoverable tunnel capture. CPU recovery precedes resource acquisition."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, os, shutil, subprocess, time, uuid
from pathlib import Path
import psutil
from initialize import HERE, ROOT, MEDIA, AUTH_KEY, read, save

PROTOCOL='architectural111-first-native-v2'
OWNER='architectural-111-first-native'
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
STATE=MEDIA/'first-native-progress.json'
WORKER=MEDIA/'first-native-worker.json'
PROJECT=MEDIA/'unity-capture'
TOPIC_MEDIA=MEDIA/'shorts-leveldesign-03-02'
OUTPUT=TOPIC_MEDIA/'native-v1'
ATTEMPTS=TOPIC_MEDIA/'native-attempts'
EDITOR='C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe'
CONTRACT=dict(frames=270,width=1920,height=1080,fps=60,cameras=['observer','top'],modes=['narrow','wide'])
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def identity(pid=None):
    p=psutil.Process(os.getpid() if pid is None else pid)
    return dict(pid=p.pid,createTime=p.create_time())


def alive(record):
    # Missing identity is not proof that an existing PID is dead.
    if not record:return False
    try:
        p=psutil.Process(record['pid'])
        return 'createTime' not in record or abs(p.create_time()-record['createTime'])<.05
    except psutil.NoSuchProcess:return False
    except (psutil.AccessDenied,KeyError,TypeError):return True


def ours(record):
    return (isinstance(record,dict) and record.get('protocol')==PROTOCOL and record.get('owner')==OWNER
            and isinstance(record.get('token'),str) and bool(record['token']))


def archive(path,token):
    dest=path.parent/'native-recovery-history'/f'{path.name}.{token}.{uuid.uuid4().hex}.json'
    dest.parent.mkdir(parents=True,exist_ok=True);os.replace(path,dest);return dest


class SingleWorker:
    """Kernel guard closes both initial-start and stale-file-reclamation races."""
    def __init__(self,path=WORKER,is_alive=alive):
        self.path=Path(path);self.is_alive=is_alive;self.handle=None;self.record=None;self.previous=None

    def acquire(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.handle=self.path.with_suffix('.guard').open('a+b')
        if self.handle.seek(0,2)==0:self.handle.write(b'0');self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.handle.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            self.handle.close();self.handle=None
            raise RuntimeError('Another finite native worker holds the singleton lock')
        try:
            if self.path.exists():
                old=read(self.path)
                if not ours(old) or self.is_alive(old) or self.is_alive(old.get('child')):
                    raise RuntimeError('Preserve existing worker or its live/unknown child')
                self.previous=old;archive(self.path,old['token'])
            self.record=dict(protocol=PROTOCOL,owner=OWNER,token=uuid.uuid4().hex,**identity(),child=None)
            save(self.path,self.record);return self
        except BaseException:
            self.close(remove=False);raise

    def update(self,**fields):
        self.record.update(fields);save(self.path,self.record)

    def close(self,remove=True):
        if self.handle is None:return
        try:
            if remove and self.record and not self.is_alive(self.record.get('child')) and self.path.exists():
                rec=read(self.path)
                if ours(rec) and rec['token']==self.record['token']:self.path.unlink()
        finally:self.handle.close();self.handle=None


def fingerprint(pins,version):
    value=dict(protocol=PROTOCOL,sourcePins=pins,unityVersion=version,contract=CONTRACT,topicId='03.02')
    value['fingerprint']=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return value


def authorize():
    control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
    assert control['userEvidence']=='111개 전체 제작 들어가줘'
    assert control['status'] not in ('paused','cancelled','stopped')
    assert control['automaticAdvanceWithinExactList'] and not control['automaticAdvanceOutsideList']
    assert control['humanFinalReviewRequired'] and not control['youtubeAuthorized']
    batch=read(HERE/'batch.json');assert batch['localFinalReviewOnly'] and len(batch['projects'])==111
    assert sha(ROOT/batch['sourceCatalog'])==batch['sourceCatalogSHA256']
    assert any(r['topicId']=='03.02' and r['slug']=='shorts-leveldesign-03-02' for r in batch['projects'])
    prep=read(HERE/'first-unity-preparation.json');pins=[]
    for item in prep['files']:
        assert sha(ROOT/item['source'])==item['sha256'],'Original input changed; reprepare and audit'
        # Import can reserialize staged .meta; original metadata provenance remains pinned.
        if not item['target'].endswith('.meta'):
            assert sha(PROJECT/item['target'])==item['sha256'],'Staged production input changed'
        pins.append({k:item[k] for k in ('source','target','sha256')})
    report=read(HERE/'first-unity-compiler-preflight.json');assert report['compilerExitCode']==0
    for name,expected in report['sourceHashes'].items():assert sha(HERE/name)==expected
    return fingerprint(sorted(pins,key=lambda p:p['source']),prep['editorVersion'])


def unrecorded_child_alive(rec):
    # A worker can die between Popen and recording child identity. Inspect only this
    # exact attempt's Unity command, never infer ownership from a generic Unity PID.
    if rec.get('phase')!='launching' or rec.get('child'):return False
    for p in psutil.process_iter(['name','cmdline']):
        try:
            if (p.info['name'] or '').lower()!='unity.exe':continue
            args=p.info['cmdline'] or []
            if not args:return True
            if rec.get('fingerprint') in args and str(rec.get('output')) in args:return True
        except psutil.NoSuchProcess:continue
        except psutil.AccessDenied:return True
    return False


def recover_own_lease(known_tokens,lease=None,is_alive=alive,unrecorded=unrecorded_child_alive):
    lease=LEASE if lease is None else Path(lease)
    if not lease.exists():return False
    try:rec=read(lease)
    except (OSError,ValueError):return False
    if not ours(rec) or rec['token'] not in known_tokens:return False
    if 'pid' not in rec or 'createTime' not in rec or rec.get('phase') not in ('reserved','launching','running'):return False
    if rec.get('phase')=='running' and not rec.get('child'):return False
    if is_alive(rec) or is_alive(rec.get('child')) or unrecorded(rec):return False
    archive(lease,rec['token']);return True


def busy_reason(own_token=None):
    if LEASE.exists():
        try:rec=read(LEASE)
        except (OSError,ValueError):return 'Uninspected GPU lease preserved'
        if not (own_token and ours(rec) and rec['token']==own_token):return 'Another scoped job holds the shared GPU lease'
    for p in psutil.process_iter(['pid','name','exe','cmdline']):
        try:
            i=p.info;name=(i['name'] or '').lower();exe=(i['exe'] or '').replace('\\','/').lower();args=[s.lower() for s in i['cmdline'] or []]
            if p.pid==os.getpid():continue
            if '/steamapps/common/' in exe or name in ('overwatch.exe','d2r.exe'):return 'User game is running; do not use GPU'
            if name=='unity.exe':
                if 'unity hub' in exe and 'serve' in args:continue
                return 'Another Unity editor or batch worker is running'
            if name=='unrealeditor.exe':return 'Another Unreal editor is running'
            if name.startswith('python') and any(k in ' '.join(args) for k in ('--synthesize','render_narration','faster_whisper','torchrun')):return 'Another model job is running'
            if name=='ffmpeg.exe':return 'Another media job is running'
        except (psutil.NoSuchProcess,psutil.AccessDenied):continue
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=CREATE)
    free,use=map(int,raw.splitlines()[0].split(','))
    return f'GPU headroom insufficient ({free} MiB free, {use}% use)' if free<8192 or use>25 else None


def check_mode(output,mode,fp):
    folder=Path(output)/mode;rec=read(folder/'mode-complete.json')
    expected=dict(fingerprint=fp,mode=mode,**{k:CONTRACT[k] for k in ('frames','width','height','fps','cameras')})
    if any(rec.get(k)!=v for k,v in expected.items()):raise ValueError('Wrong mode receipt/fingerprint')
    with (folder/'trace.csv').open(encoding='utf-8-sig') as f:trace=list(csv.DictReader(f))
    if len(trace)!=270 or [int(r['frame']) for r in trace]!=list(range(270)):raise ValueError('Missing/unordered trace')
    for row in trace:
        if any(not math.isfinite(float(row[k])) for k in ('commandX','commandZ','playerX','playerZ','travelled','playerDiameter')):raise ValueError('Nonfinite trace')
        if abs(float(row['playerDiameter'])-.72)>1e-5:raise ValueError('Wrong capsule')
        if abs(float(row['width'])-({'narrow':2.5,'wide':3.5}[mode]))>1e-5:raise ValueError('Wrong width')
    last=trace[-1]
    if mode=='narrow' and not (float(last['travelled'])<2 and last['blocked']=='1'):raise ValueError('Narrow did not block')
    if mode=='wide' and not (float(last['travelled'])>6 and last['blocked']=='0'):raise ValueError('Wide did not traverse')
    from PIL import Image
    for view in CONTRACT['cameras']:
        files=sorted((folder/view).glob('*.jpg'))
        if [p.name for p in files]!=[f'{n:04}.jpg' for n in range(270)]:raise ValueError('Missing/extra capture frames')
        for n in (0,70,160,269):
            with Image.open(files[n]) as image:
                image.load()
                if image.size!=(1920,1080):raise ValueError('Wrong decoded dimensions')
    return trace


def check_capture(output,fp):
    traces={m:check_mode(output,m,fp) for m in CONTRACT['modes']}
    for a,b in zip(traces['narrow'],traces['wide']):
        if any(a[k]!=b[k] for k in ('frame','commandX','commandZ','playerDiameter')):raise ValueError('Input streams differ')
    return traces


def attempts():
    return ([OUTPUT] if OUTPUT.exists() else [])+(sorted(ATTEMPTS.iterdir()) if ATTEMPTS.exists() else [])


def matching_attempt(path,prov):
    try:
        rec=read(path/'attempt.json')
        return rec['fingerprint']==prov['fingerprint'] and rec['sourcePins']==prov['sourcePins'] and rec['contract']==CONTRACT
    except (OSError,ValueError,KeyError,TypeError):return False


def scan_attempts(prov):
    valid={}
    for output in attempts():
        if not output.is_dir() or not matching_attempt(output,prov):continue
        modes={}
        for mode in CONTRACT['modes']:
            try:modes[mode]=check_mode(output,mode,prov['fingerprint'])
            except (OSError,ValueError,KeyError,TypeError):continue
            valid.setdefault(mode,output/mode)
        if len(modes)==2:
            check_capture(output,prov['fingerprint']);return output,valid
    return None,valid


def link_or_copy(source,dest):
    try:os.link(source,dest)
    except OSError:shutil.copy2(source,dest)
    return dest


def stage_attempt(prov,reusable):
    output=OUTPUT if not OUTPUT.exists() or not any(OUTPUT.iterdir()) else ATTEMPTS/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:10])
    output.mkdir(parents=True,exist_ok=(output==OUTPUT))
    record=dict(prov,createdAt=time.time(),output=str(output),reusedModes={})
    for mode,source in reusable.items():
        check_mode(source.parent,mode,prov['fingerprint'])
        shutil.copytree(source,output/mode,copy_function=link_or_copy)
        record['reusedModes'][mode]=dict(source=str(source),receiptSHA256=sha(source/'mode-complete.json'),traceSHA256=sha(source/'trace.csv'))
    save(output/'attempt.json',record)
    return output


def update_json(path,change):
    for _ in range(5):
        original=path.read_bytes();value=json.loads(original.decode('utf-8-sig'));change(value)
        if path.read_bytes()==original:save(path,value);return
    raise RuntimeError('Concurrent project update; preserve capture and retry CPU export')


def verify_export(output,prov):
    fp=prov['fingerprint'];traces=check_capture(output,fp);marker=output/'capture-complete.txt'
    if marker.exists() and marker.read_text(encoding='utf-8-sig').split(';')[0].strip()!=fp:raise ValueError('Preserve marker for another fingerprint')
    recovered=not marker.exists()
    if recovered:marker.write_text(fp+'; CPU recovery from two validated native mode receipts\n',encoding='utf-8')
    source=PROJECT/'Assets/VideoScenes/architectural-111-20261106';target=ROOT/'unity/VideoEditing/Assets/VideoScenes/architectural-111-20261106'
    for name in ('02-narrow.unity','04-wide.unity'):
        if not (source/'03-02'/name).is_file():raise ValueError('Native editable scene was not saved')
    for p in source.rglob('*'):
        dest=target/p.relative_to(source)
        if p.is_file() and dest.exists() and sha(p)!=sha(dest):raise RuntimeError('Capture valid, export pending: differing prior editable asset preserved')
    shutil.copytree(source,target,dirs_exist_ok=True)
    exported=[target/p.relative_to(source) for p in sorted(source.rglob('*')) if p.is_file()]
    proof=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in exported]
    paths=[(target/'03-02'/n).relative_to(ROOT).as_posix() for n in ('02-narrow.unity','04-wide.unity')]
    evidence=dict(status='native-structure-and-trace-verified; visual-and-audio-review-pending',fingerprint=fp,output=str(output),resolution=[1920,1080],framesPerView=270,simulationFps=60,cameras=CONTRACT['cameras'],narrowLast=traces['narrow'][-1],wideLast=traces['wide'][-1],traceSHA256={m:sha(output/m/'trace.csv') for m in CONTRACT['modes']},inputCommandComparison='Same initial coordinates and commands; only wall width changes',completionMarkerRecoveredByCpu=recovered,editableScenePaths=paths,exportedAssetProof=proof,fullRealTimeReview=False,captionedMaster=False,humanApproval=False,finalMovieComplete=False)
    save(HERE/'first-native-evidence.json',evidence)
    update_json(HERE/'first-unity-preparation.json',lambda p:p.update(actualSceneFilesSaved=True,savedScenePaths=paths,exportedAssetProof=proof,unityLaunched=True,nativeFingerprint=fp))
    record=dict(fingerprint=fp,output=str(output),evidence='production/batches/architectural-111-20261106/first-native-evidence.json',editableScenePaths=paths,exportedAssetProof=proof,finalMovieComplete=False,visualReviewPending=True)
    project_dir=ROOT/'projects/shorts-leveldesign-03-02'
    pre_native={'preproduction-in-progress','script-preparation','source-mapped-script-draft',
                'preproduction-prepared','source-audited-native-prepared','waiting-for-native',
                'native-capture-in-progress','native-captured-review-pending'}
    def attach_native(p):
        previous=p.get('nativeCapture',{})
        merged=dict(record)
        if previous.get('fingerprint')==fp:
            for key in ('visualReviewPending','fullRealTimeReview','humanApproval','finalMovieComplete'):
                if key in previous:merged[key]=previous[key]
        p['nativeCapture']=merged;p.setdefault('finalMovieComplete',False)
    def project_record(p):
        attach_native(p)
        if p.get('status') in pre_native:p['status']='native-captured-review-pending'
    update_json(project_dir/'project.json',project_record)
    def checkpoint(p):
        attach_native(p)
        p['editableUnityScenesSaved']=list(dict.fromkeys(p.get('editableUnityScenesSaved',[])+paths))
        if p.get('stage') in pre_native:p['stage']='native-captured-review-pending'
        p.setdefault('finalOutputsVerified',False)
        p['completedStages']=list(dict.fromkeys(p.get('completedStages',[])+['native-capture-structure-and-trace','editable-unity-scene-export']))
    update_json(project_dir/'checkpoint.json',checkpoint)
    return evidence


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6)
    args=parser.parse_args();prov=authorize()
    if not args.execute:
        complete,valid=scan_attempts(prov)
        print(json.dumps(dict(prepared=True,existingComplete=str(complete) if complete else None,reusableModes=list(valid),resourceWait=busy_reason(),rendererStarted=False)));return
    worker=SingleWorker().acquire();owned=None;child=None;state=None
    try:
        old=read(STATE) if STATE.exists() else {}
        legacy_child=old.get('child') or ({'pid':old['unityPid']} if old.get('unityPid') else None)
        if old.get('pid')!=os.getpid() and (alive(old) or alive(legacy_child)):raise RuntimeError('Existing worker or child remains alive/unknown')
        known={r.get('leaseToken') for r in (old,worker.previous or {}) if r.get('leaseToken')}
        for rec in (old,worker.previous or {}):known.update(rec.get('recoverableLeaseTokens',[]))
        worker.update(recoverableLeaseTokens=sorted(known))
        recover_own_lease(known)
        state=dict(protocol=PROTOCOL,owner=OWNER,token=worker.record['token'],**identity(),child=None,status='recovering-existing-output',scope='Only topic03.02 native capture',automation=False,fingerprint=prov['fingerprint'],recoverableLeaseTokens=sorted(known),gpuStarted=False,completed=False,finalMovieComplete=False)
        save(STATE,state);complete,reusable=scan_attempts(prov);output=complete or stage_attempt(prov,reusable);state['output']=str(output)
        if complete or len(reusable)==2:verify_export(output,prov)
        else:
            deadline=time.monotonic()+max(0,args.wait_hours)*3600
            while owned is None:
                assert authorize()['fingerprint']==prov['fingerprint'],'Inputs changed while waiting'
                recover_own_lease(known)
                reason=busy_reason();state.update(status='waiting-for-resources',reason=reason,checkedAt=time.time());save(STATE,state)
                if not reason:
                    token=uuid.uuid4().hex;rec=dict(protocol=PROTOCOL,owner=OWNER,token=token,**identity(),child=None,phase='reserved',fingerprint=prov['fingerprint'],output=str(output),createdAt=time.time())
                    try:
                        with LEASE.open('x',encoding='utf-8') as f:json.dump(rec,f)
                    except FileExistsError:pass
                    else:owned=token;worker.update(leaseToken=owned);state['leaseToken']=owned;save(STATE,state)
                if owned is None:
                    if time.monotonic()>=deadline:raise RuntimeError('Finite resource wait ended; applications preserved')
                    time.sleep(10)
            assert authorize()['fingerprint']==prov['fingerprint']
            if busy_reason(owned):raise RuntimeError('Resource changed after lease; safely retry later')
            newer,_=scan_attempts(prov)
            if newer:output=newer;state['output']=str(output);verify_export(output,prov)
            else:
                missing=[m for m in CONTRACT['modes'] if m not in reusable]
                command=[EDITOR,'-batchmode','-job-worker-count','2','-projectPath',str(PROJECT),'-executeMethod','Yamyam.Architectural111.Editor.TunnelBuilder.Capture','-architecturalOutput',str(output),'-architecturalModes',','.join(missing),'-architecturalFingerprint',prov['fingerprint'],'-logFile',str(output/'unity.log')]
                rec=read(LEASE);assert ours(rec) and rec['token']==owned
                rec['phase']='launching';save(LEASE,rec)
                child=subprocess.Popen(command,creationflags=CREATE);child_id=identity(child.pid)
                worker.update(child=child_id);state.update(status='native-capturing',child=child_id,unityPid=child.pid,gpuStarted=True,reason=None)
                rec=read(LEASE)
                if not ours(rec) or rec['token']!=owned:raise RuntimeError('Lease changed; preserve live child')
                rec.update(child=child_id,phase='running');save(LEASE,rec);save(STATE,state)
                if child.wait()!=0:raise RuntimeError('Unity failed; preserve attempt, mode outputs and log')
                assert authorize()['fingerprint']==prov['fingerprint'],'Inputs changed during capture'
                state['status']='capture-valid-export-pending';save(STATE,state);verify_export(output,prov)
        state.update(status='native-complete-review-pending',completed=True,reviewReady=False)
    except BaseException as error:
        if state is not None:state.update(status='failed-or-resource-blocked',error=repr(error))
        raise
    finally:
        child_live=bool(child and child.poll() is None) or bool(state and alive(state.get('child')))
        if owned and LEASE.exists():
            try:
                rec=read(LEASE)
                if ours(rec) and rec['token']==owned and not child_live:LEASE.unlink()
            except (OSError,ValueError):pass  # Unknown ownership is preserved.
        if state is not None:
            state.update(finishedOrYieldedAt=time.time(),childStillAlive=child_live)
            if child_live:state['status']='worker-yielded-child-still-running'
            save(STATE,state)
        worker.close(remove=not child_live)
    print('Native capture verified; final-movie and human-review records preserved separately.',flush=True)


if __name__=='__main__':main()
