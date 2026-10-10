"""Serial CPU2: repair only 13 shared HUD shots and one measured label scene.
Reuse every unchanged segment/sample byte; extract only changed planned pixels.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,re,subprocess,time,traceback
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/character-parameters/selected-inputs-v4';STATE=BASE/'selected-input-repair-execution-v4.json';SESSION=BASE/'selected-input-repair-execution-v4.session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args();resource=ROOT/args.resource;r=read(resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
assert not OUT.exists() and not STATE.exists(),'Inspect actual checkpoint, preserve all files'
OLD=BASE/'selected-input-preflight-v3.json';old=read(OLD);review=read(BASE/'selected-input-direct-review-v3.json');export=read(BASE/'label-repair-export-execution-v4.json')
assert review['allPlannedSamplesDirectlyRead'] and not review['inputPixelApproval'] and review['preflightSha256']==sha(OLD)
assert export['exitCode']==0 and export['childExited'] and sha(ROOT/export['output'])==export['outputSha256']
for key in ('plan','captionCandidate'):assert sha(ROOT/old[key])==old[key+'Sha256']
for row in old['segments']:assert sha(ROOT/row['path'])==row['sha256']
for row in old['samples']:assert sha(ROOT/row['path'])==row['sha256']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir();(OUT/'segments').mkdir();(OUT/'logs').mkdir();QA=OUT/'qa';QA.mkdir()
p=psutil.Process();s=dict(schemaVersion=4,status='targeted-input-repair-running',pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),sessionId=None,startedAt=now(),exitCode=None,cpuThreads=2,gpuJobs=0,resource=args.resource,resourceSha256=sha(resource),operations=[],segments=[],changedSegments=[],reusedSegments=[],allInputPixels=False,finalTimingApproved=False,mixedAsrApproved=False,allFinalPixels=False,qa=False,collected=False,uploaded=False,actualId=None,sourceAudio=False,loop=False,slowdown=False,processMutations=0,rasterGitAdditions=0)
def checkpoint():
 if SESSION.exists():
  sess=read(SESSION)
  if sess['pid']==s['pid'] and abs(sess['createTime']-s['createTime'])<.01:s['sessionId']=sess['sessionId']
 s['updatedAt']=now();save(STATE,s)
 cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=s['status'],ownedJob=dict(pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],sessionId=s['sessionId'],state=rel(STATE),activeOperation=s.get('activeOperation'),completed=len(s['changedSegments']),total=14,cpuThreads=2,gpu=0,exitCode=s['exitCode']),nextAction='Finish only targeted input repairs; directly read every changed planned cue/cut/motion board. Reuse sealed v3 unchanged samples. Final timing/mix/pair/encoded QA/collection/private remain false.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(i for i in q['items']if i['slug']=='character-parameters');item.update(stage=s['status'],currentExecution=cp['ownedJob'],selectedInputExecution=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);return
  time.sleep(.15)
 raise RuntimeError('Concurrent queue write preserved')
def run(exe,args,kind):
 cmd=[str(exe),*map(str,args)];log=OUT/'logs'/f'{len(s["operations"])+1:03d}-{kind}.log';op=dict(kind=kind,command=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8')as f:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);op.update(pid=child.pid,createTime=psutil.Process(child.pid).create_time());s['activeOperation']=op;checkpoint();code=child.wait()
 op.update(exitCode=code,finishedAt=now());s['activeOperation']=None;checkpoint();assert code==0,f'{kind}: {log}'
 return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-nostdin','-hide_banner','-v','info','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def verify(path,frames):
 j=json.loads(run(FP,['-v','error','-show_streams','-show_format','-of','json',path],'probe'));v=j['streams'][0];assert len(j['streams'])==1 and (v['width'],v['height'],v['avg_frame_rate'],v['time_base'])==(1920,1080,'60/1','1/90000') and int(v['nb_frames'])==frames and int(v['duration_ts'])==frames*1500
 pts=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',path],'all-pts'))['frames'];assert [int(v['best_effort_timestamp'])for v in pts]==list(range(0,frames*1500,1500))
 ff(['-i',path,'-map','0:v:0','-an','-f','null','-'],'whole-decode');return j
try:
 checkpoint();verify(ROOT/export['output'],371)
 for row in old['segments']:
  segment=dict(row);changed=False;path=OUT/'segments'/f'{row["index"]:02}-{row["id"]}.mp4'
  if row['role']=='actual-existing-game' and row['sourceKey']=='gBbKFYZYvbc':
   assert sha(ROOT/row['sourcePath'])==row['sourceSha256']
   trim=f"trim=start_pts={row['nativeStartPts']}:end_pts={row['nativeEndPtsExclusive']},setpts=PTS-{row['nativeStartPts']},format=rgb24"
   filt=f'[0:v]{trim},split=5[main][bg][p1][p2][credit];'+\
    '[main]scale=1920:1080:flags=neighbor[full];[bg]crop=1280:55:0:602,gblur=sigma=12,scale=1920:160[back];'+\
    '[p1]crop=320:100:0:620,scale=449:140:flags=neighbor[left];[p2]crop=319:100:320:620,scale=447:140:flags=neighbor[right];'+\
    '[credit]crop=641:63:639:657,scale=462:45:flags=lanczos[c];[full][back]overlay=0:920:shortest=1:format=rgb[a];'+\
    '[a][left]overlay=24:940:shortest=1:format=rgb[b];[b][right]overlay=1476:940:shortest=1:format=rgb[d];[d][c]overlay=729:1035:shortest=1:format=rgb[framed];'+\
    f'[framed]tpad=stop_mode=clone:stop=1,fps=60:start_time=0:round=near,trim=end_frame={row["frames"]},settb=1/90000,setpts=N*1500,setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
   ff(['-reinit_filter','0','-i',ROOT/row['sourcePath'],'-filter_complex',filt,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-frames:v',row['frames'],'-fps_mode','cfr','-r','60','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',path],'repair-shared-HUD')
   segment.update(framingRepair=dict(version=4,sourcePlayerCrops=[[0,620,320,100],[320,620,319,100]],destinations=[[24,940,449,140],[1476,940,447,140]],sameFrameBlur=[0,920,1920,160],creditPreserved=True,nativeOriginalTransientClippingPreserved=True,noInventedPixels=True));changed=True
  elif row['id']=='02-common-baseline-04-explanation':
   ff(['-reinit_filter','0','-i',ROOT/export['output'],'-map','0:v:0','-an','-map_metadata','-1','-vf','trim=start_frame=0:end_frame=370,settb=1/90000,setpts=N*1500,setsar=1,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-frames:v','370','-fps_mode','passthrough','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',path],'replace-only-label-scene')
   segment.update(engine='motion-canvas/src/projects/character-parameters/spatial-character-explanation-measured-v4.tsx',engineSha256=sha(ROOT/'motion-canvas/src/projects/character-parameters/spatial-character-explanation-measured-v4.tsx'),blackSourceStartFrame=0,blackSourceEndFrameExclusive=370,labelRepair=True);changed=True
  if changed:
   segment.update(path=rel(path),sha256=sha(path),probe=verify(path,row['frames']),allPtsVerified=True,wholeDecodeExitCode=0,priorPath=row['path'],priorSha256=row['sha256']);s['changedSegments'].append(row['id'])
  else:s['reusedSegments'].append(row['id']);segment['reusedWithoutRegeneration']=True
  s['segments'].append(segment);checkpoint()
 assert len(s['changedSegments'])==14 and len(s['reusedSegments'])==27
 listing=OUT/'concat-body.txt';listing.write_text('\n'.join("file '"+(ROOT/x['path']).as_posix()+"'"for x in s['segments'])+'\n','utf-8');body=OUT/'body.silent.mp4'
 ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-map_metadata','-1','-c:v','copy','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',body],'concat-repaired-body');bp=verify(body,22677)
 changed_ids=set(s['changedSegments']);changed=[dict(x)for x in old['samples']if any(seg['id']in changed_ids and seg['startFrame']-120<=x['frame']<seg['endFrameExclusive']-120 for seg in s['segments'])]
 assert changed and all(x['pts']==x['frame']*1500 for x in changed)
 ass=ROOT/'shared/output/character-parameters/selected-inputs-v3/candidate-body.ko.ass';select='+'.join(f'eq(pts\\,{x["pts"]})'for x in changed)
 log=ff(['-reinit_filter','0','-i',body,'-vf',f"subtitles=filename='{rel(ass)}',select={select},showinfo",'-fps_mode','vfr','-threads','2',QA/'changed-%04d.png'],'extract-only-changed-planned-pixels')
 observed=[int(x)for x in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',log)];assert observed==[x['pts']for x in changed]
 files=sorted(QA.glob('changed-*.png'));assert len(files)==len(changed)
 for row,path in zip(changed,files):row.update(path=rel(path),sha256=sha(path),requiresNewDirectReview=True)
 changed_byframe={x['frame']:x for x in changed};samples=[changed_byframe.get(x['frame'],dict(x,reusedDirectReview='projects/character-parameters/production/selected-input-direct-review-v3.json'))for x in old['samples']]
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);boards=[]
 for i in range(0,len(changed),6):
  board=Image.new('RGB',(1920,1758),(18,18,18));draw=ImageDraw.Draw(board)
  for j,row in enumerate(changed[i:i+6]):
   board.paste(Image.open(ROOT/row['path']).convert('RGB').resize((960,540)),((j%2)*960,(j//2)*586+40));draw.text(((j%2)*960+10,(j//2)*586+7),f'f{row["frame"]} PTS{row["pts"]}',font=font,fill='white')
  path=QA/f'board-{i//6+1:03d}.jpg';board.save(path,quality=94);boards.append(dict(path=rel(path),sha256=sha(path),sampleFrames=[x['frame']for x in changed[i:i+6]]))
 proof=dict(old,schemaVersion=4,completedAt=now(),previousPreflight=rel(OLD),previousPreflightSha256=sha(OLD),previousDirectReview='projects/character-parameters/production/selected-input-direct-review-v3.json',bodyPath=rel(body),bodySha256=sha(body),bodyProbe=bp,segments=s['segments'],samples=samples,boards=boards,changedSamples=len(changed),reusedSamples=len(samples)-len(changed),changedSegmentIds=s['changedSegments'],reusedSegmentIds=s['reusedSegments'],allBoardsDirectlyRead=False,allInputCaptionPixelsReviewed=False,allFinalPixels=False,finalTimingApproved=False,finalMixedAsrApproved=False,allContinuousFramesReviewed=False,sourceAcquisitionRepeated=False)
 save(BASE/'selected-input-preflight-v4.json',proof);s.update(status='targeted-input-repair-complete-changed-direct-review-pending',exitCode=0,finishedAt=now(),changedSamples=len(changed),reusedSamples=len(samples)-len(changed),boards=len(boards),bodyPath=rel(body),bodySha256=sha(body));checkpoint();print(json.dumps(dict(changedSegments=14,reusedSegments=27,changedSamples=len(changed),reusedSamples=len(samples)-len(changed),boards=len(boards),bodyFrames=22677,exitCode=0)),flush=True)
except BaseException as e:
 s.update(status='targeted-input-repair-failed-preserve-every-output',exitCode=1,failedAt=now(),error=repr(e),traceback=traceback.format_exc());checkpoint();raise
