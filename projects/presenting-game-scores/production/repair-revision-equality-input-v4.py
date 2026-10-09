"""One source-only correction; reuse all unchanged inputs, PCM and QA pixels."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,os,re,subprocess,traceback,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).parent;B=P/'revision-balatro60-v2'
OUT=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/selected-inputs-v4'
EP=B/'selected-input-preflight-execution-v4.json';FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args();resource=read(ROOT/a.resource)
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<180
assert not EP.exists() and not OUT.exists()
prior=read(B/'selected-input-preflight-v3.json');execution=read(B/'selected-input-preflight-execution-v3.json')
assert execution['exitCode']==execution['outerExitCode']==0 and execution['outerExitDirectlyObserved']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
for row in [*prior['segments'],*prior['samples'],*prior['boards']]:assert sha(ROOT/row['path'])==row['sha256']
plan=read(ROOT/prior['plan']);caption=read(ROOT/prior['captionCandidate']);oldplan=copy.deepcopy(plan)
cut=next(s for s in plan['segments'] if s['id']=='classic-02-equality-remainder')
assert (cut['sourceStartFrame'],cut['sourceEndFrameExclusive'],cut['frames'])==(1625,2100,1140)
assert sha(Path(cut['sourcePath']))==cut['sourceSha256']
evidence=[]
for name,observation in [('classic-002057.jpg','LINES9/11; disproves old equality annotation.'),('classic-002307.jpg','LINES12/12; SCORE2500/1413, signed1087.'),('classic-002350.jpg','LINES12/12; SCORE2502/1508, signed994.'),('modern-002915.jpg','LINES27/27; SCORE14096/17016, signed2920. Existing modern cut remains valid.')]:
 p=ROOT/'shared/output/presenting-game-scores/native-framing-v2'/name;evidence.append(dict(path=rel(p),sha256=sha(p),directlyRead=True,observation=observation))
correction=dict(schemaVersion=1,recordedAt=now(),oldAnnotationDisproved=True,oldBank=oldplan['bank'],oldBankSha256=oldplan['bankSha256'],
 previousPlan=prior['plan'],previousPlanSha256=prior['planSha256'],directlyReadEvidence=evidence,
 replacement=dict(sourceStartFrame=2050,sourceEndFrameExclusive=2525,nativeStartPts=2050000,nativeEndPtsExclusive=2525000,nativeTimebase='1/25000',seconds=[82,101],frames60fps=1140,
 equalityNativeFrame=2307,equalityNativePts=2307000,equalitySecondsIntoCut=10.28,visible='Both12 lines with different scores; normal piece placement before/after.'),
 noPcmChange=True,noCaptionTextOrClockChange=True,noBlackSceneChange=True,noRatioOrDurationChange=True,sourceAudio=False,loop=False,slowdown=False,
 currentCuePixelsApproved=False,allFinalPixels=False,humanListening='pending',publicRights='pending',newImagesGit=0)
cp=B/'source-equality-correction-v1.json';save(cp,correction)
cut.update(sourceStartFrame=2050,sourceEndFrameExclusive=2525,nativeStartPts=2050000,sourceBankCutId='classic-equality-corrected-v1',sourceCorrection=rel(cp),sourceCorrectionSha256=sha(cp),visibleAction='At nativef2307 both LINES12, scores2500/1413 and signed1087; subsequent equal12 samples have changing scores.')
next(s for s in plan['segments'] if s['id']=='black-03-equal-counts')['narrationConnection']='Preserve complete narration; nativef2307 equality at10.28s of corrected cut, near the guide asking viewers to compare line counts. Oldf2057 annotation disproved.'
next(s for s in plan['segments'] if s['id']=='classic-02-early-audit-prefix').update(visibleAction='Persistent LINES and SCORE read separately during placement; this audit prefix does not claim equal counts.',diagramConnection='Audit what is counted and how it is evaluated.')
plan.update(schemaVersion=4,preparedAt=now(),sourceCorrection=rel(cp),sourceCorrectionSha256=sha(cp),previousCandidate=prior['plan'],previousCandidateSha256=prior['planSha256'])
pp=B/'measured-editorial-candidate-v4.json';save(pp,plan)
capdir=B/'caption-candidate-v5';capdir.mkdir();caption.update(plan=rel(pp),planSha256=sha(pp),sourceOnlyRepair=rel(cp),allLiteralTextsAndTimingUnchanged=True)
cap=capdir/'captions.json';save(cap,caption)
for lang in ['ko','en']:(capdir/f'candidate.{lang}.srt').write_bytes((ROOT/prior['captionCandidate']).with_name(f'candidate.{lang}.srt').read_bytes())
OUT.mkdir();QA=OUT/'qa';QA.mkdir();(OUT/'logs').mkdir();p=psutil.Process()
s=dict(schemaVersion=4,startedAt=now(),pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),sessionId=None,resource=a.resource,plan=rel(pp),planSha256=sha(pp),captionCandidate=rel(cap),captionCandidateSha256=sha(cap),cpuThreads=2,gpuJobs=0,singleJob=True,status='source-only-equality-repair-running',operations=[],exitCode=None,allFinalPixels=False,qa=False,collected=False,private=False,imagesGitAdded=0)
def checkpoint():
 sp=B/'selected-input-preflight-execution-v4.session.json'
 if sp.exists():s['sessionId']=read(sp)['sessionId']
 save(EP,s);c=read(P/'latest-checkpoint.json');c.update(recordedAt=now(),stage=s['status'],ownedJob=dict(state=rel(EP),pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],sessionId=s['sessionId'],exitCode=s['exitCode'],activeOperation=s.get('activeOperation'),cpuThreads=2,gpu=0),sourceOnlyRepair=rel(cp),nextAction='Directly review only corrected classic cue pixels and exact numeric anchors; retain unchanged707 samples/reviews. Then finish remaining input boards and adopt mix. Final mixed ASR/pair/QA/upload/Git pending.');save(P/'latest-checkpoint.json',c)
 qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qpath.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items'] if x['slug']=='presenting-game-scores');item.update(stage=s['status'],currentExecution=c['ownedJob'],sourceOnlyRepair=rel(cp),nextAction=c['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
  if qpath.read_text('utf-8-sig')==raw:save(qpath,q);break
 else:raise RuntimeError('Concurrent queue changed; preserve foreign work.')
def run(exe,args,kind):
 cmd=[str(exe),*map(str,args)];log=OUT/'logs'/f'{len(s["operations"])+1:03d}-{kind}.log';op=dict(kind=kind,command=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8') as f:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);op.update(pid=child.pid,createTime=psutil.Process(child.pid).create_time());s['activeOperation']=op;checkpoint();code=child.wait()
 op.update(exitCode=code,finishedAt=now());s['activeOperation']=None;checkpoint();assert code==0,log
 return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-nostdin','-v','info','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
try:
 checkpoint();dest=OUT/'classic-equality-corrected.mp4'
 vf='trim=start_pts=2050000:end_pts=2525000,setpts=PTS-2050000,split=2[b][f];[b]gblur=sigma=24:steps=2[bg];[f]crop=1920:960:0:120[fg];[bg][fg]overlay=0:0:shortest=1,tpad=stop_mode=clone:stop=1,fps=60:start_time=0:round=near,trim=end_frame=1140,settb=1/90000,setpts=N*1500,setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
 ff(['-reinit_filter','0','-i',cut['sourcePath'],'-filter_complex',vf,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-frames:v','1140','-fps_mode','cfr','-r','60','-video_track_timescale','90000','-movflags','+faststart',dest],'encode-one-classic-input')
 segments=copy.deepcopy(prior['segments'])
 for row in segments:
  if row['id']==cut['id']:row.update(cut,path=rel(dest),sha256=sha(dest),previousInputPath=row['path'],previousInputSha256=row['sha256'],sourceOnlyCorrection=True)
  else:row['reusedUnchangedCurrentInput']=True
 listing=OUT/'concat-body.txt';listing.write_text('\n'.join("file '"+(ROOT/x['path']).as_posix()+"'" for x in segments)+'\n','utf-8')
 body=OUT/'body.silent.mp4';ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-map_metadata','-1','-c:v','copy','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',body],'concat-body-copy')
 info=json.loads(run(FP,['-v','error','-threads','2','-select_streams','v:0','-show_frames','-show_streams','-show_entries','frame=best_effort_timestamp,width,height:stream=time_base,avg_frame_rate,nb_frames,duration_ts','-of','json',body],'probe-all-body-PTS'))
 assert len(info['frames'])==19268 and info['streams'][0]['time_base']=='1/90000';assert all(f['best_effort_timestamp']==i*1500 and (f['width'],f['height'])==(1920,1080) for i,f in enumerate(info['frames']))
 ff(['-i',body,'-map','0:v:0','-an','-f','null','-'],'whole-body-decode')
 planned=copy.deepcopy(prior['samples']);a0,b0=cut['startFrame']-120,cut['endFrameExclusive']-120
 extra=[dict(frame=3639,pts=3639*1500,reasons=[dict(segment='corrected-classic-native2307-LINES12/12')]),dict(frame=8599,pts=8599*1500,reasons=[dict(segment='existing-modern-native2915-27/27-2920')])]
 extra=[x for x in extra if x['frame'] not in {v['frame'] for v in planned}];planned.extend(extra)
 changed=sorted([x for x in planned if a0<=x['frame']<b0 or x in extra],key=lambda x:x['pts'])
 ass=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/selected-inputs-v3/candidate-body.ko.ass'
 expression='+'.join(f'eq(pts\\,{v["pts"]})' for v in changed)
 log=ff(['-reinit_filter','0','-i',body,'-vf',f"subtitles=filename='{rel(ass)}',select={expression},showinfo",'-fps_mode','vfr','-threads','2',QA/'changed-%04d.png'],'extract-only-corrected-cues-and-numeric-anchors')
 observed=[int(v) for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',log)];assert observed==[x['pts'] for x in changed]
 files=sorted(QA.glob('changed-*.png'));assert len(files)==len(changed)
 for row,path in zip(changed,files):row.update(path=rel(path),sha256=sha(path),newPixels=True)
 boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
 for i in range(0,len(planned),6):
  rows=planned[i:i+6];old=prior['boards'][i//6] if i//6<len(prior['boards']) else None
  if old and not any(x.get('newPixels') for x in rows):boards.append({**old,'reusedUnchangedCurrentPixels':True});continue
  board=Image.new('RGB',(1920,1758),(18,18,18));draw=ImageDraw.Draw(board)
  for j,row in enumerate(rows):
   board.paste(Image.open(ROOT/row['path']).convert('RGB').resize((960,540)),((j%2)*960,(j//2)*586+40));expected=' / '.join(str(v.get('cue',v.get('segment',v.get('scene','')))) for v in row['reasons']);draw.text(((j%2)*960+10,(j//2)*586+7),f'f{row["frame"]} PTS{row["pts"]} {expected}'[:92],font=font,fill='white')
  path=QA/f'board-{i//6+1:03d}.jpg';board.save(path,quality=94);boards.append(dict(path=rel(path),sha256=sha(path),sampleFrames=[v['frame'] for v in rows],changedForSourceCorrection=True))
 proof={**prior,'schemaVersion':9,'completedAt':now(),'plan':rel(pp),'planSha256':sha(pp),'captionCandidate':rel(cap),'captionCandidateSha256':sha(cap),'bodyPath':rel(body),'bodySha256':sha(body),'bodyProbe':info['streams'][0],'segments':segments,'samples':planned,'boards':boards,'sourceCorrection':rel(cp),'sourceCorrectionSha256':sha(cp),'newlyExtractedSampleCount':len(changed),'reusedSampleCount':len(planned)-len(changed),'priorPreflight':'projects/presenting-game-scores/production/revision-balatro60-v2/selected-input-preflight-v3.json','allInputCaptionPixelsReviewed':False,'allBoardsDirectlyRead':False}
 save(B/'selected-input-preflight-v4.json',proof);s.update(status='source-only-equality-repair-complete-direct-review-pending',exitCode=0,completedAt=now(),bodyPath=rel(body),bodySha256=sha(body),sampleCount=len(planned),boardCount=len(boards),changedBoardNumbers=[i+1 for i,x in enumerate(boards) if x.get('changedForSourceCorrection')],newlyExtractedSampleCount=len(changed));checkpoint();print(json.dumps({k:s[k] for k in ['status','sampleCount','boardCount','changedBoardNumbers','newlyExtractedSampleCount']}))
except BaseException as e:
 s.update(status='source-only-equality-repair-failed-preserve-files',exitCode=1,error=repr(e),traceback=traceback.format_exc());checkpoint();raise
