"""CPU2 exact encoded-PTS samples for guides or the final244-cue pair; local only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, re, subprocess, traceback
import psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.resolve().relative_to(ROOT).as_posix()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(p,v):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--mode',choices=['pair'],required=True);a=ap.parse_args()
    resource=read(ROOT/a.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    subprocess.run([node,'scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file',str(O/'duplicate-candidate-v1.json'),'--check'],cwd=ROOT,check=True)
    local=ROOT/f'shared/output/unpublished-teaching-clarity-revision/orientation/current34-{a.mode}-pixel-v2'
    sp=O/f'current34-{a.mode}-pixel-execution-v2.json';assert not local.exists() and not sp.exists()
    proof=read(O/'narration-07b-guide-repair-execution-v1.json')
    for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
    timing=read(O/'current34-measured-timing-plan-v1.json'); tasks=[]
    def sample_points(n, cues):
        points={0:['first'],n-1:['last']}
        def put(f,reason):
            f=max(0,min(n-1,int(f)));points.setdefault(f,[]).append(reason)
        for f in range(0,n,120):put(f,'whole-two-second')
        for c in cues:
            start=max(0,int(c['start']*60+.999999));end=min(n,int(c['end']*60+.999999))
            assert end>start
            for f,kind in [(start,'first'),((start+end-1)//2,'mid'),(end-1,'last')]:put(f,c['id']+'-'+kind)
        return points,put
    if a.mode=='guides':
        worker=read(O/'current34-baseline-guides-render-execution-v1.json')
        assert worker['actualOuterExitCode']==0 and worker['workerDead']
        plan=read(O/'current34-baseline-guide-plan-v2.json')
        for row,encoded in zip(plan['scenes'],worker['results']):
            assert row['id']==encoded['id']
            cues=[dict(id=f'p{x["index"]:02d}',start=x['start'],end=x['end']) for x in row['retainedParagraphs']]
            points,put=sample_points(row['frames'],cues)
            for x in row['pointWindow']['keyframes']:
                put(row['pointWindow']['sceneFrameIn']+x['frame'],'manual-anchor')
            for a1,b1 in row['pointWindow']['hiddenLocalFrameRanges']:
                for f in [a1-1,a1,b1-1,b1]:put(row['pointWindow']['sceneFrameIn']+f,'occlusion-boundary')
            for name in ['pointVisibleSceneFrameRange','redScreenDisplacementSceneFrameRange','goldImageUpSceneFrameRange']:
                region=row[name]
                if len(region)==2:
                    for f in [region[0]-1,region[0],region[1]-1,region[1]]:put(f,name+'-boundary')
                    for f in range(region[0],region[1],30):put(f,name+'-moving-half-second')
            for cut in row['windows']:
                for f in [cut['sceneFrameIn']-1,cut['sceneFrameIn'],cut['sceneFrameOut']-1,cut['sceneFrameOut']]:put(f,'native-cut-boundary')
            tasks.append(dict(id=row['id'],video=encoded['output'],videoSha256=encoded['outputSha256'],frames=row['frames'],points=points,frameAudit=encoded['frameAudit']))
    else:
        worker=read(O/'current34-final-pair-execution-v3.json')
        assert worker['actualOuterExitCode']==0 and worker['workerDead'] and len(worker['pair'])==2
        pair=worker['pair'][1];alignment=read(O/'current34-caption-alignment-v1.json')
        assert alignment['allNewCueTimingDirectlyReviewed'] and len(alignment['entries'])==244
        cues=[dict(id=f'cue{x["id"]:03d}',start=x['start'],end=x['end']) for x in alignment['entries']]
        points,put=sample_points(worker['frames'],cues)
        offset=0
        for piece in worker['pieces']:
            for f in [offset-1,offset,offset+piece['frames']-1,offset+piece['frames']]:put(f,'piece-'+piece['id']+'-boundary')
            offset+=piece['frames']
        assert offset==worker['frames']
        mix=read(O/'current34-mix-execution-v2.json')
        for i,x in enumerate(mix['placements']):
            for field in ['destinationStartSample','destinationEndSample']:
                f=round(x[field]/400)
                for v in [f-1,f,f+1]:put(v,f'PCM{i:02d}-{field}')
        for s in timing['scenes']:
            if not s['baseline'] or s['id'] in ['01','12','18','24']:
                for f in range(s['frameIn'],s['frameOut'],60):put(f,'new-current-motion-'+s['id'])
        for row in read(O/'current34-baseline-guide-plan-v2.json')['scenes']:
            scene=next(x for x in timing['scenes'] if x['id']==row['id'])
            for cut in row['windows']:
                for f in [cut['sceneFrameIn']-1,cut['sceneFrameIn'],cut['sceneFrameOut']-1,cut['sceneFrameOut']]:put(scene['frameIn']+f,'native-guide-cut-'+row['id'])
        inputs=read(O/'current34-assembly-inputs-v3.json')
        assert inputs['detailedExplanationPieceCount']==17 and inputs['detailedMixedPieceCount']==3
        for pk,hk in [('detailedSampleReview','detailedSampleReviewSha256'),('detailedNormalReview','detailedNormalReviewSha256'),('overviewReview','overviewReviewSha256'),('guideReview','guideReviewSha256'),('mixedDetailReview','mixedDetailReviewSha256')]:
            assert sha(ROOT/inputs[pk])==inputs[hk]
        offsets={};offset=0
        for piece in worker['pieces']:
            offsets[piece['id']]=offset;offset+=piece['frames']
        assert offset==worker['frames']
        detail=read(O/'current34-detailed-explanations-sampled-direct-review-v1.json')
        mixed=read(O/'current34-mixed-detailed-direct-review-v1.json')
        guides=read(O/'current34-guides-pixel-execution-v1.json')
        overview=read(O/'current34-overview-direct-review-v5.json')
        assert detail['all605SamplesDirectlyRead'] and mixed['all172SamplesDirectlyRead']
        assert read(O/'current34-baseline-guides-direct-review-v1.json')['all562SamplesDirectlyRead']
        # Bind the final captioned frames to every prior selected moving subject/guide sample.
        for record,key in [(detail,'rows'),(mixed,'rows'),(guides,'results')]:
            for row in record[key]:
                sid=row.get('scene',row.get('id'))
                assert sid in offsets
                for sample in row['samples']:put(offsets[sid]+sample['frame'],'reviewed-subject-or-guide-'+sid)
        # The overview record may bind its samples through rows or scenes.
        ovexec=read(O/'current34-overview-render-execution-v5.json')
        for row in ovexec['scenes']:
            for sample in row['samples']:put(offsets[row['id']]+sample['frame'],'reviewed-detailed-overview-'+row['id'])
        for piece in worker['pieces']:
            if piece['id'] not in ['intro','19','outro']:
                for f in range(offsets[piece['id']],offsets[piece['id']]+piece['frames'],60):put(f,'current-detailed-motion-'+piece['id'])
        tasks=[dict(id='captioned',video=pair['path'],videoSha256=pair['sha256'],frames=worker['frames'],points=points)]
    local.mkdir(parents=True);me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    state=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
        mode=a.mode,resource=a.resource,resourceSha256=sha(ROOT/a.resource),cpuThreads=2,gpuJobs=0,status='extracting-current34-'+a.mode+'-pixels',exitCode=None,results=[],allFinalPixelsApproved=False,newImageGit=0,researchChanges=0)
    def checkpoint():
        ss=sp.with_name(sp.stem+'.session.json')
        if ss.exists():state['sessionId']=read(ss)['sessionId']
        state['updatedAt']=now();save(sp,state)
        cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],activeOwnedWorkers=int(state['exitCode'] is None),ownedJob=dict(active=state['exitCode'] is None,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(sp),cpuThreads=2,gpuJobs=0),next='Observe actual pixel extraction exit, then directly inspect every planned encoded sample/board and normal UI playback. Sampling does not approve every intermediate frame or human listening.');save(O/'latest-checkpoint.json',cp)
        qp=B/'queue.json';old=qp.read_bytes();q=read(qp);q['currentOrientationReview'].update(stage=cp['stage'],activeOwnedWorkers=cp['activeOwnedWorkers'],ownedJob=cp['ownedJob'],next=cp['next']);q['updatedAt']=now();assert qp.read_bytes()==old;save(qp,q)
    checkpoint()
    try:
        font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
        for task in tasks:
            video=ROOT/task['video'];assert sha(video)==task['videoSha256']
            folder=local/task['id'];folder.mkdir();indices=sorted(task['points'])
            selector='+'.join(f'eq(n,{f})' for f in indices)
            filterp=folder/'absolute-PTS-selection.fffilter'
            filterp.write_text(f"select='{selector}',showinfo",'utf-8')
            # Keep the complete selection in a file, below Windows argv limits.
            cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(video),'-filter_script:v',str(filterp),'-fps_mode','passthrough','-frames:v',str(len(indices)),'-threads','2',str(folder/'sample-%04d.png')]
            log=folder/'extraction.log'
            with log.open('wb') as f:
                child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
                state.update(currentTask=task['id'],childPid=child.pid,childCreateTime=psutil.Process(child.pid).create_time(),childCommand=cmd);checkpoint();code=child.wait()
            assert code==0
            pts=[int(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',log.read_text('utf-8',errors='replace'))]
            assert pts==[f*1500 for f in indices], (task['id'],'Exact encoded PTS mismatch')
            rows=[dict(frame=f,pts=f*1500,path=rel(folder/f'sample-{i:04d}.png'),sha256=sha(folder/f'sample-{i:04d}.png'),reasons=task['points'][f]) for i,f in enumerate(indices,1)]
            boards=[]
            for off in range(0,len(rows),4):
                im=Image.new('RGB',(1920,1140),'#171a1e');draw=ImageDraw.Draw(im)
                for j,x in enumerate(rows[off:off+4]):
                    xx=j%2*960;yy=j//2*570
                    with Image.open(ROOT/x['path']) as source:im.paste(source.resize((960,540)),(xx,yy+30))
                    draw.text((xx+8,yy+3),f'{task["id"]} frame{x["frame"]} PTS{x["pts"]}',font=font,fill='white')
                bp=folder/f'board-{off//4+1:03d}.png';im.save(bp);boards.append(dict(path=rel(bp),sha256=sha(bp)))
            state['results'].append(dict(id=task['id'],video=task['video'],videoSha256=task['videoSha256'],extractExitCode=code,log=rel(log),samples=rows,boards=boards,allSelectedEncodedPtsExact=True,allSamplesDirectlyRead=False));checkpoint()
            print(json.dumps(dict(id=task['id'],samples=len(rows),boards=len(boards),exitCode=0)),flush=True)
        for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
        state.update(status='current34-'+a.mode+'-pixels-extracted-awaiting-direct-review',exitCode=0,finishedAt=now(),all79ProtectedInputsUnchanged=True,repairCandidateUnchanged=True);checkpoint()
    except BaseException:
        state.update(status='failed-current34-'+a.mode+'-pixel-extraction-preserve-history',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
if __name__=='__main__':main()
