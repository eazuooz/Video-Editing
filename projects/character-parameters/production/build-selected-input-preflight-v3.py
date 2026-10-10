"""One CPU2 serial job: slice17 measured black inputs, reuse24 native, ASS QA."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,math,os,re,subprocess,sys,time,traceback
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OUT=ROOT/'shared/output/character-parameters/selected-inputs-v3'
STATE=BASE/'selected-input-preflight-execution-v3.json';SESSION=BASE/'selected-input-preflight-execution-v3.session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe');FP=FF.with_name('ffprobe.exe')
now=lambda:datetime.now(timezone.utc).isoformat();read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 tmp=p.with_name(p.name+f'.{os.getpid()}.writing');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for i in range(40):
  try:os.replace(tmp,p);return
  except OSError:
   if i==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args()
r=read(ROOT/args.resource)
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
assert not STATE.exists() and not OUT.exists(),'Resume actual checkpoint, never replace existing output'
PLAN=BASE/'measured-timeline-candidate-v3.json';CAP=BASE/'caption-candidate-v4/captions.json'
plan=read(PLAN);cap=read(CAP);assert sha(PLAN)==cap['planSha256']
export=read(BASE/'measured-black-export-execution-v3.json');native=read(BASE/'measured-native-inputs-execution-v3.json')
assert export['exitCode']==0 and export['childExited']
black=dict(videoPath=export['output'],videoSha256=export['outputSha256'])
assert native['exitCode']==0 and len(native['results'])==24
assert cap['koCueCount']==201 and cap['enCueCount']==95 and cap['allCurrent37KoEnParagraphsRetained']
assert sha(ROOT/black['videoPath'])==black['videoSha256']
for row in native['results']:assert sha(ROOT/row['path'])==row['sha256']
subprocess.run(['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs','character-parameters','--check'],cwd=ROOT,check=True)
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
OUT.mkdir(parents=True);(OUT/'segments').mkdir();(OUT/'logs').mkdir();QA=OUT/'qa';QA.mkdir()
p=psutil.Process();s=dict(schemaVersion=3,slug='character-parameters',pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),sessionId=None,startedAt=now(),status='selected-input-build-and-ASS-preflight-running',cpuThreads=2,gpuJobs=0,singleJob=True,resource=args.resource,plan=rel(PLAN),planSha256=sha(PLAN),captionCandidate=rel(CAP),captionCandidateSha256=sha(CAP),operations=[],segments=[],completedBlackSegments=0,totalBlackSegments=17,exitCode=None,sourceAudio=False,finalTimingApproved=False,finalMixedAsrApproved=False,allInputCaptionPixelsReviewed=False,allFinalPixels=False,qa=False,collected=False,private=False,imagesGitAdded=0)
def checkpoint():
 if SESSION.exists():
  session=read(SESSION)
  if session['pid']==s['pid'] and abs(session['createTime']-s['createTime'])<.01:s['sessionId']=session['sessionId']
 s['updatedAt']=now();save(STATE,s)
 cp=read(BASE/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=s['status'],ownedJob=dict(pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],sessionId=s['sessionId'],state=rel(STATE),activeOperation=s.get('activeOperation'),completed=s['completedBlackSegments'],total=17,cpuThreads=2,gpu=0,exitCode=s['exitCode']),nextAction='Read every new measured ASS cue/cut/motion board directly. Only then adopt final input timing and Nimbus current mix; mixed ASR/pair/final encoded QA/collection/private remain false.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);item=next(x for x in q['items']if x['slug']=='character-parameters')
  item.update(stage=s['status'],currentExecution=cp['ownedJob'],selectedInputExecution=rel(STATE),nextAction=cp['nextAction']);q.update(updatedAt=now(),lastProgressAt=now())
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 else:raise RuntimeError('Concurrent queue preserved')
def run(exe,args,kind):
 cmd=[str(exe),*map(str,args)];log=OUT/'logs'/f'{len(s["operations"])+1:03d}-{kind}.log'
 op=dict(kind=kind,command=cmd,log=rel(log),startedAt=now());s['operations'].append(op)
 with log.open('w',encoding='utf-8')as f:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  op.update(pid=child.pid,createTime=psutil.Process(child.pid).create_time());s['activeOperation']=op;checkpoint();code=child.wait()
 op.update(exitCode=code,finishedAt=now());s['activeOperation']=None;checkpoint();assert code==0,f'{kind}: {log}'
 return log.read_text('utf-8-sig')
def ff(args,kind):return run(FF,['-v','info','-nostdin','-threads','2','-filter_threads','1','-filter_complex_threads','1',*args],kind)
def probe(path,frames):
 j=json.loads(run(FP,['-v','error','-show_streams','-show_format','-of','json',path],'probe'))
 assert len(j['streams'])==1;v=j['streams'][0]
 assert (v['width'],v['height'],v['avg_frame_rate'],v['time_base'])==(1920,1080,'60/1','1/90000')
 assert int(v['nb_frames'])==frames and int(v['duration_ts'])==frames*1500
 return j
def ass_stamp(t):
 n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
def make_ass():
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
 h=['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','WrapStyle: 2','ScaledBorderAndShadow: yes','','[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding','Style: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1','','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
 for c in cap['ko']:
  assert len(c['lines'])==1 and c['center']==[960,970]
  text=c['ko'];assert not any(a in text for a in '{}\\')
  width=math.ceil(font.getlength(text))+44;height=84;x=960-width/2;y=928
  assert width<=924 and x>485 and x+width+14<1460
  a,b=ass_stamp(c['startSeconds']-2),ass_stamp(c['endSeconds']-2);base=lambda layer:f'Dialogue: {layer},{a},{b},Default,,0,0,0,,'
  shape=f'm 0 0 l {width} 0 {width} {height} 0 {height}'
  h.extend([base(0)+f'{{\\an7\\pos({x+14:g},{y+14:g})\\p1\\bord0\\shad0\\1c&H323C07&}}'+shape,base(1)+f'{{\\an7\\pos({x:g},{y:g})\\p1\\bord3\\shad0\\1c&HFFFFFF&\\3c&H181B16&}}'+shape,base(2)+'{\\an5\\pos(960,970)\\bord0\\shad0}'+text])
 path=OUT/'candidate-body.ko.ass';path.write_text('\n'.join(h)+'\n','utf-8');return path
try:
 checkpoint()
 raw_probe=probe(ROOT/black['videoPath'],9072)
 raw_pts=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',ROOT/black['videoPath']],'all-raw-black-pts'))['frames']
 assert [int(v['best_effort_timestamp'])for v in raw_pts]==list(range(0,9072*1500,1500))
 ff(['-i',ROOT/black['videoPath'],'-f','null','-'],'whole-raw-black-decode')
 save(BASE/'measured-black-input-verification-v3.json',dict(videoPath=black['videoPath'],videoSha256=black['videoSha256'],frames=9072,plannedSegmentFrames=9071,probe=raw_probe,allPtsVerified=True,wholeDecodeExitCode=0,actualExportExitCode=export['exitCode'],scope='Current raw measured silent black input. No final animated/caption/pair approval.'))
 black_cursor=0;nb={x['id']:x for x in native['results']}
 for index,row in enumerate(plan['segments'],1):
  segment=dict(row,index=index)
  if row['role']=='explanation':
   a,b=black_cursor,black_cursor+row['frames'];black_cursor=b
   path=OUT/'segments'/f'{index:02}-{row["id"]}.mp4'
   # Remove only the confirmed inclusive terminal frame9071. Each planned
   # black interval retains exactly its own frame count and animation speed.
   ff(['-reinit_filter','0','-i',ROOT/black['videoPath'],'-map','0:v:0','-an','-map_metadata','-1','-vf',f'trim=start_frame={a}:end_frame={b},settb=1/90000,setpts=N*1500,setsar=1,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-frames:v',row['frames'],'-fps_mode','passthrough','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',path],'slice-measured-black')
   segment.update(path=rel(path),sha256=sha(path),probe=probe(path,row['frames']),blackSourceStartFrame=a,blackSourceEndFrameExclusive=b)
   s['completedBlackSegments']+=1
  else:segment.update(path=nb[row['id']]['path'],sha256=nb[row['id']]['sha256'],nativeAlreadyVerified=True)
  s['segments'].append(segment);checkpoint()
 assert black_cursor==9071 and len(s['segments'])==41
 listing=OUT/'concat-body.txt';listing.write_text('\n'.join("file '"+(ROOT/x['path']).as_posix().replace("'","'\\''")+"'"for x in s['segments'])+'\n','utf-8')
 body=OUT/'body.silent.mp4';ff(['-f','concat','-safe','0','-i',listing,'-map','0:v:0','-an','-map_metadata','-1','-c:v','copy','-video_track_timescale','90000','-movie_timescale','90000','-movflags','+faststart',body],'concat-selected-body')
 body_probe=probe(body,22677)
 pts=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',body],'all-body-pts'))['frames']
 assert [int(v['best_effort_timestamp'])for v in pts]==list(range(0,22677*1500,1500))
 ff(['-i',body,'-f','null','-'],'whole-selected-body-decode')
 ass=make_ass();samples={}
 def sample(frame,reason):
  frame=max(0,min(22676,frame));samples.setdefault(frame,dict(frame=frame,pts=frame*1500,reasons=[]))['reasons'].append(reason)
 for cue in cap['ko']:
  a=math.ceil((cue['startSeconds']-2)*60);b=math.ceil((cue['endSeconds']-2)*60)-1
  for frame in (a+1,(a+b)//2,b):sample(frame,dict(kind='literal-cue',cue=cue['index'],text=cue['ko']))
 for segment in s['segments']:
  a=segment['startFrame']-120;b=segment['endFrameExclusive']-120
  for frame in (a,a+1,b-2,b-1):sample(frame,dict(kind='cut-edge',segment=segment['id']))
  if segment['role']=='explanation':
   for fraction in (.02,.18,.38,.60,.82,.97):sample(a+round((b-a-1)*fraction),dict(kind='measured-spatial-motion',segment=segment['id'],fraction=fraction))
 for para in cap['paragraphs']:
  onset=min(c['startSeconds']for c in cap['ko']if (c['scene'],c['paragraph'])==(para['scene'],para['paragraph']))
  sample(math.ceil((onset-2)*60)+1,dict(kind='complete-paragraph-onset',scene=para['scene'],paragraph=para['paragraph']))
 planned=[samples[f]for f in sorted(samples)]
 assert set(v['cue']for r in planned for v in r['reasons']if v['kind']=='literal-cue')==set(range(1,202))
 assert set(v['segment']for r in planned for v in r['reasons']if v['kind']=='cut-edge')=={v['id']for v in s['segments']}
 assert planned[-1]['frame']==22676
 save(OUT/'qa-plan.json',dict(samples=planned,all201CuesCovered=True,all41CutsCovered=True,all17BlackMotionSegmentsCovered=True))
 select='+'.join(f'eq(pts\\,{x["pts"]})'for x in planned)
 ass_arg=rel(ass).replace(':','\\:')
 log=ff(['-reinit_filter','0','-i',body,'-vf',f"subtitles=filename='{ass_arg}',select={select},showinfo",'-fps_mode','vfr','-threads','2',QA/'sample-%04d.png'],'extract-all-selected-ASS-pixels')
 observed=[int(v)for v in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',log)]
 assert observed==[x['pts']for x in planned],(len(observed),len(planned))
 files=sorted(QA.glob('sample-*.png'));assert len(files)==len(planned)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);boards=[]
 for i in range(0,len(planned),6):
  board=Image.new('RGB',(1920,1758),(18,18,18));draw=ImageDraw.Draw(board)
  for j,row in enumerate(planned[i:i+6]):
   path=files[i+j];row.update(path=rel(path),sha256=sha(path))
   board.paste(Image.open(path).convert('RGB').resize((960,540)),((j%2)*960,(j//2)*586+40))
   expected=' / '.join(str(v.get('cue',v.get('segment',v.get('scene',''))))for v in row['reasons'])
   draw.text(((j%2)*960+10,(j//2)*586+7),f'f{row["frame"]} PTS{row["pts"]} {expected}'[:92],font=font,fill='white')
  path=QA/f'board-{i//6+1:03d}.jpg';board.save(path,quality=94)
  boards.append(dict(path=rel(path),sha256=sha(path),sampleFrames=[v['frame']for v in planned[i:i+6]]))
 proof=dict(schemaVersion=3,completedAt=now(),plan=rel(PLAN),planSha256=sha(PLAN),captionCandidate=rel(CAP),captionCandidateSha256=sha(CAP),bodyPath=rel(body),bodySha256=sha(body),bodyProbe=body_probe,segments=s['segments'],bodyFrames=22677,actualFrames=13606,explanationFrames=9071,allBodyPtsVerified=True,wholeBodyDecodeExitCode=0,extractionExitCode=0,allSamplePtsVerified=True,samples=planned,boards=boards,cues=201,cuts=41,blackSegments=17,allBoardsDirectlyRead=False,allInputCaptionPixelsReviewed=False,allFinalPixels=False,finalTimingApproved=False,finalMixedAsrApproved=False,qa=False,collected=False,private=False,localOnly=True,imagesGitAdded=0,sourceAudio=False)
 save(BASE/'selected-input-preflight-v3.json',proof)
 s.update(exitCode=0,status='selected-input-preflight-complete-direct-review-pending',completedAt=now(),bodyPath=rel(body),bodySha256=sha(body),sampleCount=len(planned),boardCount=len(boards));checkpoint()
 print(json.dumps(dict(inputs=41,bodyFrames=22677,ko=201,en=95,samples=len(planned),boards=len(boards),pixelReviewApproved=False)),flush=True)
except BaseException as e:
 s.update(exitCode=1,status='selected-input-preflight-failed-preserve-outputs',failedAt=now(),error=str(e),traceback=traceback.format_exc());checkpoint();raise
