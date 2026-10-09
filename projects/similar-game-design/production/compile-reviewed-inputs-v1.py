"""One CPU2 selected-input build and actual ASS preflight; no final approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, math, os, subprocess, sys, time, traceback
import psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/similar-game-design/selected-inputs-v1'
STATE=BASE/'selected-inputs-execution-v1.json';SESSION=BASE/'selected-inputs-execution-v1.session.json'
PLAN=BASE/'measured-allocation-v2/plan.json';CAP=BASE/'caption-candidate-v2/captions.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
now=lambda:datetime.now(timezone.utc).isoformat();read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for i in range(60):
  try:os.replace(t,p);return
  except OSError:
   if i==59:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
r=read(ROOT/args.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
previous=read(STATE)if STATE.exists()else None
if args.resume:
 assert previous and previous['exitCode']==1 and previous['completedCuts']==1 and OUT.exists(),'Only the observed metadata failure may resume here'
else:assert not OUT.exists() and not STATE.exists(),'Read actual checkpoint; preserve previous work'
plan=read(PLAN);cap=read(CAP);white=read(BASE/'white-measured-verification-v1.json');review=read(BASE/'white-motion-caption-text-direct-review-v1.json')
assert plan['sourceAllocationApproved'] and plan['allSelectedNativePixelsReviewed'] and not plan['finalTimingApproved']
assert sha(PLAN)==cap['plan']['sha256']==review['plan']['sha256'] and sha(CAP)==review['captionTextReview']['sha256']
assert review['all22BoardsDirectlyRead'] and white['allAnimatedMeasuredPixelsReviewed'] and white['actualExitObserved']
assert len(cap['ko'])==400 and len(cap['en'])==148 and len(plan['scenes'])==24
assert sha(ROOT/white['currentWhite']['path'])==white['currentWhite']['sha256']
for source in plan['sources']:assert sha(ROOT/source['path'])==source['sha256']
for scene in plan['scenes']:assert sha(ROOT/scene['voicePath'])==scene['voiceSha256']
timing=read(ROOT/'motion-canvas/src/projects/similar-game-design/measured-timing-v1.json')
cuts=[dict(c)for c in plan['selectedNativeCuts']]
for w in timing['white']:
 cuts.append(dict(scene=w['id'],role='explanation',frames=w['frames'],startFrame=w['finalStartFrame'],endFrameExclusive=w['finalEndFrameExclusive'],sourcePath=white['currentWhite']['path'],sourceSha256=white['currentWhite']['sha256'],sourceInFrame=w['whiteProjectStartFrame'],sourceOutFrameExclusive=w['whiteProjectEndFrameExclusive'],part=w['part'],narrationConnection='Measured projected paragraph motion, directly reviewed128 samples.'))
cuts.sort(key=lambda c:c['startFrame']);assert len(cuts)==69
assert cuts[0]['startFrame']==120 and cuts[-1]['endFrameExclusive']==36498
for a,b in zip(cuts,cuts[1:]):assert a['endFrameExclusive']==b['startFrame'],'Timeline gap/overlap'
assert sum(c['frames']for c in cuts)==36378
assert sum(c['frames']for c in cuts if c['role']=='actual')==21827
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir(parents=True,exist_ok=args.resume);(OUT/'segments').mkdir(exist_ok=args.resume);(OUT/'logs').mkdir(exist_ok=args.resume)
s=dict(schemaVersion=1,slug='similar-game-design',pid=os.getpid(),createTime=psutil.Process().create_time(),commandLine=[sys.executable,*sys.argv],sessionId=None,startedAt=now(),status='compile-selected69-inputs',cpuThreads=2,gpuJobs=0,singleJob=True,resourceEvidence=args.resource,plan=dict(path=rel(PLAN),sha256=sha(PLAN)),captionCandidate=dict(path=rel(CAP),sha256=sha(CAP)),rawWhiteReview=rel(BASE/'white-motion-caption-text-direct-review-v1.json'),operations=[],segments=[],completedCuts=0,totalCuts=69,exitCode=None,sourceAudio=False,sourceAllocationApproved=True,allInputSegmentCaptionPixelsReviewed=False,finalTimingApproved=False,finalMixedAsrApproved=False,allFinalPixelsReviewed=False,render=False,qa=False,collected=False,uploaded=False,newGitImages=0)
if previous:
 assert previous['plan']==s['plan'] and previous['captionCandidate']==s['captionCandidate']
 s.update(operations=previous['operations'],segments=previous['segments'],completedCuts=previous['completedCuts'],recoveryHistory=[dict(pid=previous['pid'],createTime=previous['createTime'],sessionId=previous['sessionId'],exitCode=1,actualExitObserved=True,finishedAt=previous['finishedAt'],error=previous['error'],reason='Source timecode tag caused an automatic tmcd data stream. Reuse the first input; preserve second encoding and remux only its video. Disable inherited metadata for later inputs.')])
def checkpoint():
 if SESSION.exists():
  se=read(SESSION)
  if se['pid']==os.getpid() and abs(se['createTime']-s['createTime'])<.1:s['sessionId']=se['sessionId']
 s['updatedAt']=now();save(STATE,s)
 job=dict(pid=s['pid'],createTime=s['createTime'],commandLine=s['commandLine'],sessionId=s['sessionId'],cpuThreads=2,gpuJobs=0,singleJob=True,state=rel(STATE),status=s['status'],activeTask=s.get('activeTask'),completed=s['completedCuts'],total=69,workerExpectedRunning=s['exitCode'] is None,exitCode=s['exitCode'],actualExitObserved=False)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,selectedInputExecution=rel(STATE),nextAction='Directly inspect every actual ASS preflight board/cue/cut/white paragraph; only then adopt timing and build continuous Nimbus mix/current48-window mixed ASR. Final pair/QA/collection/private remain false.',updatedAt=now());save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(i for i in q['items']if i['slug']=='similar-game-design');item.update(stage=s['status'],currentExecution=job,selectedInputExecution=rel(STATE),nextAction=cp['nextAction'],updatedAt=now());q['updatedAt']=now();save(qp,q)
def run(exe,args,kind):
 cmd=[str(exe),*map(str,args)];log=OUT/'logs'/f'{len(s["operations"])+1:04d}.log';op=dict(kind=kind,commandLine=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8')as f:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);op.update(pid=p.pid,createTime=psutil.Process(p.pid).create_time());s['activeTask']=op;checkpoint();code=p.wait()
 op.update(exitCode=code,finishedAt=now());s['activeTask']=None;checkpoint();assert code==0,f'{kind} exit{code}: {log}';return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-v','error','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def probe(p,n):
 j=json.loads(run(FP,['-v','error','-threads','2','-show_streams','-show_format','-of','json',p],'probe-current-input'))
 assert len(j['streams'])==1;v=j['streams'][0]
 assert v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='60/1' and v['time_base']=='1/90000'
 assert int(v['nb_frames'])==n and int(v['duration_ts'])==n*1500
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
  lines=c['lines'];assert 1<=len(lines)<=2 and c['center']==[960,970]
  w=math.ceil(max(font.getlength(t)for t in lines))+44;height=62*len(lines)+22;x=960-w/2;y=970-height/2
  a,b=stamp(c['startSeconds']-2),stamp(c['endSeconds']-2);base=lambda layer:f'Dialogue: {layer},{a},{b},Default,,0,0,0,,';shape=f'm 0 0 l {w} 0 {w} {height} 0 {height}'
  h.extend([base(0)+f'{{\\an7\\pos({x+14:g},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&}}'+shape,base(1)+f'{{\\an7\\pos({x:g},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+shape])
  for i,text in enumerate(lines):
   assert not any(a in text for a in ['{','}','\\'])
   h.append(base(2)+f'{{\\an5\\pos(960,{970+(i-(len(lines)-1)/2)*62:g})\\bord0\\shad0}}'+text)
 p=OUT/'candidate-body.ko.ass';p.write_text('\n'.join(h)+'\n','utf-8');return p
try:
 checkpoint()
 for idx,c in enumerate(cuts,1):
  if idx<=s['completedCuts']:
   assert sha(ROOT/s['segments'][idx-1]['video'])==s['segments'][idx-1]['videoSha256'];continue
  start=c['sourceInFrame']/60;out=OUT/'segments'/f'{idx:03d}-{c["scene"]}.mp4';filt=[]
  if c['role']=='actual':filt.extend([c['cropFilter'],'scale=1920:1080:flags=lanczos'])
  filt.extend(['setsar=1','setpts=N/(60*TB)'])
  if out.exists():
   assert args.resume and idx==2 and any(o['kind']=='crop-selected-native'and o.get('exitCode')==0 and o['commandLine'][-1]==str(out)for o in s['operations']),'Unknown existing output'
   raw=out;out=out.with_name(out.stem+'.video-only.mp4');assert not out.exists()
   ff(['-i',raw,'-map','0:v:0','-an','-c:v','copy','-map_metadata','-1','-write_tmcd','0','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',out],'remux-existing-second-input-remove-tmcd')
   s['preservedTimecodeMetadataEncoding']=dict(path=rel(raw),sha256=sha(raw))
  else:
   ff(['-ss',f'{max(0,start-.00001):.8f}','-i',ROOT/c['sourcePath'],'-map','0:v:0','-an','-map_metadata','-1','-write_tmcd','0','-vf',','.join(filt),'-frames:v',c['frames'],'-fps_mode','passthrough','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',out],'crop-selected-native'if c['role']=='actual'else'slice-existing-measured-white')
  pr=probe(out,c['frames']);s['segments'].append(dict(c,index=idx,video=rel(out),videoSha256=sha(out),probe=pr,captionPixelsReviewed=False,finalPixelsReviewed=False));s['completedCuts']=idx;checkpoint();print(f'Input {idx}/69',flush=True)
 listing=OUT/'concat-body.txt';listing.write_text('ffconcat version 1.0\n'+''.join("file '"+(ROOT/c['video']).as_posix()+"'\nduration "+f"{c['frames']/60:.12f}"+'\n'for c in s['segments']),'utf-8')
 body=OUT/'candidate-body.silent.mp4'
 ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-c:v','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500:time_base=1/90000','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',body],'assemble-selected-inputs')
 bodyProbe=probe(body,36378)
 packets=json.loads(run(FP,['-v','error','-threads','2','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',body],'probe-all-body-PTS'))['packets']
 assert len(packets)==36378 and sorted(int(p['pts'])for p in packets)==list(range(0,36378*1500,1500)) and all(int(p['duration'])==1500 for p in packets)
 assert not ff(['-i',body,'-an','-f','null','-'],'decode-entire-current-input-body').strip()
 apath=ass();s.update(silentVideo=rel(body),silentSha256=sha(body),captionAss=rel(apath),captionAssSha256=sha(apath),bodyProbe=bodyProbe,frames=36378,wholeDecodeExitCode=0,exact90000Pts=True);checkpoint()
 # Every cue and every visible-role/native boundary, plus all measured white
 # paragraph-motion points. ASS operates on the unaltered body presentation clock.
 samples={}
 def sample(f,reason):
  assert 0<=f<36378;samples.setdefault(f,[]).append(reason)
 for c in cap['ko']:
  f=round(((c['startSeconds']+c['endSeconds'])/2-2)*60);sample(f,dict(kind='cue',cue=c['index'],scene=c['scene'],paragraph=c['paragraph']))
 for c in cuts:
  sample(c['startFrame']-120,dict(kind='cut-first',scene=c['scene'],role=c['role']))
  sample(c['endFrameExclusive']-121,dict(kind='cut-last',scene=c['scene'],role=c['role']))
 for p in cap['paragraphs']:sample(min(36377,max(0,round((p['startSeconds']-2)*60))),dict(kind='PCM-paragraph-onset',scene=p['scene'],paragraph=p['paragraph']))
 for f in white['samplePlan']:
  w=next(w for w in timing['white']if w['id']==f['scene']and w['part']==f['part']);sample(w['finalStartFrame']-120+f['frame']-w['whiteProjectStartFrame'],dict(kind='white-motion',scene=f['scene'],paragraph=f['paragraph'],phase=f['phase']))
 frames=sorted(samples);native=OUT/'ass-preflight-native';boards=OUT/'ass-preflight-boards';native.mkdir();boards.mkdir()
 expr='+'.join(f'eq(n,{f})'for f in frames)
 # Apply ASS before selecting frames so presentation time stays the exact body clock.
 ff(['-i',body,'-an','-vf',f"ass={rel(apath)},select='{expr}'",'-fps_mode','vfr','-threads','2',native/'frame-%04d.png'],'extract-all-cue-cut-white-actual-ASS-preflight')
 assert len(list(native.glob('frame-*.png')))==len(frames)
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',21);rows=[]
 for i,f in enumerate(frames,1):
  p=native/f'frame-{i:04d}.png';visible=[c['index']for c in cap['ko']if round((c['startSeconds']-2)*100)/100<=f/60<round((c['endSeconds']-2)*100)/100]
  rows.append(dict(index=i,bodyFrame=f,finalFrame=f+120,path=rel(p),sha256=sha(p),observations=samples[f],visibleCueIds=visible))
 boardrows=[]
 for bi,start in enumerate(range(0,len(rows),6),1):
  group=rows[start:start+6];board=Image.new('RGB',(1920,1240),'white');draw=ImageDraw.Draw(board)
  for ci,row in enumerate(group):
   x=(ci%3)*640;y=(ci//3)*620;draw.text((x+6,y+5),f'{row["index"]:04d} n{row["finalFrame"]} cue{row["visibleCueIds"]}',font=font,fill='black');im=Image.open(ROOT/row['path']).convert('RGB');board.paste(im.resize((640,360)),(x,y+34));board.paste(im.crop((600,862,1320,1072)).resize((640,187)),(x,y+404))
   draw.text((x+6,y+593),'; '.join(o['kind']for o in row['observations'])[:57],font=font,fill='black')
  p=boards/f'board-{bi:03d}.jpg';board.save(p,quality=94);boardrows.append(dict(path=rel(p),sha256=sha(p),entries=group,directlyRead=False))
 s.update(status='closed-selected69-inputs-actual-ASS-await-direct-review',exitCode=0,finishedAt=now(),samples=rows,boards=boardrows,uniqueSampleFrames=len(rows),all400CueSamplesExtracted=True,all69CutEdgesExtracted=True,all128WhiteMotionSamplesExtracted=True,previewIsCompletedVideo=False,allCurrentPcmPreserved=True);checkpoint();print(json.dumps(dict(exitCode=0,cuts=69,frames=36378,samples=len(rows),boards=len(boardrows),allPixelGates=False)),flush=True)
except BaseException:
 s.update(status='failed-selected-inputs-preserve-completed-media',exitCode=1,finishedAt=now(),error=traceback.format_exc());checkpoint();raise
