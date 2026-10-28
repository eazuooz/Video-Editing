"""Sequential clarity-v3 bridge requests. Parent alone starts costly captures."""
from pathlib import Path
import argparse,hashlib,json,time,subprocess,os,re
from freeze_sources import R,H,U,C,STAGES,digest,read,records_for,fingerprint
M=Path('C:/Users/1/.codex/video-production/design-25-30-review-actions-20261029')

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def exclusive_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def authorize(slug):
    assert slug in STAGES,'Only D25 and D29 revisions are selected'
    auth=read(H/'authorization.json');assert any(x['slug']==slug and x['revision']=='clarity-v3' for x in auth['revisions'])
    assert auth['gpuAuthorization']['authorized'] and auth['gpuAuthorization']['sequentialCostlyJobs']
    control=read(R/'shared/publishing/video-production-control.json')['finiteBatchAuthorizations'][H.name]
    assert control['gpuAuthorized'] and control['status']=='active-upload-and-two-revisions'
    assert ('D25' if slug=='limited-color-world' else 'D29') in control['revisionEpisodeIds']
def ensure_idle():
    library=U/'Library'
    pending=list(library.glob('*.request'))+list(library.glob('*.request.json'))
    assert not pending,'Pending bridge request must be preserved: '+','.join(str(p) for p in pending)
    for name in ['DesignVisualV2','DesignClarityV3']:
        p=library/(name+'.status.json')
        if p.exists():assert read(p).get('status') not in ['building','capturing'],'Active capture: '+name
    asset=library/'YamyamAssetLibrary/state.json'
    if asset.exists():assert read(asset).get('phase') in ['complete','failed'],'Asset-library bridge is still active'
REPRESENTATIVE_CUTS={'limited-color-world':{'forest-gray','puyo-official-filters'},'kind-to-beginners':{'05-01','06-02'}}
def gpu_check(representative_only=False,selected_clarity_8gib=False):
    lines=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().splitlines()
    free,util=map(int,lines[0].split(','))
    if representative_only or selected_clarity_8gib:
        # Root explicitly authorized these four short preflights despite uncertain
        # external utilization, after D25 CPU ASR released the production slot.
        assert free>=8192,('Selected sequential clarity capture requires 8GiB free; preserve other tasks',free,util)
    else:assert free>=2500 and util<=85,('GPU busy; do not terminate other tasks',free,util)
    return {'freeVramMiB':free,'utilizationPercent':util,'policy':'selected-D25-D29-measured-clarity-only-8GiB' if selected_clarity_8gib else ('four-representative-preflight-8GiB' if representative_only else 'standard-sequential-capture')}
def validate_job(j,slug):
    assert j['slug']==slug and j['stageClass']==STAGES[slug],'Slug/stage mismatch'
    assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',j['cutId']),'Invalid cut ID'
    assert isinstance(j['frames'],int) and 0<j['frames']<=36000,'Invalid frame count'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--slug',choices=list(STAGES),required=True);ap.add_argument('--cut')
    ap.add_argument('--phase',choices=['preflight','render'],default='preflight');ap.add_argument('--revision',default='v1')
    ap.add_argument('--sample-frames');ap.add_argument('--exact-sample-frames',help='One preflight cut only: replace the normal sample set with these bounded frame numbers')
    ap.add_argument('--jobs',help='Workspace-relative selected project job JSON')
    ap.add_argument('--dry-run',action='store_true');ap.add_argument('--representative-only',action='store_true')
    ap.add_argument('--selected-clarity-8gib',action='store_true');a=ap.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9_-]+',a.revision),'Invalid capture revision'
    authorize(a.slug)
    selected=R/'projects'/a.slug/'production/clarity-v3'
    jobsPath=R/a.jobs if a.jobs else selected/'capture-jobs.json'
    assert jobsPath.resolve().is_relative_to(selected.resolve()),'Jobs must remain inside the selected clarity-v3 project folder'
    doc=read(jobsPath)
    if a.selected_clarity_8gib:
        assert not a.representative_only and doc.get('timingLocked') is True, 'The scoped 8GiB exception requires final measured D25/D29 jobs and a separately granted sequential resource slot'
    if a.phase=='render':assert doc.get('timingLocked') is True,'Render requires measured final narration timing; provisional preflight is not production timing'
    jobs=[j for j in doc['jobs'] if j['slug']==a.slug and (not a.cut or j['cutId']==a.cut)];assert jobs,'No matching jobs'
    if a.representative_only:
        assert a.phase=='preflight' and len(jobs)==1 and a.cut in REPRESENTATIVE_CUTS[a.slug], '8GiB representative exception is limited to four designated single-cut preflights'
    request=U/'Library/DesignClarityV3.request.json';status=U/'Library/DesignClarityV3.status.json'
    for j in jobs:
        authorize(a.slug);validate_job(j,a.slug)
        frozen=read(H/'clarity-code-fingerprint.json');records=records_for(j['stageClass']);fp=fingerprint(records)
        assert frozen['fingerprints'].get(j['stageClass'])==fp,'Source changed after freeze; do not waive compile guard'
        assert digest(R/frozen['generatedBuildVersion'])==frozen['generatedBuildVersionSha256'],'Generated build-version source changed'
        out=M/a.slug/'clarity-v3'/a.phase/a.revision/j['cutId']
        assert out.resolve().is_relative_to((M/a.slug/'clarity-v3').resolve()),'Resolved output escapes media scope'
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
            print('REUSED '+a.slug+' '+j['cutId'],flush=True);continue
        if a.dry_run:
            print(json.dumps({'status':'dry-run-only','request':raw,'inputHash':inputHash,'writesPerformed':False}),flush=True);continue
        ensure_idle();resourceRead=gpu_check(a.representative_only,a.selected_clarity_8gib)
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
        expectedRender='RenderPipeline.StandardRequest (D25 world only; editorial UI composited separately)' if a.slug=='limited-color-world' else 'RenderPipeline.StandardRequest (full camera stack)'
        assert done['renderRequest']==expectedRender
        print('DONE '+a.slug+' '+j['cutId'],flush=True)
    print('ALL COMPLETE '+a.slug+' '+a.phase,flush=True)
if __name__=='__main__':main()
