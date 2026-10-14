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
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--mode',choices=['branding'],required=True);a=ap.parse_args()
    resource=read(ROOT/a.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    subprocess.run([node,'scripts/review-video-duplicates.cjs','game-math-orientation-matrices','--candidate-file',str(O/'duplicate-candidate-v1.json'),'--check'],cwd=ROOT,check=True)
    local=ROOT/f'shared/output/unpublished-teaching-clarity-revision/orientation/current34-{a.mode}-pixel-v3'
    sp=O/f'current34-{a.mode}-pixel-execution-v3.json';assert not local.exists() and not sp.exists()
    proof=read(O/'narration-07b-guide-repair-execution-v1.json')
    for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
    worker=read(O/'current34-final-pair-execution-v3.json')
    assert worker['actualOuterExitCode']==0 and worker['workerDead'] and worker['frames']==65917
    pair=worker['pair'][1]
    tasks=[dict(id='branding-middle',video=pair['path'],videoSha256=pair['sha256'],frames=worker['frames'],points={f:['original-branding-middle-not-in-prior3168'] for f in [30,60,90]})]
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
