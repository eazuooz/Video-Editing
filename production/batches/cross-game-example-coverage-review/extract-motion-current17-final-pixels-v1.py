"""Prepared exact absolute-PTS final cue/action/annotation pixel extraction.

Color metadata can reset filter n; only absolute decoded PTS selects frames.
No raster produced here is a Git asset or automatic visual approval.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,math,os,re,subprocess,traceback
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
DEST=ROOT/'shared/output/cross-game-example-coverage/motion/current17-final-pixels-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,o):
    t=p.with_name(p.name+'.writing');t.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
    resource=read(ROOT/args.resource)
    assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
    assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
    pair=read(R/'current17-final-pair-execution-v2.json');session=read(R/'current17-final-pair-execution-v2.session.json')
    assert pair['exitCode']==0 and session['actualOuterExitCode']==0 and session['workerCurrentlyAlive']==False
    plan=read(R/'measured-current17-plan-v2.json');layout=read(R/'caption-layout-v1.json')
    srcrow=next(x for x in pair['pair'] if '.captioned.' in x['path']);source=ROOT/srcrow['path']
    assert sha(source)==srcrow['sha256'] and srcrow['wholeDecodeExitCode']==0 and srcrow['allPts1500Verified']
    sp=R/'current17-final-pixel-execution-v1.json';assert not DEST.exists() and not sp.exists()
    DEST.mkdir(parents=True);me=psutil.Process()
    if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
    points={}
    def add(n,reason):
        if 0<=n<plan['totalFrames']:points.setdefault(int(n),[]).append(reason)
    for c in layout['cues']:
        a=math.ceil(c['start']*60-1e-7);b=math.ceil(c['end']*60-1e-7)-1
        assert b>=a
        for n,k in [(a,'first'),((a+b)//2,'middle'),(b,'last')]:add(n,f'cue{c["cue"]}:{k}:segment{c["start"]}-{c["end"]}')
    assembly=read(R/'current17-assembly-inputs-v2.json')
    for c in assembly['pieces']:
        for n in [c['startFrame']-1,c['startFrame'],c['startFrame']+1,c['endFrame']-1,c['endFrame'],c['endFrame']+1]:add(n,'cut-boundary:'+c['id'])
        if not c.get('retainedByteIdentical'):
            for n in range(c['startFrame'],c['endFrame'],60):add(n,'new-moving-piece-one-second:'+c['id'])
    for scene in plan['scenes']:
        for n in [scene['startFrame']-1,scene['startFrame'],scene['endFrame']-1]:add(n,'scene-boundary:'+scene['id'])
        for voice in scene.get('voicePlacements',[v for v in plan['voicePlacements'] if v['sceneId']==scene['id']]):
            a=voice['destinationStartSample']/400
            b=a+(voice['sourceEndSample']-voice['sourceStartSample'])/400
            for n in [int(a)-1,int(a),int(a)+1,int(b)-1,int(b),int(b)+1]:add(n,'exact-current-PCM-placement:'+scene['id'])
    for n in range(0,plan['totalFrames'],120):add(n,'whole-body-two-second-coverage')
    for n in [0,1,119,plan['totalFrames']-600,plan['totalFrames']-599,plan['totalFrames']-2,plan['totalFrames']-1]:add(n,'original-branding-member-boundary')
    selected=sorted(points)
    state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,
      startedAt=now(),status='extracting-absolute-PTS-final-captioned-pixels',exitCode=None,resource=resource,cpuThreads=2,gpuJobs=0,
      source=rel(source),sourceSha256=sha(source),frames=plan['totalFrames'],selectedFrames=len(selected),
      allFinalPixelsApproved=False,humanListeningApproved=False,researchManipulations=0,newGitImages=0)
    def checkpoint():
        side=sp.with_name(sp.stem+'.session.json')
        if side.exists():
            v=read(side);assert v['pid']==me.pid and abs(v['createTime']-me.create_time())<.01;state['sessionId']=v['sessionId']
        state['updatedAt']=now();save(sp,state)
        cp=read(R/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=state['status'],ownedJob=dict(pid=me.pid,createTime=me.create_time(),
          commandLine=me.cmdline(),cwd=me.cwd(),sessionId=state['sessionId'],state=rel(sp),cpuThreads=2,gpuJobs=0,exitCode=state['exitCode']),
          activeOwnedWorkers=0 if state['exitCode'] is not None else 1,allFinalPixelsApproved=False,qaApproved=False,next='Observe actual extraction exit and read every planned board/full-size defect plus continuous flow; no automatic pixel approval.')
        save(R/'latest-checkpoint.json',cp)
        qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
        q['currentMotionReview'].update(stage=cp['stage'],status=cp['stage'],activeOwnedWorkers=0 if state['exitCode'] is not None else 1,currentPixelExecution=rel(sp));q.update(next=cp['next'])
        assert qp.read_text('utf-8-sig')==raw;save(qp,q)
    checkpoint()
    try:
        expr='+'.join(f'eq(pts\\,{n*1500})' for n in selected)
        filt=DEST/'absolute-pts.filter.txt';filt.write_text(f'select={expr},showinfo','utf-8')
        cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-i',str(source),'-an',
          '-filter_script:v',str(filt),'-fps_mode','passthrough','-c:v','png','-threads','2',str(DEST/'frame-%05d.png')]
        state['actualCommand']=cmd;checkpoint()
        with (DEST/'extract.log').open('wb') as log:x=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=log).returncode
        state['extractionExitCode']=x;assert x==0
        logs=(DEST/'extract.log').read_text('utf-8',errors='replace')
        actual=[int(v) for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(-?\d+)',logs)]
        assert actual==[n*1500 for n in selected],('Absolute PTS mismatch',len(actual),len(selected))
        images=sorted(DEST.glob('frame-*.png'));assert len(images)==len(selected)
        samples=[dict(index=i+1,frame=n,pts=n*1500,seconds=n/60,reasons=points[n],path=rel(p),sha256=sha(p)) for i,(n,p) in enumerate(zip(selected,images))]
        boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',19)
        for base in range(0,len(samples),6):
            canvas=Image.new('RGB',(1920,828),'#161616');d=ImageDraw.Draw(canvas)
            group=samples[base:base+6]
            for j,s in enumerate(group):
                x=(j%3)*640;y=(j//3)*414
                with Image.open(ROOT/s['path']) as im:canvas.paste(im.convert('RGB').resize((640,360),Image.Resampling.LANCZOS),(x,y+54))
                d.text((x+8,y+4),f'{s["index"]:04d}  f{s["frame"]}  {s["seconds"]:.3f}s',font=font,fill='white')
                label=' | '.join(s['reasons'])[:61];d.text((x+8,y+28),label,font=font,fill='#FFD366')
            p=DEST/f'board-{base//6+1:03d}.jpg';canvas.save(p,quality=96,subsampling=0)
            boards.append(dict(path=rel(p),sha256=sha(p),sampleIndices=[s['index'] for s in group],directlyReviewed=False))
        assert sha(source)==srcrow['sha256']
        save(DEST/'index.json',dict(source=rel(source),sourceSha256=sha(source),samples=samples,boards=boards,allExactAbsolutePtsVerified=True,
          all220CuesAnd37PieceCutBoundariesIncluded=True,directReviewComplete=False,GitImagesAdded=0))
        state.update(status='final-encoded-pixel-extraction-closed-awaiting-direct-review',exitCode=0,finishedAt=now(),
          samples=len(samples),boards=boards,allExactAbsolutePtsVerified=True,index=rel(DEST/'index.json'),indexSha256=sha(DEST/'index.json'))
        checkpoint();print(json.dumps(dict(exitCode=0,samples=len(samples),boards=len(boards),pixelApproval=False)),flush=True)
    except BaseException:
        state.update(status='failed-final-pixel-extraction-preserve-local-output',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
if __name__=='__main__':main()
