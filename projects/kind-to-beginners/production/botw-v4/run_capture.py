"""Sequential independent D29 BOTW bridge. Source-only dry-run or explicitly granted native execution."""
from pathlib import Path
import argparse,hashlib,json,time,subprocess,os,re
from freeze_sources import R,H,U,C,STAGES,digest,read,records_for,fingerprint
from native_scene_evidence import persist as persist_scene_evidence, verify as verify_scene_evidence
M=R/'projects/kind-to-beginners/production/local/botw-v4'

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def exclusive_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def authorize(slug):
    assert slug=='kind-to-beginners'
    auth=read(H/'authorization.json');assert auth['revision']=='botw-v4' and auth['localProductionAuthorized']
    control=read(R/'shared/publishing/video-production-control.json')['finiteBatchAuthorizations']['design-25-30-review-actions-20261029']['selectedD29Revision']
    assert control['revision']=='botw-v4' and control['status']=='production' and control['localProductionAuthorized']

def ensure_idle():
    library=U/'Library'
    pending=list(library.glob('*.request'))+list(library.glob('*.request.json'))
    assert not pending,'Pending bridge request must be preserved: '+','.join(str(p) for p in pending)
    for name in ['DesignVisualV2','DesignClarityV3','DesignBotwV4']:
        p=library/(name+'.status.json')
        if p.exists():assert read(p).get('status') not in ['building','capturing'],'Active capture: '+name
    asset=library/'YamyamAssetLibrary/state.json'
    if asset.exists():assert read(asset).get('phase') in ['complete','failed'],'Asset-library bridge is still active'
def gpu_check():
    lines=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().splitlines()
    free,util=map(int,lines[0].split(','))
    concurrent=read(H/'authorization.json').get('concurrentUnityCapture',{}).get('allowed') is True
    if concurrent:
        assert free>=2048,('Concurrent Unity capture needs 2GiB free; preserve game and wait',free,util)
    else:
        assert free>=8192 and util<=85,('Preserve external activity; wait for root resource decision',free,util)
    return {'freeVramMiB':free,'utilizationPercent':util,'policy':'user-authorized-concurrent-Unity-only-min2GiB-one-scene' if concurrent else 'D29-botw-v4-root-sequenced-8GiB'}

