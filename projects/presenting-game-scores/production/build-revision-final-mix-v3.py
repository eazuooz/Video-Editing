"""One serial CPU2 job: exact current PCM, continuous Nimbus, silent visual.

Refuse before state creation unless measured input pixels and current content
are reviewed. No TTS, source audio, research control or final speech approval.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, math, os, re, subprocess, sys, time, traceback
import numpy as np
import soundfile as sf
import psutil

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
FINAL=BASE/'revision-balatro60-v2/final-v3'; STATE=FINAL/'mix-execution.json'; SESSION=FINAL/'mix-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'); FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig')); now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
r=read(ROOT/a.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
assert not STATE.exists(), 'Continue actual checkpoint; never repeat completed work.'
plan_path=FINAL/'plan.json'; plan=read(plan_path);review_path=ROOT/plan['selectedInputReview'];review=read(review_path)
assert sha(review_path)==plan['selectedInputReviewSha256']
assert review['allBoardsDirectlyRead'] and review['sourceAllocationApproved'] and not review['unresolvedDefects']
assert plan['finalTimingApproved'] and plan['bodyRatioApproved'] and plan['allInputSegmentCaptionPixelsReviewed']
assert (plan['bodyFrames'],plan['finalFrames'],sum(p['samples'] for p in plan['voicePlacements']))==(19268,19988,6691203)
voice_selection=read(ROOT/plan['voiceSelection'])
assert sha(ROOT/plan['voiceSelection'])==plan['voiceSelectionSha256']
assert voice_selection['currentCompleteVoiceApproved'] and len(voice_selection['scenes'])==19
for row in voice_selection['scenes']:assert sha(ROOT/row['path'])==row['sha256']
assert sha(ROOT/plan['bodySilent'])==plan['bodySilentSha256']
music_approval=read(BASE.parent/'project.json')['audio']['backgroundMusic']; music=ROOT/music_approval['file']
assert music_approval['approvalStatus']=='approved-continuous-Nimbus-by-user-production-defaults'
assert sha(music)==music_approval['sha256']
intro=ROOT/'projects/game-reward-planning/production/final-v1/white-segments/branding.mp4'
member=ROOT/'projects/game-reward-planning/production/final-v1/white-segments/membership.mp4'
assert sha(intro)=='706a0738dcd160b80ace24e54e16c09604c0173aba095fcd221a227c541fffb2'
assert sha(member)=='181e5c5dd37672349542aa590629fe2f2d00a83f4cd3c811a29a21c029612123'
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','presenting-game-scores','--check'],cwd=ROOT,check=True)
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
p=psutil.Process();s=dict(schemaVersion=1,slug='presenting-game-scores',pid=p.pid,createTime=p.create_time(),
 command=p.cmdline(),cwd=p.cwd(),sessionId=None,startedAt=now(),status='current-PCM-Nimbus-mix-running',
 resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,plan=rel(plan_path),planSha256=sha(plan_path),
 operations=[],exitCode=None,newTts=0,sourceAudioStreams=0,researchControlChanges=0,
 finalMixedAsrApproved=False,humanWholeListening='pending',humanPronunciation='pending',allFinalPixels=False,collected=False,uploaded=False)
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==s['pid'] and abs(x['createTime']-s['createTime'])<.01:s['sessionId']=x['sessionId']
 s['observedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],
  sessionId=s['sessionId'],state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,activeTask=s.get('activeTask'),
  exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),finalMixExecution=rel(STATE),
  nextAction='Directly compare current mixed10 whole chapters and42 independent complete contexts, then guarded pair/final encoded pixels/QA/collection/private/Git.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items'] if x['slug']=='presenting-game-scores')
  i.update(stage=cp['stage'],currentExecution=job,currentJob=job,ownedJob=job,finalMixExecution=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 else:raise RuntimeError('Concurrent queue preserved; retry only checkpoint writing.')
def run(exe,args,kind):
 log=FINAL/f'mix-{len(s["operations"])+1:02d}-{kind}.log';cmd=[str(exe),*map(str,args)]
 op=dict(kind=kind,command=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8') as f:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  op.update(pid=child.pid,createTime=psutil.Process(child.pid).create_time());s['activeTask']=op;checkpoint();code=child.wait()
 op.update(exitCode=code,endedAt=now());s['activeTask']=None;checkpoint();assert code==0,f'{kind} exit{code}: preserve {log}'
 return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-hide_banner','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def scan(path,I=-16,TP=-2):
 out=ff(['-i',path,'-af',f'loudnorm=I={I}:TP={TP}:LRA=11:print_format=json','-f','null','-'],'loudness-scan')
 return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',out).group())
try:
 checkpoint();N=plan['finalFrames'];D=N/60;timeline=np.zeros(N*400,dtype='int16');occupied=np.zeros(N*400,dtype=bool)
 sources={};placements=[]
 for row in plan['voicePlacements']:
  src=ROOT/row['sourcePath'];assert sha(src)==row['sourceSha256']
  if row['voiceId'] not in sources:
   x,rate=sf.read(src,dtype='int16');assert rate==24000 and x.ndim==1;sources[row['voiceId']]=x
  x=sources[row['voiceId']][row['sourceStartSample']:row['sourceEndSampleExclusive']]
  a0=row['startSample'];b0=row['endSampleExclusive'];assert len(x)==row['samples']==b0-a0 and not occupied[a0:b0].any()
  timeline[a0:b0]=x;occupied[a0:b0]=True;assert np.array_equal(timeline[a0:b0],x)
  placements.append(dict(row,allSourcePcmSamplesIdentical=True))
 assert int(occupied.sum())==6691203
 for voice in voice_selection['scenes']:
  rows=[p for p in placements if p['voiceId']==voice['id']]
  stitched=np.concatenate([timeline[p['startSample']:p['endSampleExclusive']] for p in rows])
  assert np.array_equal(stitched,sources[voice['id']])
 assert not timeline[:48000].any() and not timeline[19388*400:].any()
 narration=FINAL/'narration-timed.wav';sf.write(narration,timeline,24000,subtype='PCM_16')
 back,rate=sf.read(narration,dtype='int16');assert rate==24000 and np.array_equal(back,timeline)
 save(FINAL/'pcm-timeline-preservation.json',dict(createdAt=now(),planSha256=sha(plan_path),voice=rel(narration),
  sha256=sha(narration),totalSamples=N*400,originalSamples=6691203,all19CurrentPcmSamplesIdentical=True,
  sourceCoverageExactlyOnce=True,placements=placements,newTts=0,speechTrimmed=False))
 raw=scan(narration);normal_pass=FINAL/'voice-normalized-pass.wav'
 lf=f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={raw['input_i']}:measured_TP={raw['input_tp']}:measured_LRA={raw['input_lra']}:measured_thresh={raw['input_thresh']}:offset={raw['target_offset']}:linear=true,aresample=48000,aformat=channel_layouts=stereo"
 ff(['-i',narration,'-af',lf,'-c:a','pcm_s16le',normal_pass],'two-pass-current-voice-normalization')
 x,rate=sf.read(normal_pass,dtype='int16',always_2d=True);assert rate==48000 and len(x)==N*800
 outside=int(np.count_nonzero(x[:96000])+np.count_nonzero(x[19388*800:]));x[:96000]=0;x[19388*800:]=0
 normalized=FINAL/'voice-normalized.wav';sf.write(normalized,x,48000,subtype='PCM_16')
 save(FINAL/'normalization-outside-body-silence.json',dict(createdAt=now(),originalPassSha256=sha(normal_pass),
  normalizedSha256=sha(normalized),outsideBodyNonzeroSamplesBefore=outside,
  changedOnlyBrandingAndMembership=True,allBodyNormalizedSamplesRetained=True))
 md=float(json.loads(run(FP,['-v','error','-show_format','-of','json',music],'Nimbus-probe'))['format']['duration'])
 original_music_sha=sha(music);count=math.ceil((D-1)/(md-1))
 if count>1:
  chain=';'.join(f"{'[0:a]' if k==1 else '[b'+str(k-1)+']'}[{k}:a]acrossfade=d=1:c1=tri:c2=tri[b{k}]" for k in range(1,count))
  continuous=FINAL/'nimbus-continuous.wav'
  ff([*sum((['-i',music] for _ in range(count)),[]),'-filter_complex',chain,'-map',f'[b{count-1}]','-c:a','pcm_s16le',continuous],'continuous-approved-Nimbus')
  music=continuous
 bg=FINAL/'bgm-before-ducking.wav'
 ff(['-i',music,'-af',f'atrim=duration={D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st={D-.45}:d=0.45','-c:a','pcm_s16le',bg],'background-level')
 premix=FINAL/'final-mix-before-master-level.wav';mix=FINAL/'final-mix.wav';aac=FINAL/'final-mix.m4a'
 filt='[0:a]asplit[n][d];[1:a][d]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=.80:level=false:latency=true[mix]'
 ff(['-i',normalized,'-i',bg,'-filter_complex',filt,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',premix],'current-Nimbus-ducked-premix')
 assert sf.info(premix).frames==N*800
 measured=scan(premix);gain=min(-16-float(measured['input_i']),-2-float(measured['input_tp']))
 assert -3<gain<3, measured
 ff(['-i',premix,'-af',f'volume={gain:.8f}dB','-c:a','pcm_s16le',mix],'measured-master-gain')
 assert sf.info(mix).frames==N*800
 ff(['-i',mix,'-c:a','aac','-b:a','192k',aac],'final-current-AAC')
 final=scan(aac,-16,-1.5);assert abs(float(final['input_i'])+16)<=.6 and float(final['input_tp'])<=-1.5,final
 save(FINAL/'mix-settings.json',dict(createdAt=now(),durationSeconds=D,frames=N,planSha256=sha(plan_path),
  voiceSourceSha256=sha(narration),narrationMeasurement=raw,premixMeasurement=measured,masterGainDb=gain,
  finalAacMeasurement=final,wavSha256=sha(mix),aacSha256=sha(aac),bgmSha256=sha(bg),
  approvedNimbusReferenceSha256=original_music_sha,continuousApprovedNimbus=True,sourceAudioStreams=0,newTts=0,
  originalNimbusFileVerified=False,currentFinalMixedWindowAsr='pending',humanWholeListening='pending',humanPronunciation='pending'))
 # Only concatenate already completed branding, reviewed body, original member.
 listing=FINAL/'concat-visual.txt';listing.write_text('\n'.join("file '"+p.as_posix().replace("'","'\\''")+"'" for p in [intro,ROOT/plan['bodySilent'],member])+'\n','utf-8')
 visual=FINAL/'silent-visual.mp4'
 ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-map_metadata','-1','-c:v','copy','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',visual],'concat-reviewed-final-silent-visual')
 probe=json.loads(run(FP,['-v','error','-show_streams','-show_format','-of','json',visual],'visual-probe'))
 assert len(probe['streams'])==1;v=probe['streams'][0]
 assert (v['width'],v['height'],v['avg_frame_rate'],v['time_base'],int(v['nb_frames']))==(1920,1080,'60/1','1/90000',N)
 pts=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',visual],'all-visual-PTS'))['frames']
 assert [int(v['best_effort_timestamp']) for v in pts]==list(range(0,N*1500,1500))
 ff(['-i',visual,'-f','null','-'],'whole-silent-visual-decode')
 save(FINAL/'visual-build.json',dict(createdAt=now(),planSha256=sha(plan_path),path=rel(visual),sha256=sha(visual),
  frames=N,timebase='1/90000',ptsStep=1500,allPtsVerified=True,wholeDecodeExitCode=0,probe=probe,
  retainedIntro=dict(path=rel(intro),sha256=sha(intro),frames=120),retainedMember=dict(path=rel(member),sha256=sha(member),frames=600),
  retainedBodySha256=plan['bodySilentSha256'],sourceAudioStreams=0,newWhiteRender=0,newNativeRender=0,
  allFinalPixels=False,finalMixedAsrApproved=False,private=False))
 s.update(status='closed-current-Nimbus-and-silent-visual-mixed-ASR-pending',exitCode=0,endedAt=now(),activeTask=None);checkpoint()
 print(json.dumps(dict(exitCode=0,frames=N,seconds=D,lufs=final['input_i'],truePeak=final['input_tp'],finalMixedAsrApproved=False)),flush=True)
except BaseException:
 s.update(status='closed-current-mix-failed-preserve-outputs',exitCode=1,endedAt=now(),activeTask=None,error=traceback.format_exc());checkpoint();raise
