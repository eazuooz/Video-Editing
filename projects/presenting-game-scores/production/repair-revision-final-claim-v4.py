"""Replace only one 19s source cut; reuse identical audio and unchanged GOPs.

Stream-copy at independently verified existing keyframe boundaries. Reuse of
older pixel observations requires exact decoded frame hashes outside this cut.
Every changed encoded cue is still subject to a new direct pixel review.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,os,subprocess,time,traceback,psutil,ctypes
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).parent;B=P/'revision-balatro60-v2'
OLD=B/'final-v3';W=B/'final-v4';EP=W/'source-only-pair-execution.json';SESSION=W/'source-only-pair-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
r=read(ROOT/a.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
assert not W.exists(),'Preserve any actual repair; never restart.'
source_review=read(B/'equality-claim-source-direct-review-v5.json');assert source_review['sourceSampleActionAndFramingApproved']
for row in source_review['directlyReadSamples']+source_review['directlyReadBoards']:assert sha(ROOT/row['path'])==row['sha256']
plan=read(OLD/'plan.json');mix=read(OLD/'mix-settings.json');asr=read(OLD/'full-mix-asr-review.json');prior=read(OLD/'review-pair-build.json')
assert asr['technicallyApproved'] and asr['all52WindowsDirectlyCompared'] and not asr['unresolvedContentDefects']
assert prior['planSha256']==asr['planSha256']==sha(OLD/'plan.json') and prior['identicalAacPayload']
assert sha(OLD/'final-mix.wav')==mix['wavSha256'] and sha(OLD/'final-mix.m4a')==mix['aacSha256']
for row in prior['records']:assert sha(ROOT/row['path'])==row['sha256']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
W.mkdir();(W/'chunks').mkdir();p=psutil.Process()
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
s=dict(startedAt=now(),pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),sessionId=None,resource=a.resource,
 status='source-only-final-claim-repair-running',cpuThreads=2,gpu=0,singleJob=True,operations=[],activeTask=None,exitCode=None,
 allFinalPixels=False,qa=False,collected=False,uploaded=False,newTts=0,newMixedAsr=0,researchControlChanges=0)
def checkpoint():
 if SESSION.exists():s['sessionId']=read(SESSION)['sessionId']
 s['observedAt']=now();save(EP,s)
 job={k:s[k] for k in ['pid','createTime','command','cwd','sessionId','status','exitCode','cpuThreads','gpu','activeTask']};job['state']=rel(EP)
 cp=read(P/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=s['status'],ownedJob=job,sourceOnlyFinalRepair=rel(EP),
 allFinalPixels=False,qa=False,collected=False,private=False,nextAction='Verify corrected encoded cues and unchanged-frame identity; review all remaining final boards, then collect/private upload/Git/09KST schedule.')
 save(P/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(12):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
  i.update(stage=s['status'],currentExecution=job,sourceOnlyFinalRepair=rel(EP),allFinalPixels=False,qa=False,collected=False,uploaded=False,nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
  time.sleep(.1)
 else:raise RuntimeError('Concurrent queue preserved')
def run(exe,args,kind):
 log=W/f'{len(s["operations"])+1:02d}-{kind}.log';cmd=[str(exe),*map(str,args)]
 op=dict(kind=kind,command=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8') as f:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  op.update(pid=child.pid,createTime=psutil.Process(child.pid).create_time());s['activeTask']=op;checkpoint();code=child.wait()
 op.update(exitCode=code,endedAt=now());s['activeTask']=None;checkpoint();assert code==0,f'{kind}: preserve {log}'
 return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-nostdin','-v','error','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def probe(path,N,audio=False):
 j=json.loads(run(FP,['-v','error','-threads','2','-show_streams','-show_packets','-show_entries','stream=codec_type,width,height,avg_frame_rate,time_base,nb_frames,duration_ts:packet=stream_index,pts,duration','-of','json',path],'probe-exact-PTS'))
 v=next(x for x in j['streams'] if x['codec_type']=='video');vi=j['streams'].index(v);pk=[x for x in j['packets'] if x['stream_index']==vi]
 assert (v['width'],v['height'],v['avg_frame_rate'],v['time_base'],int(v['nb_frames']),int(v['duration_ts']))==(1920,1080,'60/1','1/90000',N,N*1500),(path,v)
 assert len(pk)==N and sorted(int(x['pts']) for x in pk)==list(range(0,N*1500,1500)) and all(int(x['duration'])==1500 for x in pk)
 assert len(j['streams'])==(2 if audio else 1)
 return dict(frames=N,timebase='1/90000',ptsStep=1500,allPacketPtsExact=True,probeStreams=j['streams'])
def concat(paths,dst,kind):
 listing=W/f'{kind}.txt';listing.write_text('\n'.join("file '"+x.as_posix()+"'" for x in paths)+'\n','utf-8')
 ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-c:v','copy','-map_metadata','-1','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',dst],kind)
def hashes(path,kind):
 dst=W/f'{kind}.framemd5'
 ff(['-i',path,'-map','0:v:0','-an','-c:v','rawvideo','-pix_fmt','yuv420p','-threads','2','-f','framemd5',dst],kind)
 rows=[x.split(',') for x in dst.read_text('utf-8-sig').splitlines() if x and not x.startswith('#')]
 assert len(rows)==19988
 return [x[-1].strip() for x in rows],rel(dst),sha(dst)
try:
 checkpoint();correction=dict(recordedAt=now(),previousDefect=rel(OLD/'equality-claim-pixel-defect-v1.json'),previousDefectSha256=sha(OLD/'equality-claim-pixel-defect-v1.json'),
 sourceReview=rel(B/'equality-claim-source-direct-review-v5.json'),sourceReviewSha256=sha(B/'equality-claim-source-direct-review-v5.json'),
 replacementNativeFrames=[2250,2725],replacementNativePts=[2250000,2725000],replacementSeconds=[90,109],finalFrames=[3142,4282],
 claimFinalFrames=[3315,3509],claimNativeSeconds=[92.8833333333333,96.1166666666667],claimObservedLines=[12,12],
 guideStartsNativeSeconds=100.145,guideStartObservedLines=[13,13],guideDoesNotClaimPersistentEquality=True,
 pcmUnchanged=True,captionTextAndClockUnchanged=True,ratiosAndDurationUnchanged=True,loop=False,slowdown=False,sourceAudio=False,
 finalEncodedClaimApproved=False,allFinalPixels=False,publicRightsApproved=False,humanListeningApproved=False)
 save(W/'source-correction.json',correction)
 newplan=copy.deepcopy(plan)
 for group in ['segments','selectedInputSegments']:
  cut=next(x for x in newplan[group] if x['id']=='classic-02-equality-remainder')
  assert (cut['startFrame'],cut['frames'])==(3142,1140)
  cut.update(sourceStartFrame=2250,sourceEndFrameExclusive=2725,nativeStartPts=2250000,sourceCorrection=rel(W/'source-correction.json'),sourceCorrectionSha256=sha(W/'source-correction.json'),
   sourceBankCutId='classic-equality-claim-corrected-v2',visibleAction='At current claim cues33/34 both LINES12 with unequal scores; guide begins13/13 then continues changing normal placements.',finalCuePixelsReviewed=False)
 newplan.update(previousPlan=rel(OLD/'plan.json'),previousPlanSha256=sha(OLD/'plan.json'),preparedAt=now(),sourceOnlyClaimRepair=rel(W/'source-correction.json'),allInputSegmentCaptionPixelsReviewed=False)
 source=ROOT/source_review['source'];assert sha(source)==source_review['sourceSha256']
 fixed=W/'classic-equality-corrected.silent.mp4'
 base='trim=start_pts=2250000:end_pts=2725000,setpts=PTS-2250000,split=2[b][f];[b]gblur=sigma=24:steps=2[bg];[f]crop=1920:960:0:120[fg];[bg][fg]overlay=0:0:shortest=1,tpad=stop_mode=clone:stop=1,fps=60:start_time=0:round=near,trim=end_frame=1140,settb=1/90000,setpts=N*1500,setsar=1,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
 ff(['-reinit_filter','0','-i',source,'-filter_complex',base,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-frames:v','1140','-fps_mode','cfr','-r','60','-video_track_timescale','90000','-movflags','+faststart',fixed],'encode-one-normal-speed-source')
 probe(fixed,1140)
 for group in ['segments','selectedInputSegments']:
  cut=next(x for x in newplan[group] if x['id']=='classic-02-equality-remainder')
  if 'path' in cut:cut.update(previousInputPath=cut['path'],previousInputSha256=cut['sha256'],path=rel(fixed),sha256=sha(fixed))
 paths=[ROOT/row['path'] if row['id']!='classic-02-equality-remainder' else fixed for row in plan['selectedInputSegments']]
 for row,path in zip(plan['selectedInputSegments'],paths):
  if row['id']!='classic-02-equality-remainder':assert sha(path)==row['sha256']
 visual=read(OLD/'visual-build.json');intro=ROOT/visual['retainedIntro']['path'];member=ROOT/visual['retainedMember']['path']
 assert sha(intro)==visual['retainedIntro']['sha256'] and sha(member)==visual['retainedMember']['sha256']
 silent=W/'silent-visual.mp4';concat([intro,*paths,member],silent,'concat-retained-clean-inputs');probe(silent,19988)
 save(W/'plan.json',newplan)
 for name in ['captions.ko.ass','presenting-game-scores.ko.srt','presenting-game-scores.en.srt']:(W/name).write_bytes((OLD/name).read_bytes())
 audio=dict(recordedAt=now(),previousPlanSha256=sha(OLD/'plan.json'),planSha256=sha(W/'plan.json'),voicePlacementsIdentical=newplan['voicePlacements']==plan['voicePlacements'],
  wavPath=rel(OLD/'final-mix.wav'),wavSha256=sha(OLD/'final-mix.wav'),aacPath=rel(OLD/'final-mix.m4a'),aacSha256=sha(OLD/'final-mix.m4a'),
  currentMixedAsrReview=rel(OLD/'full-mix-asr-review.json'),currentMixedAsrReviewSha256=sha(OLD/'full-mix-asr-review.json'),all52CurrentIdenticalAudioWindowsApproved=True,
  all52WindowsDirectlyCompared=True,unresolvedContentDefects=[],humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,newTts=0,newAsr=0)
 assert audio['voicePlacementsIdentical'];save(W/'audio-identity-provenance.json',audio)
 original=ROOT/next(x['path'] for x in prior['records'] if '.captioned.' in x['path'])
 # Segment demuxed GOPs exactly at the two observed existing I-frame boundaries.
 ff(['-i',original,'-map','0:v:0','-an','-c:v','copy','-f','segment','-segment_times','52.366666666667,71.366666666667','-segment_time_delta','0.0083333333',
  '-reset_timestamps','1','-avoid_negative_ts','disabled','-segment_format','mp4','-segment_format_options','video_track_timescale=90000',W/'chunks/old-%02d.mp4'],'copy-existing-three-GOP-regions')
 chunks=[W/f'chunks/old-{i:02d}.mp4' for i in range(3)]
 assert len(list((W/'chunks').glob('old-*.mp4')))==3
 for path,N in zip(chunks,[3142,1140,15706]):probe(path,N)
 replacement=W/'chunks/replacement-captioned.mp4'
 vf=f"settb=1/90000,setpts=PTS+4713000,ass={rel(OLD/'captions.ko.ass')},setpts=PTS-4713000"
 ff(['-reinit_filter','0','-i',fixed,'-vf',vf,'-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-frames:v','1140','-fps_mode','passthrough','-video_track_timescale','90000','-movflags','+faststart',replacement],'encode-only-corrected-fixed-caption-region');probe(replacement,1140)
 capvideo=W/'captioned.silent.mp4';concat([chunks[0],replacement,chunks[2]],capvideo,'concat-unchanged-caption-GOPs');probe(capvideo,19988)
 records=[]
 for video,name in [(silent,'clean'),(capvideo,'captioned')]:
  dst=W/f'presenting-game-scores.{name}.mp4'
  ff(['-i',video,'-i',OLD/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-map_metadata','-1','-video_track_timescale','90000','-movflags','+faststart',dst],f'mux-identical-{name}-AAC')
  checks=probe(dst,19988,audio=True);log=ff(['-i',dst,'-f','null','-'],f'whole-{name}-decode');assert not log.strip()
  payload=ff(['-i',dst,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],f'{name}-AAC-hash').strip()
  assert payload==prior['records'][0]['aacPayloadHash']
  records.append(dict(path=rel(dst),sha256=sha(dst),aacPayloadHash=payload,wholeDecodeExitCode=0,**checks))
 oldhash,oldmd5,oldmd5sha=hashes(original,'old-captioned-decoded-frame-hashes')
 newhash,newmd5,newmd5sha=hashes(W/'presenting-game-scores.captioned.mp4','new-captioned-decoded-frame-hashes')
 differences=[i for i,(x,y) in enumerate(zip(oldhash,newhash)) if x!=y]
 assert differences and all(3142<=i<4282 for i in differences),f'Unexpected changed pixels outside corrected cut: {differences[:20]}'
 identity=dict(recordedAt=now(),oldSourceSha256=sha(original),newSourceSha256=records[1]['sha256'],oldFrameHashFile=oldmd5,oldFrameHashFileSha256=oldmd5sha,
  newFrameHashFile=newmd5,newFrameHashFileSha256=newmd5sha,changedFrames=differences,unchangedFrameRanges=[[0,3142],[4282,19988]],
  all18848OutsideCutDecodedFramesIdentical=True,allFramePtsVerified=True,reuseScope='Exact decoded pixels outside corrected cut only; historical unresolved claim remains until new encoded review.',allFinalPixels=False)
 save(W/'unchanged-pixel-identity.json',identity)
 save(W/'review-pair-build.json',dict(createdAt=now(),planSha256=sha(W/'plan.json'),captionAssSha256=sha(W/'captions.ko.ass'),sourceMixAacSha256=mix['aacSha256'],
  records=records,frames=19988,seconds=19988/60,identicalAacPayload=True,inheritedSameAacLufs=float(mix['finalAacMeasurement']['input_i']),
  inheritedSameAacTruePeakDbtp=float(mix['finalAacMeasurement']['input_tp']),pixelIdentity=rel(W/'unchanged-pixel-identity.json'),allFinalFixedCaptionPixelsReviewed=False,qaApproved=False))
 s.update(status='source-only-final-pair-complete-awaiting-corrected-encoded-review',exitCode=0,completedAt=now(),pairRendered=True,
  identicalAacPayload=True,all18848OutsideCutDecodedFramesIdentical=True,allFinalPixels=False);checkpoint()
 print(json.dumps(dict(exitCode=0,frames=19988,unchangedDecodedFrames=18848,changedFrames=len(differences),allFinalPixels=False)))
except BaseException:
 s.update(status='source-only-final-claim-repair-failed-preserve',exitCode=1,error=traceback.format_exc(),endedAt=now());checkpoint();raise