def validate_job(j,slug):
    assert j['slug']==slug and j['stageClass']==STAGES[slug],'Slug/stage mismatch'
    assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',j['cutId']),'Invalid cut ID'
    assert isinstance(j['frames'],int) and 0<j['frames']<=36000,'Invalid frame count'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--slug',choices=list(STAGES),required=True);ap.add_argument('--cut')
    ap.add_argument('--phase',choices=['preflight','render'],default='preflight');ap.add_argument('--revision',default='v1')
    ap.add_argument('--sample-frames');ap.add_argument('--exact-sample-frames',help='One preflight cut only: replace the normal sample set with these bounded frame numbers')
    ap.add_argument('--jobs',help='Workspace-relative selected project job JSON')
    ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9_-]+',a.revision),'Invalid capture revision'
    authorize(a.slug)
    selected=H
    jobsPath=R/a.jobs if a.jobs else selected/'capture-jobs.json'
    assert jobsPath.resolve().is_relative_to(selected.resolve()),'Jobs must remain inside the selected botw-v4 project folder'
    doc=read(jobsPath)
    if a.phase=='render':assert doc.get('timingLocked') is True,'Final render requires measured voice timing'
    jobs=[j for j in doc['jobs'] if j['slug']==a.slug and (not a.cut or j['cutId']==a.cut)];assert jobs,'No matching jobs'
    request=U/'Library/DesignBotwV4.request.json';status=U/'Library/DesignBotwV4.status.json'
    for j in jobs:
        authorize(a.slug);validate_job(j,a.slug)
        frozen=read(H/'botw-code-fingerprint.json');records=records_for(j['stageClass']);fp=fingerprint(records)
        assert frozen['fingerprints'].get(j['stageClass'])==fp,'Source changed after freeze; do not waive compile guard'
        assert digest(R/frozen['generatedBuildVersion'])==frozen['generatedBuildVersionSha256'],'Generated build-version source changed'
        out=M/a.phase/a.revision/j['cutId']
        assert out.resolve().is_relative_to(M.resolve()),'Resolved output escapes media scope'
        samples=sorted(set([0,min(j['frames']-1,30),*[int((j['frames']-1)*v) for v in [.2,.4,.6,.8,1]],*j.get('sampleFrames',[])]))
        if a.sample_frames:
            assert a.phase=='preflight' and a.cut,'Extra sample frames require one preflight cut'
            samples=sorted(set(samples+[int(x) for x in a.sample_frames.split(',')]))
        if a.exact_sample_frames:
            assert a.phase=='preflight' and a.cut and not a.sample_frames,'Exact samples require a single preflight cut and no additive samples'
            samples=sorted(set(int(x) for x in a.exact_sample_frames.split(',')))
        assert all(isinstance(f,int) and 0<=f<j['frames'] for f in samples)
        raw={'slug':j['slug'],'cutId':j['cutId'],'stageClass':j['stageClass'],'frames':j['frames'],
             'command':a.phase,'expectedFingerprint':fp,'output':out.as_posix(),'sampleFrames':samples}
        inputHash=hashlib.sha256(json.dumps({'request':raw,'job':j,'files':records},sort_keys=True).encode()).hexdigest()
        success=out/(a.phase+'-success.json');receipt=out/'request.json'
        if success.exists():
            assert receipt.exists() and read(receipt)['inputHash']==inputHash,'Existing capture differs; use a new revision'
            done=read(success);assert done['compiledSourceFingerprint']==fp and done['frames']==j['frames'] and done['status']=='complete'
            if a.phase=='render':verify_scene_evidence(receipt,success)
            print('REUSED '+a.slug+' '+j['cutId'],flush=True);continue
        if a.dry_run:
            print(json.dumps({'status':'dry-run-only','request':raw,'inputHash':inputHash,'writesPerformed':False}),flush=True);continue
        ensure_idle();resourceRead=gpu_check()
        assert not out.exists() or not any(out.iterdir()),'Existing partial output preserved; choose a fresh revision'
        out.mkdir(parents=True,exist_ok=True)
        exclusive_json(receipt,{**raw,'inputHash':inputHash,'sourceFiles':records,'jobsFile':jobsPath.relative_to(R).as_posix(),
            'jobsSha256':digest(jobsPath),'startedAt':time.time(),'coordinatorPid':os.getpid(),'resourceCheck':resourceRead})
        exclusive_json(request,raw)
        print('START '+a.slug+' '+j['cutId']+' '+a.phase+' '+str(j['frames']),flush=True)
        start=time.monotonic();last=-1
        while not success.exists():
            failure=out/(a.phase+'-failure.json')
            if failure.exists():raise RuntimeError(failure.read_text('utf-8'))
            if status.exists():
                try:s=read(status)
                except json.JSONDecodeError:s={}
                if s.get('slug')==a.slug and s.get('cutId')==j['cutId'] and s.get('output')==raw['output'] and s.get('status')=='rejected':
                    raise RuntimeError('Native bridge rejected request: '+s.get('error',''))
            if time.monotonic()-start>900:raise RuntimeError('Timeout; preserve active editor/request and inspect '+str(out))
            time.sleep(1)
            p=out/'progress.json'
            if p.exists():
                try:count=read(p)['completed']
                except (json.JSONDecodeError,KeyError):continue
                if count!=last and count%600==0:print('PROGRESS '+j['cutId']+' '+str(count),flush=True);last=count
        done=read(success)
        assert done['compiledSourceFingerprint']==fp,'Stale compiled source refused'
        assert done['completed']==(len(samples) if a.phase=='preflight' else j['frames'])
        expectedRender='RenderPipeline.StandardRequest (full camera stack)'
        assert done['renderRequest']==expectedRender
        if a.phase=='render':persist_scene_evidence(receipt,success)
        print('DONE '+a.slug+' '+j['cutId'],flush=True)
    print(('DRY RUN COMPLETE ' if a.dry_run else 'ALL COMPLETE ')+a.slug+' '+a.phase,flush=True)
if __name__=='__main__':main()
