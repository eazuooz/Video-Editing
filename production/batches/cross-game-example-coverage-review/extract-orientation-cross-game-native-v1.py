"""One CPU2/GPU0 exact source-PTS audit of three candidate game intervals."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, re, subprocess, psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,o):
    tmp=p.with_name(p.name+f'.{os.getpid()}.writing')
    tmp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
statepath=O/'cross-game-native-extraction-v1.json'
sessionpath=statepath.with_name(statepath.stem+'.session.json')
dest=O/'cross-game-native-v1'
assert not statepath.exists() and not dest.exists(),'Reuse actual current worker/results; no re-extraction.'
resource=read(ROOT/args.resource)
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyCpuJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
tts=read(O/'narration-tts-execution-v2.json')
for row in tts['protectedInputs']+tts['results']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
playback=read(O/'cross-game-normal-playback-direct-review-v1.json')
assert len(playback['observations'])==4 and all(x['normalSpeedReachedRequestedEnd'] for x in playback['observations'])
plan=read(O/'cross-game-native-candidate-plan-v1.json')
bygame={x['game']:x for x in plan['candidates']}
windows={'descenders':(680,705,[(696,702,12)]),'trailmakers':(665,700,[(682,684,12)]),'space-engineers':(170,184,[(172,179,12)])}
me=psutil.Process()
state=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),
    sessionId=None,startedAt=now(),status='preparing-exact-source-PTS',cpuThreads=2,gpuJobs=0,
    resource=args.resource,exitCode=None,actualExitObserved=False,completedSources=0,totalSources=3,
    sourceSelectionApproved=False,allSamplesDirectlyRead=False)
dest.mkdir()
def checkpoint():
    if sessionpath.exists():
        session=read(sessionpath);assert session['pid']==me.pid and abs(session['createTime']-me.create_time())<.01
        state['sessionId']=session['sessionId']
    state['updatedAt']=now();save(statepath,state)
    cp=read(O/'latest-checkpoint.json')
    cp.update(recordedAt=now(),stage='cross-game-exact-native-audit',ownedJob={**state},activeOwnedWorkers=0 if state['exitCode'] is not None else 1)
    save(O/'latest-checkpoint.json',cp)
    path=B/'queue.json';before=path.read_bytes();q=read(path)
    q['currentOrientationReview'].update(stage=cp['stage'],ownedJob={**state},actualSession=state['sessionId'],activeOwnedWorkers=cp['activeOwnedWorkers'],
        next='Actual exit/worker absence/hash verification; directly read every new native sample before source selection or dependent narration.')
    q['updatedAt']=now();assert path.read_bytes()==before;save(path,q)
checkpoint()
all_samples=[];boards=[];source_records=[]
try:
    for game,(a,b,fine) in windows.items():
        row=bygame[game];source=ROOT/row['sourcePath'];assert sha(source)==row['sourceSha256']
        probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,time_base,start_pts','-of','json',str(source)],text=True))['streams'][0]
        assert probe['time_base']=='1/15360' and probe['avg_frame_rate']=='60/1' and probe['start_pts']==0
        first,last=a*60,b*60
        targets=set(range(first,last,30))|{first,last-1,(first+last-1)//2}
        for lo,hi,step in fine:targets.update(range(lo*60,hi*60,step));targets.add(hi*60-1)
        targets=sorted(targets)
        folder=dest/game;folder.mkdir()
        selector='+'.join(f'eq(pts,{f*256})' for f in targets)
        log=folder/'extract.log'
        cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1',
            '-ss',str(max(0,a-1)),'-copyts','-i',str(source),'-an',
            '-vf',f"select='{selector}',showinfo,scale=1280:720",'-fps_mode','passthrough',
            '-frames:v',str(len(targets)),'-threads','2','-compression_level','3',str(folder/'sample-%04d.png')]
        source_record=dict(game=game,sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],probe=probe,
            nativeIn=first,nativeOutExclusive=last,timeBase='1/15360',ptsStep=256,targetNativeFrames=targets,
            command=cmd,log=rel(log),browserOvershootUsedForOut=False,normalPlaybackReview='cross-game-normal-playback-direct-review-v1.json')
        save(folder/'plan.json',source_record)
        state.update(status='extracting-'+game,currentGame=game,log=rel(log),requestedSamples=len(targets))
        with log.open('x',encoding='utf-8') as file:
            proc=subprocess.Popen(cmd,stdout=file,stderr=subprocess.STDOUT,cwd=ROOT)
            state.update(ffmpegPid=proc.pid,ffmpegCreateTime=psutil.Process(proc.pid).create_time(),ffmpegCommandLine=cmd);checkpoint();rc=proc.wait()
        pts=[int(x) for x in re.findall(r'Parsed_showinfo_\d+.*?\bpts:\s*(-?\d+)',log.read_text('utf-8'))]
        files=sorted(folder.glob('sample-*.png'))
        assert rc==0 and pts==[f*256 for f in targets] and len(files)==len(targets),(game,rc,len(pts),len(targets))
        samples=[dict(game=game,path=rel(path),sha256=sha(path),nativeFrame=f,pts=f*256,seconds=f/60,
            sourceSha256=row['sourceSha256']) for f,path in zip(targets,files)]
        font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
        for offset in range(0,len(samples),5):
            group=samples[offset:offset+5]
            board=Image.new('RGB',(1280,392*3),'#161616');draw=ImageDraw.Draw(board)
            for j,sample in enumerate(group):
                x=(j%2)*640;y=(j//2)*392
                with Image.open(ROOT/sample['path']) as frame:board.paste(frame.resize((640,360)),(x,y))
                draw.text((x+6,y+364),f'{game} f{sample["nativeFrame"]} PTS{sample["pts"]} {sample["seconds"]:.3f}s',font=font,fill='white')
            path=folder/f'board-{offset//5+1:03}.png';board.save(path)
            boards.append(dict(game=game,path=rel(path),sha256=sha(path),samplePaths=[s['path'] for s in group]))
        source_record.update(ffmpegExitCode=rc,exactPtsMatched=True,sampleCount=len(samples))
        all_samples.extend(samples);source_records.append(source_record)
        state['completedSources']+=1;checkpoint()
    for row in tts['protectedInputs']+tts['results']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    manifest=dict(createdAt=now(),sources=source_records,samples=all_samples,boards=boards,
        exactSourcePtsVerified=True,allSamplesDirectlyRead=False,nativeInOutSelected=False,
        continuousAllFramesApproval=False,narrationTimedAnnotationsApproved=False,finalFourGameTeachingApproved=False,
        sourceOrHumanRightsApproval=False,newMediaCopied=0,foreignFilesChanged=0)
    save(dest/'manifest.json',manifest)
    state.update(exitCode=0,status='closed-awaiting-all-native-pixel-review',finishedAt=now(),
        manifest=rel(dest/'manifest.json'),sampleCount=len(all_samples),boardCount=len(boards));checkpoint()
    print(json.dumps(dict(samples=len(all_samples),boards=len(boards),sources=3,exactPtsMatched=True,exitCode=0)))
except BaseException as error:
    state.update(exitCode=1,status='failed-preserve-extraction-history',error=repr(error),finishedAt=now());checkpoint();raise
