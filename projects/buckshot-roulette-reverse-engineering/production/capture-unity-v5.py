"""Capture only this video's editable Unity workflow scenes in the open editor."""
from pathlib import Path
import argparse, atexit, hashlib, json, os, subprocess, time, uuid
from datetime import datetime,timezone

P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
U=ROOT/'unity/VideoEditing';ASSETS=U/'Assets/VideoScenes/buckshot-workflow-v5'
OUT=P/'production/local/unity-v5';CONFIG=P/'production/unity-workflow-v5-cues.json'
REQUEST=U/'Library/BuckshotWorkflowV5.request.json';STATUS=U/'Library/BuckshotWorkflowV5.status.json'
LEASE=ROOT/'shared/output/GPU_HANDOFF.json'
def read(p):
    for attempt in range(12):
        try:return json.loads(p.read_text(encoding='utf-8-sig'))
        except (PermissionError,json.JSONDecodeError):
            if attempt==11:raise
            time.sleep(.1)
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def prepare():
    spec=read(CONFIG);files=[ASSETS/'BuckshotWorkflowStage.cs',ASSETS/'Editor/BuckshotWorkflowCapture.cs',CONFIG,P/'production/rasterize-unity-labels-v5.py']
    fingerprint=hashlib.sha256(''.join(sha(x) for x in files).encode()).hexdigest()
    version=ASSETS/'BuckshotWorkflowBuildVersion.cs'
    text='namespace Yamyam.BuckshotWorkflowV5 { public static class BuckshotWorkflowBuildVersion { public const string Value="'+fingerprint+'"; } }\n'
    if not version.exists() or version.read_text()!=text:version.write_text(text,encoding='utf-8')
    for row in spec['entries']:write(OUT/row['id']/'config.json',row)
    write(OUT/'build.json',{'fingerprint':fingerprint,'files':{str(x.relative_to(ROOT)):sha(x) for x in files},'preparedAt':now(),'userReview':False})
    return spec,fingerprint
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--capture',choices=['preflight','render']);ap.add_argument('--id');args=ap.parse_args()
    spec,fingerprint=prepare()
    if not args.capture:print(json.dumps({'prepared':True,'fingerprint':fingerprint,'scenes':len(spec['entries'])}));return
    control=read(ROOT/'shared/publishing/video-production-control.json')['scopedSetupAuthorizations'][P.name]
    assert control['productionAllowedNow'] and control['revision']=='v5'
    assert not REQUEST.exists(),'Existing editor request preserved'
    OUT.mkdir(parents=True,exist_ok=True)
    if LEASE.exists():raise RuntimeError('Existing GPU job lease preserved')
    token=f'buckshot-unity-v5-{os.getpid()}'
    lease={'owner':token,'pid':os.getpid(),'project':P.name,'kind':'Unity explanation capture','createdAt':now(),'scope':'v5 selected visual revision'}
    LEASE.parent.mkdir(parents=True,exist_ok=True)
    with LEASE.open('x',encoding='utf-8') as f:json.dump(lease,f)
    in_flight=False
    def release():
        if in_flight:return
        try:
            if read(LEASE).get('owner')==token:LEASE.unlink()
        except FileNotFoundError:pass
    atexit.register(release)
    entries=[r for r in spec['entries'] if not args.id or r['id']==args.id]
    assert entries
    for row in entries:
        current=read(ROOT/'shared/publishing/video-production-control.json')['scopedSetupAuthorizations'][P.name]
        assert current['productionAllowedNow'] and current['revision']=='v5','Authorization changed; stop before next cut'
        folder=OUT/row['id']/('preflight-'+fingerprint[:8] if args.capture=='preflight' else 'render')
        success=folder/(args.capture+'-success.json')
        if success.exists():
            assert read(success)['fingerprint']==fingerprint,'Earlier capture preserved; choose a new revision'
            print(row['id']+' already captured',flush=True);continue
        if args.capture=='render':
            approval=read(OUT/'source-preflight-review.json')
            assert approval['fingerprint']==fingerprint and row['id'] in approval['passedIds'],'Current Unity sample review required'
        samples={0,round(row['frames']*.2),round(row['frames']*.5),row['frames']-1}
        for c in row['cues']:
            for delta in [-2,24,60]:samples.add(max(0,min(row['frames']-1,round(c['time']*60)+delta)))
        assert not folder.exists() or not any(folder.iterdir()),'Previous partial attempt preserved; inspect before retrying'
        request={'command':args.capture,'id':row['id'],'mode':row['mode'],'frames':row['frames'],'config':str((OUT/row['id']/'config.json').resolve()),'output':str(folder.resolve()),'expectedFingerprint':fingerprint,'sampleFrames':sorted(samples),'jobToken':uuid.uuid4().hex}
        in_flight=True
        write(REQUEST,request);print('requested '+row['id']+' '+args.capture,flush=True)
        started=time.monotonic();last=-1
        while not success.exists():
            if STATUS.exists():
                observed=read(STATUS)
                if observed.get('jobToken')==request['jobToken'] and observed.get('status')=='rejected':
                    in_flight=False
                    raise RuntimeError(observed.get('error','Editor rejected request'))
            failed=folder/(args.capture+'-failure.json')
            if failed.exists():
                # The bridge writes terminal state after closing its encoder.
                in_flight=False
                raise RuntimeError(failed.read_text())
            if time.monotonic()-started>1800:raise TimeoutError('Editor response/capture timeout; do not duplicate its request')
            progress=folder/'progress.json'
            if progress.exists():
                try:
                    info=read(progress)
                    if info.get('completed',0)!=last:
                        last=info.get('completed',0);print(row['id']+' '+str(last)+'/'+str(row['frames']),flush=True)
                except json.JSONDecodeError:pass
            time.sleep(2)
        info=read(success);assert info['fingerprint']==fingerprint and info['status']=='complete'
        in_flight=False
        print('complete '+row['id'],flush=True)
    write(OUT/(args.capture+'-batch.json'),{'finishedAt':now(),'fingerprint':fingerprint,'ids':[x['id'] for x in entries],'status':'complete','humanReview':False})
    release()
if __name__=='__main__':main()
