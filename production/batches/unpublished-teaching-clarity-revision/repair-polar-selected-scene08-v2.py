"""Repair only two scene08 intervals; retain all unchanged pieces and samples."""
from pathlib import Path
from datetime import datetime, timezone
import os, json, re, hashlib, subprocess
import psutil
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/game-math-polar-3d/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/polar/selected-scene08-v2'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def main():
    old=json.loads((OUT/'selected-scene08-execution-v1.json').read_text(encoding='utf-8'))
    assert old['status']=='completed' and old['exitCode']==0
    held=json.loads((OUT/'remaining-annotation-sampled-review-v1.json').read_text(encoding='utf-8'))
    assert not held['scene08ReframeApproved']
    five=OUT/'five-moving-pilots-execution-v1.json'
    if five.exists():
        f=json.loads(five.read_text(encoding='utf-8'))
        assert f['status']=='completed' and f['exitCode']==0,'Wait for the existing owned CPU job, do not run concurrently.'
    source=ROOT/'shared/output/game-math-polar-lecture/sources/WJVRoLR6KvY.mp4'
    assert sha(source)==old['sourceSha256']
    LOCAL.mkdir(parents=True,exist_ok=True)
    statefile=OUT/'selected-scene08-execution-v2.json';assert not statefile.exists()
    cuts=[dict(old['cuts'][0]),
      {'sourceInFrame':22500,'frames':450,'sceneStartFrame':1560,'reason':'End at382.5s before jump-end helmet leaves the retained top crop.'},
      {'sourceInFrame':23340,'frames':413,'sceneStartFrame':2010,'reason':'Extend normal steering to395.883333s; existing native395s observation shows completed recovery and active riding.'},
      dict(old['cuts'][3])]
    assert sum(c['frames'] for c in cuts)==3743 and cuts[3]['sceneStartFrame']==2423
    state={'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'createTime':psutil.Process().create_time(),
      'commandLine':psutil.Process().cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','cuts':cuts,
      'sourceSha256':old['sourceSha256'],'previousSelectionSha256':old['sourceCandidateSha256'],
      'narrationChanged':False,'frames':3743,'baselineMutations':0,'sourceAudio':False,'loop':False,'slowdown':False,
      'footageSelectionFinalApproved':False,'annotationFinalApproved':False}
    def save():statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save();print(json.dumps({'pid':state['pid'],'createTime':state['createTime']}),flush=True)
    try:
        pieces=[]
        for j,c in enumerate(cuts):
            if j in [0,3]:
                p=ROOT/c['path'];assert sha(p)==c['sha256']
                c['reusedUnchangedPiece']=True;pieces.append(p);save();continue
            a=c['sourceInFrame']*256;b=(c['sourceInFrame']+c['frames'])*256
            p=LOCAL/f'source-{j+1}.mp4';assert not p.exists();log=LOCAL/f'source-{j+1}.log'
            vf=f"trim=start_pts={a}:end_pts={b},showinfo,setpts=PTS-STARTPTS,setsar=1,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='Descenders - MezzyGameplay | CC BY | edited excerpt, muted':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=808,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='youtu.be/WJVRoLR6KvY | creativecommons.org/licenses/by/4.0':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=834"
            cmd=[FF,'-hide_banner','-nostdin','-loglevel','info','-threads','2','-filter_threads','1','-copyts','-ss',str(c['sourceInFrame']/60-2),'-i',str(source),'-vf',vf,'-frames:v',str(c['frames']),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(p)]
            c['command']=cmd;save()
            with log.open('w',encoding='utf-8') as stream:r=subprocess.run(cmd,stdout=stream,stderr=stream,check=True)
            pts=[int(v) for v in re.findall(r' n:\s*\d+\s+pts:\s*(\d+)\s+pts_time:',log.read_text(encoding='utf-8'))]
            assert pts==list(range(a,b,256))
            c.update(exitCode=r.returncode,nativeFirstPts=pts[0],nativeLastPts=pts[-1],allNativePtsVerified=True,path=rel(p),sha256=sha(p),reusedUnchangedPiece=False)
            pieces.append(p);save()
        listing=LOCAL/'concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in pieces)+'\n',encoding='utf-8')
        clip=LOCAL/'scene08.source-selected.mp4';assert not clip.exists()
        subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-an','-video_track_timescale','90000','-movflags','+faststart',str(clip)],check=True)
        probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=pts','-of','json',str(clip)]))
        assert [int(f['pts']) for f in probe['frames']]==list(range(0,3743*1500,1500))
        records=[]
        for row in old['samples']:
            frame=row['frame']
            if 2010<=frame<2070:continue
            newframe=frame-60 if 2070<=frame<2423 else frame
            assert sha(ROOT/row['path'])==row['sha256']
            records.append(dict(row,frame=newframe,pts=newframe*1500,reusedExactSourceFrame=True,previousSceneFrame=frame))
        points=sorted(({2009,2011,2363,2370,2382,2394,2406,2418,2422}- {r['frame'] for r in records}))
        vf='select='+ '+'.join(f'eq(pts\\,{f*1500})' for f in points)
        cmd=[FF,'-hide_banner','-nostdin','-v','error','-threads','2','-filter_threads','1','-i',str(clip),'-vf',vf,'-frames:v',str(len(points)),'-fps_mode','passthrough',str(LOCAL/'changed-%03d.png')]
        subprocess.run(cmd,check=True)
        files=sorted(LOCAL.glob('changed-*.png'));assert len(files)==len(points)
        records += [{'frame':f,'pts':f*1500,'path':rel(p),'sha256':sha(p),'reusedExactSourceFrame':False} for f,p in zip(points,files)]
        records.sort(key=lambda r:r['frame']);assert len({r['frame'] for r in records})==len(records)
        changed=[r for r in records if 1560<=r['frame']<2423];boards=[]
        for n in range(0,len(changed),6):
            board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
            for j,r in enumerate(changed[n:n+6]):
                x=j%3*640;y=j//3*390
                with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
                d.text((x+8,y+7),f"repaired scene08 f{r['frame']} / {r['frame']/60:.3f}s",fill='white')
            p=LOCAL/f'changed-board-{n//6+1:02d}.png';board.save(p);boards.append({'path':rel(p),'sha256':sha(p)})
        snapshot=json.loads((OUT/'baseline-protected-sha-v1.json').read_text(encoding='utf-8'))
        assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
        state.update(status='completed',exitCode=0,finishedAt=datetime.now(timezone.utc).isoformat(),sourceCandidate=rel(clip),sourceCandidateSha256=sha(clip),allPts1500Verified=True,
          samples=records,changedRegionSamples=changed,changedRegionBoards=boards,newSamples=len(points),reusedSamples=len(records)-len(points),protectedBaselineUnchanged=True,
          selectionContinuousPixelApproval=False)
        save();print(json.dumps({'frames':3743,'newSamples':len(points),'changedRegionSamples':len(changed),'boards':len(boards),'exitCode':0}),flush=True)
    except Exception as e:state.update(status='failed',exitCode=1,exception=str(e));save();raise
if __name__=='__main__':main()
