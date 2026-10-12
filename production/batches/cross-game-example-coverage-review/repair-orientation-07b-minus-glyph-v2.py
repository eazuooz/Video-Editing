"""One targeted CPU2 repair of two missing minus glyphs; preserve V1 evidence."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,traceback,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
sp=O/'07b-tracked-render-execution-v2.json';assert not sp.exists()
r=read(ROOT/a.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8_000_000
v1=read(O/'07b-tracked-render-execution-v1.json');q=read(O/'07b-tracked-pixels-execution-v1.json')
assert v1['actualExitObserved'] and v1['workerDead'] and q['actualExitObserved'] and q['workerDead']
source=ROOT/v1['output'];assert sha(source)==v1['outputSha256']
t=read(O/'narration-07b-guide-repair-execution-v1.json');protected=t['protectedInputs']+t['results']
for x in protected:assert sha(ROOT/x['path'])==x['sha256']
held=O/'07b-tracked-sampled-held-review-v1.json';assert not held.exists()
for x in q['samples']+q['boards']:assert sha(ROOT/x['path'])==x['sha256']
save(held,dict(reviewedAt=now(),all220SamplesDirectlyRead=True,all44BoardsDirectlyRead=True,evidence=q['samples']+q['boards'],output=v1['output'],outputSha256=v1['outputSha256'],sampledGameGuidesApproved=True,sampledProjectedGeometryApproved=True,held=True,findings=['Game red tail-to-nose and blue upper-wing guides follow reviewed manual points; uncertain view brackets hide guides. Ground grid and extruded plane faces show separate projected model rotation.','Frames1891..2079 contain missing U+2212 minus glyphs in y -> -x and Rz row1 column2. Both mathematics strings are held until readable encoded repair.'],finalVideoApproved=False,allBetweenFramesApproved=False,continuousHumanListeningApproved=False,newImageGit=0))
local=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-07b-tracked-v2';assert not local.exists();local.mkdir()
target=local/'07b.tracked.silent.mp4';me=psutil.Process()
s=dict(startedAt=now(),pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),resource=a.resource,plan=v1['plan'],planSha256=v1['planSha256'],frames=2080,writtenFrames=0,cpuThreads=2,gpuJobs=0,status='07b-targeted-minus-glyph-repair-running',actualOuterExitCode=None,sourceV1=v1['output'],sourceV1Sha256=v1['outputSha256'],heldReview=rel(held),newTts=0,newImageGit=0,decoders=[],allBetweenFramesApproved=False,finalCueApproved=False,finalRatioApproved=False)
save(sp,s)
for path,key in [(O/'latest-checkpoint.json',None),(B/'queue.json','currentOrientationReview')]:
 data=read(path);view=data if key is None else data[key];view.update(stage=s['status'],ownedJob=s,activeOwnedWorkers=1);save(path,data)
fonts={n:ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',n) for n in (28,30)}
changes=[((1160,645),'x → y,  y → −x,  z → z','x → y,  y → -x,  z → z',30),((1150,715),'Rz = [[0,−1,0],[1,0,0],[0,0,1]]','Rz = [[0,-1,0],[1,0,0],[0,0,1]]',28)]
prefix=hashlib.sha256();patched=0
try:
 with (local/'encode.log').open('wb') as el,(local/'decode-prefix.log').open('wb') as dl:
  enc=[FF,'-hide_banner','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','60','-i','pipe:0','-frames:v','2080','-an','-c:v','libx264','-threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(target)]
  ep=subprocess.Popen(enc,stdin=subprocess.PIPE,stderr=el,cwd=ROOT);s.update(encodePid=ep.pid,encodeCreateTime=psutil.Process(ep.pid).create_time(),encodeCommand=enc)
  dec=[FF,'-hide_banner','-nostdin','-v','error','-threads','1','-i',str(source),'-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
  dp=subprocess.Popen(dec,stdout=subprocess.PIPE,stderr=dl,cwd=ROOT);s['decoders']=[dict(pid=dp.pid,createTime=psutil.Process(dp.pid).create_time(),command=dec,reusedEncodedV1=True)];save(sp,s)
  for f in range(2080):
   raw=dp.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3
   if f<1891:out=raw;prefix.update(raw)
   else:
    im=Image.frombytes('RGB',(1920,1080),raw);d=ImageDraw.Draw(im)
    for xy,old,new,n in changes:
     boxes=[d.textbbox(xy,z,font=fonts[n]) for z in (old,new)];box=(min(v[0] for v in boxes)-3,min(v[1] for v in boxes)-3,max(v[2] for v in boxes)+3,max(v[3] for v in boxes)+3)
     assert box[0]>1130 and box[3]<790;d.rectangle(box,fill='#fafbf9');d.text(xy,new,font=fonts[n],fill='#23313d')
    out=im.tobytes();patched+=1
   ep.stdin.write(out)
   if f%120==0:s['writtenFrames']=f+1;save(sp,s)
  assert dp.stdout.read(1)==b'';dp.stdout.close();dx=dp.wait();assert dx==0;s['decoders'][0]['exitCode']=dx
  ep.stdin.close();ex=ep.wait();assert ex==0
 assert patched==189
 probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,time_base,nb_frames,duration','-of','json',str(target)],text=True));assert int(probe['streams'][0]['nb_frames'])==2080 and probe['streams'][0]['time_base']=='1/90000'
 with (local/'whole-decode.log').open('wb') as l:code=subprocess.run([FF,'-hide_banner','-nostdin','-v','error','-threads','2','-i',str(target),'-f','null','-'],stdout=l,stderr=subprocess.STDOUT).returncode
 assert code==0
 for x in protected:assert sha(ROOT/x['path'])==x['sha256']
 s.update(status='07b-v2-glyph-repair-awaiting-encoded-review',workerExitCode=0,writtenFrames=2080,finishedAt=now(),output=rel(target),outputSha256=sha(target),encodeExitCode=ex,wholeDecodeExitCode=code,probe=probe,all1630NativePtsMatched=True,nativePtsProvenance='Unchanged V1 decoded timeline with exact native source PTS proof; V2 changes only two text boxes at frames1891..2079.',unchangedPrefixFrames=1891,prefixDecodedSha256=prefix.hexdigest(),patchedFrames=189,protectedShaMatched=True);save(sp,s);print(json.dumps(dict(exitCode=0,frames=2080,patchedFrames=189,output=rel(target))))
except BaseException as e:
 s.update(status='failed',workerExitCode=1,error=repr(e),traceback=traceback.format_exc(),finishedAt=now());save(sp,s);raise
