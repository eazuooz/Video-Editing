"""One finite, resumable original-tunnel capture; waits for shared resources, never uploads."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import psutil
from initialize import HERE,ROOT,MEDIA,AUTH_KEY,read,save

LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
STATE=MEDIA/'first-native-progress.json'
PROJECT=MEDIA/'unity-capture'
OUTPUT=MEDIA/'shorts-leveldesign-03-02/native-v1'
CREATE=getattr(subprocess,'CREATE_NO_WINDOW',0)

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def authorize():
    control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH_KEY]
    assert control['userEvidence']=='111개 전체 제작 들어가줘'
    assert control['status'] not in ('paused','cancelled','stopped')
    assert control['automaticAdvanceWithinExactList'] and not control['automaticAdvanceOutsideList']
    assert control['humanFinalReviewRequired'] and not control['youtubeAuthorized']
    batch=read(HERE/'batch.json');assert batch['localFinalReviewOnly'] and len(batch['projects'])==111
    assert sha(ROOT/batch['sourceCatalog'])==batch['sourceCatalogSHA256']
    assert any(r['topicId']=='03.02' and r['slug']=='shorts-leveldesign-03-02' for r in batch['projects'])
    prep=read(HERE/'first-unity-preparation.json')
    for item in prep['files']:
        assert sha(ROOT/item['source'])==item['sha256'], 'Prepared source changed; prepare and re-audit before restarting'
        assert sha(PROJECT/item['target'])==item['sha256'], 'Staged source changed'
    report=read(HERE/'first-unity-compiler-preflight.json');assert report['compilerExitCode']==0
    for name,expected in report['sourceHashes'].items():assert sha(HERE/name)==expected

def busy_reason():
    if LEASE.exists():return 'Another scoped job holds the shared GPU lease'
    for proc in psutil.process_iter(['pid','name','exe','cmdline']):
        try:
            i=proc.info;name=(i['name'] or '').lower();exe=(i['exe'] or '').replace('\\','/').lower();args=[s.lower() for s in i['cmdline'] or []]
            if proc.pid==os.getpid():continue
            if '/steamapps/common/' in exe or name in ('overwatch.exe','d2r.exe'):
                return 'User game is running; do not use GPU'
            if name=='unity.exe':
                if 'unity hub' in exe and 'serve' in args:continue
                return 'Another Unity editor or batch worker is running'
            if name=='unrealeditor.exe':return 'Another Unreal editor is running'
            if name.startswith('python') and any(k in ' '.join(args) for k in ('--synthesize','render_narration','faster_whisper','torchrun')):
                return 'Another model job is running'
            if name=='ffmpeg.exe':return 'Another media job is running'
        except (psutil.NoSuchProcess,psutil.AccessDenied):continue
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=CREATE)
    free,use=map(int,raw.splitlines()[0].split(','))
    if free<8192 or use>25:return f'GPU headroom insufficient ({free} MiB free, {use}% use)'
    return None

def verify():
    assert (OUTPUT/'capture-complete.txt').exists()
    traces={}
    for mode in ['narrow','wide']:
        with (OUTPUT/mode/'trace.csv').open(encoding='utf8') as f:traces[mode]=list(csv.DictReader(f))
        assert len(traces[mode])==270
        for view in ['observer','top']:
            images=sorted((OUTPUT/mode/view).glob('*.jpg'));assert len(images)==270
            from PIL import Image
            for n in [0,70,160,269]:
                with Image.open(images[n]) as image:assert image.size==(1920,1080)
    for a,b in zip(traces['narrow'],traces['wide']):
        assert (a['frame'],a['commandX'],a['commandZ'],a['playerDiameter'])==(b['frame'],b['commandX'],b['commandZ'],b['playerDiameter'])
    assert float(traces['narrow'][-1]['travelled'])<2 and traces['narrow'][-1]['blocked']=='1'
    assert float(traces['wide'][-1]['travelled'])>6 and traces['wide'][-1]['blocked']=='0'
    evidence=dict(status='native-structure-and-trace-verified; visual-and-audio-review-pending',
        resolution=[1920,1080],framesPerView=270,simulationFps=60,cameras=['observer','top'],
        inputCommandComparison='Identical initial coordinates, commandX, commandZ, capsule, cart and speed; only wall width changes',
        narrowLast=traces['narrow'][-1],wideLast=traces['wide'][-1],
        traceSHA256={m:sha(OUTPUT/m/'trace.csv') for m in traces},
        fullRealTimeReview=False,captionedMaster=False,humanApproval=False)
    save(HERE/'first-native-evidence.json',evidence)
    source=PROJECT/'Assets/VideoScenes/architectural-111-20261106'
    target=ROOT/'unity/VideoEditing/Assets/VideoScenes/architectural-111-20261106'
    # This unique source subtree was newly selected. Never replace another video's scene.
    if target.exists():
        for p in source.rglob('*'):
            dest=target/p.relative_to(source)
            if p.is_file() and dest.exists():assert sha(p)==sha(dest),'Preserve differing prior editable asset'
    shutil.copytree(source,target,dirs_exist_ok=True)
    prep=read(HERE/'first-unity-preparation.json');prep['actualSceneFilesSaved']=True
    prep['savedScenePaths']=[(target/'03-02'/name).relative_to(ROOT).as_posix() for name in ['02-narrow.unity','04-wide.unity']]
    prep['unityLaunched']=True;save(HERE/'first-unity-preparation.json',prep)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-hours',type=float,default=6)
    args=parser.parse_args();authorize()
    if not args.execute:
        print(json.dumps(dict(prepared=True,resourceWait=busy_reason(),rendererStarted=False)));return
    if STATE.exists():
        old=read(STATE)
        if old.get('status')=='native-complete-review-pending':verify();print('Existing verified native capture preserved');return
        try:
            if abs(psutil.Process(old['pid']).create_time()-old['createTime'])<.05:
                raise RuntimeError('Existing finite capture worker is still active')
        except psutil.NoSuchProcess:pass
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise RuntimeError('Preserve partial output and inspect before choosing a new attempt directory')
    state=dict(pid=os.getpid(),createTime=psutil.Process().create_time(),status='waiting-for-resources',
               scope='One first-topic native capture only',automation=False,gpuStarted=False,completed=False)
    deadline=time.monotonic()+max(0,args.wait_hours)*3600;owned=None
    try:
        announced=False
        while owned is None:
            authorize();reason=busy_reason();state.update(reason=reason,checkedAt=time.time());save(STATE,state)
            if not reason:
                candidate=str(uuid.uuid4())
                try:
                    with LEASE.open('x',encoding='utf8') as f:json.dump(dict(owner='architectural-111-first-native',id=candidate,pid=os.getpid(),createdAt=time.time()),f)
                except FileExistsError:pass
                else:owned=candidate;break
            if not announced:print('Prepared first native capture; waiting safely for shared resources.',flush=True);announced=True
            if time.monotonic()>deadline:raise RuntimeError('Finite resource wait ended; existing applications and jobs preserved')
            time.sleep(10)
        authorize()
        log=MEDIA/'first-native-unity.log'
        command=['C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','-batchmode','-job-worker-count','2',
            '-projectPath',str(PROJECT),'-executeMethod','Yamyam.Architectural111.Editor.TunnelBuilder.Capture',
            '-architecturalOutput',str(OUTPUT),'-logFile',str(log)]
        child=subprocess.Popen(command,creationflags=CREATE);state.update(status='native-capturing',unityPid=child.pid,gpuStarted=True,reason=None);save(STATE,state)
        if child.wait()!=0:raise RuntimeError('Unity failed; inspect preserved first-native-unity.log')
        verify();state.update(status='native-complete-review-pending',completed=True,reviewReady=False)
    except BaseException as error:
        state.update(status='failed-or-resource-blocked',error=repr(error));raise
    finally:
        if owned and LEASE.exists() and read(LEASE).get('id')==owned:LEASE.unlink()
        state['finishedOrYieldedAt']=time.time();save(STATE,state)
    print('First native capture trace verified; actual image, timing, speech and final film remain to review.',flush=True)

if __name__=='__main__':main()
