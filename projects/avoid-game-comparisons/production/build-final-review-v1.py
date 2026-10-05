"""Build current review masters only; collection requires independent complete QA."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,os,sys,time,re,traceback
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;WORK=BASE/'final-v1';MEASURED=BASE/'measured-edit-v6'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stage=sys.argv[1];assert stage in ['mix','visual','captioned','captioned-exact-pts'];execution=WORK/f'build-{stage}-execution.json';assert not execution.exists()
plan=read(WORK/'plan.json');manifest=read(BASE.parent/'project.json');commands=[];active=None
assert plan['finalTimingApproved'] and plan['bodyRatioApproved'] and plan['allInputSegmentCaptionPixelsReviewed'] and plan['body60_40ErrorFrames']==0
assert read(BASE/'timed-white-pixel-direct-review-v6.json')['allCurrentWhiteCueSamplesApproved'] and read(BASE/'current-framed-pixel-direct-review-v6.json')['allCurrentGameplayCueSamplesApproved']
for s in plan['scenes']:assert sha(ROOT/s['audio'])==s['audioSha256']
D=plan['finalFrames']/60
def state(status,code=None):
 global active
 st=dict(stage=stage,pid=os.getpid(),status=status,observedAt=now(),activeChild=active,commands=commands,exitCode=code,finalApproved=False,sourceAudioStreams=0,newTts=0)
 write(execution,st)
 qpath=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qpath);item=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
 ex=item['execution'];ex['finalReview']=dict(state=rel(execution),**st);ex['activeTasks']=[a for a in ex.get('activeTasks',[]) if a.get('kind')!='current-final-review']
 if status=='running':ex['activeTasks'].append(dict(kind='current-final-review',pid=os.getpid(),stage=stage,state=rel(execution),child=active))
 ex.update(cpuProductionJobs=1 if status=='running' else 0,primaryCpuProductionJobs=1 if status=='running' else 0,gpuSynthesisJobs=0,renderJobs=1 if status=='running' and stage.startswith('captioned') else 0,uploads=0)
 item['stage']='current15-final-review-'+stage;item['nextAction']='Review final mixed narration and every encoded caption/cut, then full technical QA, collect four files, private upload and selective Git delivery.';item['updatedAt']=st['observedAt'];q['updatedAt']=st['observedAt']
 temp=qpath.with_name(qpath.name+'.avoid-final-writing');write(temp,q)
 for n in range(30):
  try:os.replace(temp,qpath);break
  except PermissionError:
   if n==29:raise
   time.sleep(.1)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=item['stage'],updatedAt=item['updatedAt'],execution=ex,nextAction=item['nextAction'],finalTimingApproved=True,bodyRatioApproved=True,finalMixComplete=(WORK/'mix-settings.json').exists(),renderComplete=False,qaComplete=False,collected=False,privateUploadSaved=False,completedVideoDelivery=False)
 write(BASE/'latest-checkpoint.json',cp)
def run(exe,args):
 global active
 log=WORK/f'build-{stage}-{len(commands)+1:02d}.log'
 with log.open('w',encoding='utf-8') as out:
  p=subprocess.Popen([str(exe),*map(str,args)],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  active=dict(pid=p.pid,command=[str(exe),*map(str,args)],log=rel(log));state('running');code=p.wait()
 commands.append(dict(**active,exitCode=code));active=None;state('running')
 if code:raise RuntimeError(f'Command failed {code}: {rel(log)}')
 return log.read_text(encoding='utf-8')
def ff(args):return run(FF,['-hide_banner','-y','-threads','2',*args])
def probe(p,count=False):return json.loads(run(FP,['-v','error',*(['-count_frames','-threads','2'] if count else []),'-show_streams','-show_format','-of','json',p]))
def scan(p,I=-16,TP=-2):return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',ff(['-i',p,'-af',f'loudnorm=I={I}:TP={TP}:LRA=11:print_format=json','-f','null','-'])).group())
state('running')
try:
 if stage=='mix':
  pres=read(WORK/'pcm-timeline-preservation.json');voice=ROOT/pres['voicePath'];assert sha(voice)==pres['voiceSha256'] and pres['all15PlacedPcmSamplesIdentical']
  raw=scan(voice);normal=WORK/'voice-normalized-pass.wav';normalized=WORK/'voice-normalized.wav'
  ff(['-i',voice,'-af',f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={raw['input_i']}:measured_TP={raw['input_tp']}:measured_LRA={raw['input_lra']}:measured_thresh={raw['input_thresh']}:offset={raw['target_offset']}:linear=true,aresample=48000,aformat=channel_layouts=stereo",'-c:a','pcm_s16le',normal])
  x,sr=sf.read(normal,dtype='int16',always_2d=True);assert sr==48000 and len(x)==plan['finalFrames']*800
  # Resampler ringing outside the narrated body is not speech and must not leak into branding.
  initial=hashlib.sha256(x[:96000].tobytes()).hexdigest();nz=int(np.count_nonzero(x[:96000]));x[:96000]=0;x[-480000:]=0
  repaired=WORK/'voice-normalized-body-only.wav';sf.write(repaired,x,sr,subtype='PCM_16')
  write(WORK/'normalization-outside-body-silence.json',dict(createdAt=now(),originalPassSha256=sha(normal),bodyOnlySha256=sha(repaired),brandingOriginalNonzeroSamples=nz,brandingOriginalPcmSha256=initial,changedOnlyBrandingAndMembership=True,allBodyNormalizedSamplesRetained=True,currentSourcePcmUnchanged=True))
  measured=scan(repaired);gain=min(-16-float(measured['input_i']),-2-float(measured['input_tp']))
  ff(['-i',repaired,'-af',f'volume={gain}dB','-c:a','pcm_s16le',normalized])
  music=ROOT/manifest['audio']['backgroundMusic']['file'];assert manifest['audio']['backgroundMusic']['approvalStatus']=='approved' and sha(music)==manifest['audio']['backgroundMusic']['restoration']['sha256']
  md=float(probe(music)['format']['duration']);n=int(np.ceil((D-1)/(md-1)))
  if n>1:
   chain=';'.join(f"{'[0:a]' if k==1 else '[b'+str(k-1)+']'}[{k}:a]acrossfade=d=1:c1=tri:c2=tri[b{k}]" for k in range(1,n));continuous=WORK/'nimbus-continuous.wav'
   ff([*sum((['-i',music] for _ in range(n)),[]),'-filter_complex',chain,'-map',f'[b{n-1}]','-c:a','pcm_s16le',continuous]);music=continuous
  bg=WORK/'bgm-before-ducking.wav'
  ff(['-i',music,'-af',f'atrim=duration={D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st={D-.45}:d=0.45','-c:a','pcm_s16le',bg])
  mix=WORK/'final-mix.wav';aac=WORK/'final-mix.m4a';filter='[0:a]asplit[n][d];[1:a][d]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=.80:level=false:latency=true[mix]'
  ff(['-i',normalized,'-i',bg,'-filter_complex',filter,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',mix]);ff(['-i',mix,'-c:a','aac','-b:a','192k',aac]);final=scan(aac,-16,-1.5)
  assert abs(float(final['input_i'])+16)<=.6 and float(final['input_tp'])<=-1.5,final
  assert len(sf.read(mix,dtype='int16')[0])==plan['finalFrames']*800
  write(WORK/'mix-settings.json',dict(createdAt=now(),durationSeconds=D,planSha256=sha(WORK/'plan.json'),voiceSourceSha256=sha(voice),narration=raw,normalizedVoice=measured,constantVoiceGainDb=gain,finalAacMeasurement=final,wavSha256=sha(mix),aacSha256=sha(aac),bgmSha256=sha(bg),continuousApprovedNimbus=True,sourceAudioStreams=0,originalNimbusFileVerified=False,currentFinalMixedWindowAsr='pending',humanWholeListening='pending'))
 elif stage=='visual':
  reward=ROOT/'projects/game-reward-planning/production/final-v1/white-segments';branding=reward/'branding.mp4';member=reward/'membership.mp4'
  assert sha(branding)=='706a0738dcd160b80ace24e54e16c09604c0173aba095fcd221a227c541fffb2' and sha(member)=='181e5c5dd37672349542aa590629fe2f2d00a83f4cd3c811a29a21c029612123'
  segments=[dict(id='branding',startFrame=0,frames=120,video=rel(branding),sha256=sha(branding),classification='branding')]
  for s in plan['scenes']:
   for c in s['segments']:
    assert sha(ROOT/c['video'])==c['videoSha256']
    segments.append(dict(id=c['id'],sceneId=s['id'],startFrame=c['startFrame'],frames=c['frames'],video=c['video'],sha256=c['videoSha256'],classification=c['classification'],diagramId=c.get('diagramId')))
  segments.append(dict(id='membership',startFrame=plan['finalFrames']-600,frames=600,video=rel(member),sha256=sha(member),classification='membership'))
  pos=0
  for c in segments:assert c['startFrame']==pos;pos+=c['frames']
  assert pos==32100
  listing=WORK/'visual-concat.txt';listing.write_text('\n'.join("file '"+(ROOT/c['video']).as_posix()+"'" for c in segments)+'\n',encoding='utf-8')
  visual=WORK/'visual-silent-review.mp4';ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',visual]);pr=probe(visual,True)
  assert int(pr['streams'][0]['nb_read_frames'])==32100 and len(pr['streams'])==1
  write(WORK/'visual-build.json',dict(createdAt=now(),status='silent-review-not-delivered',frames=pos,seconds=D,segments=segments,sha256=sha(visual),probe=pr,originalBrandingMembershipByteIdentical=True,finalFixedCaptionPixelsApproved=False))
 else:
  v=read(WORK/'visual-build.json');mix=read(WORK/'mix-settings.json');assert sha(WORK/'visual-silent-review.mp4')==v['sha256'] and sha(WORK/'final-mix.m4a')==mix['aacSha256']
  clean=WORK/'avoid-game-comparisons.clean.review.mp4';captioned=WORK/'avoid-game-comparisons.captioned.review.mp4'
  if stage=='captioned-exact-pts':
   assert read(WORK/'build-captioned-execution.json')['status']=='failed' and read(WORK/'captioned-pts-failure.json')['captionedFrames']==32102
   archived=WORK/'avoid-game-comparisons.captioned.invalid-32102-frames.mp4';assert not archived.exists();captioned.rename(archived)
   assert sha(clean)==read(WORK/'captioned-pts-failure.json')['cleanSha256']
  else:ff(['-i',WORK/'visual-silent-review.mp4','-i',WORK/'final-mix.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',clean])
  ff(['-i',clean,'-vf',f'setpts=N/(60*TB),subtitles={rel(WORK/"captions.ko.ass")}','-fps_mode','passthrough','-frames:v','32100','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-video_track_timescale','90000','-movflags','+faststart',captioned])
  probes=[probe(p,True) for p in [clean,captioned]]
  for p in probes:assert int(p['streams'][0]['nb_read_frames'])==32100
  write(WORK/'render-result.json',dict(createdAt=now(),status='two-current-review-videos-awaiting-QA',done=True,exitCode=0,clean=rel(clean),captioned=rel(captioned),cleanSha256=sha(clean),captionedSha256=sha(captioned),frames=32100,seconds=535.0,captionCueCount=199,enCueCount=160,cleanProbe=probes[0],captionedProbe=probes[1],technicalQa=False,allFinalCaptionPixelsApproved=False))
 state('finished',0);print(json.dumps(dict(stage=stage,seconds=D,frames=32100,reviewMediaBuilt=True,finalApproval=False)))
except Exception:
 traceback.print_exc();state('failed',1);sys.exit(1)
