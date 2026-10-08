"""Build one CPU2 normal-speed candidate input bank, never a final approval.

Approved MC renders and whole PCM are preserved. Reuse138 complete v2 segments; only one changed native cut is encoded. Only cropping/encoding already
selected native frames and slicing the existing MC videos occur here. The silent
preview is an input review artifact. Final mixed ASR and a reviewed pair are later
gates; neither this worker nor its completion can approve them.
"""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import argparse, ctypes, hashlib, json, math, os, subprocess, sys, time, traceback
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/player-customization/selected-inputs-v3'
STATE=BASE/'selected-inputs-execution-v3.json'; SESSION=STATE.with_name(STATE.stem+'.session.json')
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'); FP=FF.with_name('ffprobe.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):d.update(b)
 return d.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(60):
  try:t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p);return
  except OSError:
   if n==59:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
r=read(ROOT/args.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'].replace('Z','+00:00'))).total_seconds()<240
PLAN=ROOT/'projects/player-customization/planning/integer-action-allocation-candidate-v5.json'
CAP=BASE/'caption-candidate-v1/captions.json'
plan=read(PLAN);cap=read(CAP)
baseline=read(BASE/'selected-inputs-execution-v2.json');assert baseline['exitCode']==0 and baseline['completedCuts']==139
assert read(BASE/'action-repaired-pixels-direct-review-v2.json')['allBoardsDirectlyRead']
assert read(BASE/'selected-pixels-direct-review-v1.json')['allBoardsDirectlyRead']
assert read(BASE/'action-repair-candidate-direct-review-v1.json')['all17BoardsDirectlyRead']
assert read(BASE/'action-repair-candidate-direct-review-v2.json')['all8BoardsDirectlyRead']
assert plan['allNativeSourceFramesUnique'] and not plan['issues']
assert plan['wholePcmSamples']==14125441 and plan['allCurrentPcmSamplesPreserved']
assert not plan['sourceAllocationApproved'] and not plan['finalTimingApproved']
for i in plan['inputs']:assert sha(ROOT/i['path'])==i['sha256']
for s in {c['sourcePath']:c['sourceSha256'] for c in plan['cuts']}.items():assert sha(ROOT/s[0])==s[1]
previous=read(STATE) if STATE.exists() else None
if args.resume:
 assert previous and previous['exitCode']==1 and previous['allocationSha256']==sha(PLAN) and previous['captionSha256']==sha(CAP)
 assert OUT.exists()
else:assert not OUT.exists() and not STATE.exists(),'Read the actual checkpoint; no repeated encoding.'
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir(parents=True,exist_ok=args.resume);(OUT/'segments').mkdir(exist_ok=args.resume);(OUT/'logs').mkdir(exist_ok=args.resume)
s=dict(schemaVersion=1,slug='player-customization',pid=os.getpid(),commandLine=[sys.executable,*sys.argv],
 sessionId=None,startedAt=now(),status='selected-native-input-framing',cpuThreads=2,gpu=0,singleJob=True,
 resourceEvidence=args.resource,allocationPath=rel(PLAN),allocationSha256=sha(PLAN),captionPath=rel(CAP),captionSha256=sha(CAP),
 operations=[],segments=[],completedCuts=0,totalCuts=len(plan['cuts']),exitCode=None,sourceAudioUsed=False,
 allSelectedPixelsReviewed=False,sourceAllocationApproved=False,finalTimingApproved=False,finalMixedAsrApproved=False,
 allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,newGitImages=0)
if previous:
 s.update(operations=previous['operations'],segments=previous['segments'],completedCuts=previous['completedCuts'],
  recoveryHistory=previous.get('recoveryHistory',[])+[dict(pid=previous['pid'],sessionId=previous['sessionId'],startedAt=previous['startedAt'],
   endedAt=previous['endedAt'],exitCode=previous['exitCode'],error=previous.get('error'),completedCuts=previous['completedCuts'],
   reason='Resume only after inspected failure; preserve verified completed repairs and all baseline segments.')])
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==os.getpid():s.update(sessionId=x['sessionId'],processIdentity=x['processIdentity'])
 s['observedAt']=now();save(STATE,s)
 job=dict(status=s['status'],pid=os.getpid(),commandLine=s['commandLine'],sessionId=s['sessionId'],
  processIdentity=s.get('processIdentity'),state=rel(STATE),cpuThreads=2,gpu=0,singleJob=True,
  activeTask=s.get('activeTask'),exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None,
  progress=dict(completed=s['completedCuts'],total=s['totalCuts']))
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),
  selectedInputExecution=rel(STATE),nextAction='Directly inspect every candidate cue/cut and action sequence, repair mismatches without repeating good inputs; only then adopt final allocation and build Nimbus mix/current mixed ASR. Final pair, QA, collection/private/Git remain false.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(x for x in q['items'] if x['slug']=='player-customization')
 i.update(stage=cp['stage'],currentExecution=job,selectedInputExecution=rel(STATE),nextAction=cp['nextAction']);q['updatedAt']=now();save(qp,q)
