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
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
DEST=ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/final-pixels-v2'
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
    pair=read(R/'final-pair-execution-v2.json');session=read(R/'final-pair-execution-v2.session.json')
    assert pair['exitCode']==0 and session['actualOuterExitCode']==0 and session['workerCurrentlyAlive']==False
    plan=read(R/'measured-additive-plan-v1.json');layout=read(R/'caption-layout-v1.json')
    srcrow=next(x for x in pair['pair'] if '.captioned.' in x['path']);source=ROOT/srcrow['path']
    assert sha(source)==srcrow['sha256'] and srcrow['wholeDecodeExitCode']==0 and srcrow['allPts1500Verified']
    sp=R/'final-pixel-execution-v2.json';assert not DEST.exists() and not sp.exists()
    DEST.mkdir(parents=True);me=psutil.Process()
    if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
    points={}
    def add(n,reason):
        if 0<=n<plan['totalFrames']:points.setdefault(int(n),[]).append(reason)
    for c in layout['cues']:
        a=math.ceil(c['start']*60-1e-7);b=math.ceil(c['end']*60-1e-7)-1
        assert b>=a
        for n,k in [(a,'first'),((a+b)//2,'middle'),(b,'last')]:add(n,f'cue{c["cue"]}:{k}:segment{c["start"]}-{c["end"]}')
    for c in plan['cuts']:
        for t in [c['timelineStart'],c['timelineEnd']]:
            for n in [round(t*60)-1,round(t*60),round(t*60)+1]:add(n,'cut-boundary:'+c['id'])
    for s in plan['scenes']:
        for n in [s['startFrame']-1,s['startFrame'],s['startFrame']+s['frames']-1]:add(n,'scene-boundary:'+s['id'])
    retained=read(R/'retained-annotation-render-execution-v1.json')
    scenes={s['id']:s for s in plan['scenes']}
    for w in retained['windows']:
        for v in w['samples']:add(scenes[w['scene']]['startFrame']+w['sceneLocalStart']+v['frame'],'retained-moving-guide:'+w['scene'])
    opening=read(R/'opening-overlay-pilot-execution-v3.json')
    for v in opening['preparedSamples']:add(scenes['00a']['startFrame']+847+v['frame'],'opening-moving-guide')
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
          allFinalPixelsApproved=False,qaApproved=False,next='Observe actual extraction exit and read every planned board/full-size defect plus continuous flow; no automatic pixel approval.')
        save(R/'latest-checkpoint.json',cp)
        qp=B/'queue.json';raw=qp.read_text('utf-8-sig');q=json.loads(raw)
        q['execution'].update(currentSlug='motion-sickness-games',stage=cp['stage'],ownedJob=cp['ownedJob'],next=cp['next'])
        next(x for x in q['items'] if x['slug']=='motion-sickness-games').update(status=cp['stage'],currentExecution=cp['ownedJob'])
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
        priorIndex=read(ROOT/'shared/output/unpublished-teaching-clarity-revision/motion/final-pixels-v1/index.json')
        priorReview=read(R/'final-pixel-direct-review-v1.json');assert priorReview['allListedSamplesDirectlyRead']
        assert [v['frame'] for v in samples]==[v['frame'] for v in priorIndex['samples']]
        originalByFrame={v['frame']:v for v in priorIndex['samples']}
        for s in samples:
            old=originalByFrame[s['frame']];assert sha(ROOT/old['path'])==old['sha256']
            same=s['sha256']==old['sha256']
            repaired=(4843<=s['frame']<7181) or (20165<=s['frame']<20568)
            s.update(priorSamplePath=old['path'],priorSampleSha256=old['sha256'],decodedPngByteIdenticalToReviewedV1=same,
                targetRepairRegion=repaired,reusedPriorDirectPixelObservation=same and not repaired,
                currentDirectPixelReviewRequired=not same or repaired)
        for b in boards:
            b['currentDirectPixelReviewRequired']=any(samples[i-1]['currentDirectPixelReviewRequired'] for i in b['sampleIndices'])
            b['allSamplesDecodedByteIdenticalToReviewedV1']=all(samples[i-1]['reusedPriorDirectPixelObservation'] for i in b['sampleIndices'])
        save(DEST/'v1-decoded-sample-comparison.json',dict(source=rel(source),sourceSha256=srcrow['sha256'],
            priorSourceSha256=priorIndex['sourceSha256'],samples=len(samples),byteIdentical=sum(v['decodedPngByteIdenticalToReviewedV1'] for v in samples),
            reusedDirectPixelObservations=sum(v['reusedPriorDirectPixelObservation'] for v in samples),
            requireCurrentDirectReview=sum(v['currentDirectPixelReviewRequired'] for v in samples),
            currentBoardsRequired=[b for b in boards if b['currentDirectPixelReviewRequired']],
            allFinalPixelsApproved=False,newGitImages=0))
        assert sha(source)==srcrow['sha256']
        save(DEST/'index.json',dict(source=rel(source),sourceSha256=sha(source),samples=samples,boards=boards,allExactAbsolutePtsVerified=True,
          all179CuesAndCutBoundariesIncluded=True,directReviewComplete=False,GitImagesAdded=0))
        state.update(status='final-encoded-pixel-extraction-closed-awaiting-direct-review',exitCode=0,finishedAt=now(),
          samples=len(samples),boards=boards,allExactAbsolutePtsVerified=True,index=rel(DEST/'index.json'),indexSha256=sha(DEST/'index.json'))
        checkpoint();print(json.dumps(dict(exitCode=0,samples=len(samples),boards=len(boards),pixelApproval=False)),flush=True)
    except BaseException:
        state.update(status='failed-final-pixel-extraction-preserve-local-output',exitCode=1,error=traceback.format_exc(),finishedAt=now());checkpoint();raise
if __name__=='__main__':main()