def run(exe,a,kind):
 cmd=[str(exe),*map(str,a)];log=OUT/'logs'/f'{len(s["operations"])+1:04d}.log'
 op=dict(kind=kind,commandLine=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  op['pid']=p.pid;s['activeTask']=op;checkpoint();code=p.wait()
 op.update(exitCode=code,endedAt=now());s['activeTask']=None;checkpoint()
 assert code==0,f'{kind} exit{code}; preserve completed files and logs: {log}'
 return log.read_text('utf-8-sig')
def ff(a,k):return run(FF,['-nostdin','-v','error','-threads','2',*a],k)
def probe(p,n):
 j=json.loads(run(FP,['-v','error','-show_streams','-show_format','-of','json',p],'probe-selected-input'))
 assert len(j['streams'])==1
 v=j['streams'][0];assert v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='60/1'
 assert int(v['nb_frames'])==n and v['time_base']=='1/90000'
 assert abs(float(j['format']['duration'])-n/60)<.017
 return j
def stamp(x):
 n=round(x*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
def ass():
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
 h=['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','WrapStyle: 2','ScaledBorderAndShadow: yes','','[V4+ Styles]',
 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
 'Style: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1','','[Events]',
 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
 for c in cap['ko']:
  lines=c['lines'];assert len(lines)<=2 and c['center']==[960,970]
  w=math.ceil(max(font.getlength(t) for t in lines))+44;height=62*len(lines)+22;x=960-w/2;y=970-height/2
  a,b=stamp(c['startSeconds']-2),stamp(c['endSeconds']-2)
  base=lambda layer:f'Dialogue: {layer},{a},{b},Default,,0,0,0,,'
  shape=f'm 0 0 l {w} 0 {w} {height} 0 {height}'
  h += [base(0)+f'{{\\an7\\pos({x+14:g},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&}}'+shape,
        base(1)+f'{{\\an7\\pos({x:g},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+shape]
  for i,t in enumerate(lines):
   assert not any(x in t for x in ['{','}','\\'])
   h.append(base(2)+f'{{\\an5\\pos(960,{970+(i-(len(lines)-1)/2)*62:g})\\bord0\\shad0}}'+t)
 p=OUT/'candidate-body.ko.ass';p.write_text('\n'.join(h)+'\n','utf-8');return p
try:
 checkpoint()
 for idx,c in enumerate(plan['cuts'],1):
  if idx<=s['completedCuts']:
   prior=s['segments'][idx-1];assert sha(ROOT/prior['video'])==prior['videoSha256'];continue
  if not c.get('repairNativeOnly'):
   prior=baseline['segments'][c['baselineCutIndex']-1]
   for k in ['role','sourcePath','sourceSha256','sourceInFrame','sourceOutFrame','frames','outputStartFrame','cropCandidate']:
    assert prior.get(k)==c.get(k),(idx,k)
   assert sha(ROOT/prior['video'])==prior['videoSha256']
   s['segments'].append({**c,'index':idx,'video':prior['video'],'videoSha256':prior['videoSha256'],'probe':prior['probe'],'sourceRerendered':False,'baselineSegmentReused':True,'encodedFixedCuePixelsReviewed':False})
   s['completedCuts']+=1;checkpoint();print(f'Reuse baseline cut {c["baselineCutIndex"]}',flush=True);continue
  path=ROOT/c['sourcePath'];n=c['frames'];start=c.get('firstNativeSeconds',c['sourceInFrame']/60)
  # All selected native ticks are contiguous60fps, verified in the candidate.
  # One10us epsilon avoids rounding past the exact requested first frame.
  filt=[]
  if c['role']=='actual-game-candidate':
   x,y,w,h=c['cropCandidate'];filt += [f'crop={w}:{h}:{x}:{y}', 'scale=1920:1080:flags=lanczos']
  filt += ['setsar=1','setpts=N/(60*TB)']
  out=OUT/'segments'/f'{idx:03d}-{c["scene"]}-p{c["paragraph"]}.mp4'
  if out.exists():
   assert args.resume and any(o['commandLine'][-1]==str(out) and o.get('exitCode')==0 and o['kind'] in ['crop-native-action','slice-existing-MC-no-render'] for o in s['operations']), 'Preserve unknown or failed output; inspect before reusing.'
  else:
   ff(['-ss',f'{max(0,start-.00001):.8f}','-i',path,'-map','0:v:0','-an','-filter_threads','1','-vf',','.join(filt),
    '-frames:v',n,'-fps_mode','passthrough','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p',
    '-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',out],'crop-native-action' if c['role']=='actual-game-candidate' else 'slice-existing-MC-no-render')
  pr=probe(out,n)
  s['segments'].append({**c,'index':idx,'video':rel(out),'videoSha256':sha(out),'probe':pr,'sourceRerendered':False,
   'finalPixelsReviewed':False,'encodedFixedCuePixelsReviewed':False})
  s['completedCuts']+=1;checkpoint();print(f'Selected inputs {idx}/{len(plan["cuts"])}',flush=True)
 listing=OUT/'concat-body.txt';listing.write_text('\n'.join("file '"+(ROOT/c['video']).as_posix()+"'\nduration "+f"{c['frames']/60:.9f}" for c in s['segments'])+'\n','utf-8')
 body=OUT/'candidate-body.silent.mp4';s['status']='assemble-selected-candidate-body';checkpoint()
 ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-c:v','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500:time_base=1/90000','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',body],'assemble-candidate-inputs')
 probe(body,35321)
 pp=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',body],'candidate-exact-PTS'))['packets']
 assert sorted(int(p['pts']) for p in pp)==list(range(0,35321*1500,1500)) and all(int(p['duration'])==1500 for p in pp)
 assert not ff(['-i',body,'-an','-f','null','-'],'whole-silent-candidate-decode').strip()
 cp=OUT/'repair-window.captioned-silent.mp4';asspath=ROOT/baseline['captionAss'];assert sha(asspath)==baseline['captionAssSha256'];s['status']='encode-one-repair-fixed-caption-preview';checkpoint()
 lo=14513;hi=14931;wn=hi-lo
 ff(['-ss',f'{lo/60-.00001:.8f}','-i',body,'-an','-filter_threads','1','-vf',f'setpts=PTS-STARTPTS+{lo}/60/TB,ass={rel(asspath)},setpts=PTS-STARTPTS','-frames:v',str(wn),'-fps_mode','passthrough',
  '-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',cp],'encode-one-repair-captions')
 probe(cp,wn)
 assert not ff(['-i',cp,'-an','-f','null','-'],'whole-repair-caption-window-decode').strip()
 s.update(captionPreviewBodyStartFrame=lo,captionPreviewFrames=wn,captionPreviewFullBody=False)
 s.update(status='closed-selected-candidate-inputs-built-pixel-review-pending',exitCode=0,endedAt=now(),
  silentVideo=rel(body),silentSha256=sha(body),captionedSilentVideo=rel(cp),captionedSilentSha256=sha(cp),
  captionAss=rel(asspath),captionAssSha256=sha(asspath),frames=35321,exact90000Pts=True,wholeDecodesExitCode=0,
  silentPreviewIsCompletedVideo=False,actualOriginalWhiteRendersReused=True,reusedBaselineSegments=sum(bool(x.get('baselineSegmentReused')) for x in s['segments']),newNativeEncodes=sum(not bool(x.get('baselineSegmentReused')) for x in s['segments']))
 checkpoint();print(json.dumps(dict(exitCode=0,cuts=s['completedCuts'],frames=35321,allPixelsApproved=False)),flush=True)
except BaseException:
 s.update(status='closed-selected-candidate-inputs-failed',exitCode=1,endedAt=now(),error=traceback.format_exc());checkpoint();raise
