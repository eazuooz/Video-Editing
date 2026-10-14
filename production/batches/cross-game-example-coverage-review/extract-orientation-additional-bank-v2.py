"""One CPU2/GPU0 audit of later Trailmakers only, after the avatar obstruction."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,os,re,subprocess,psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,x):
 t=p.with_name(p.name+'.'+str(os.getpid())+'.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
resource=read(ROOT/a.resource);assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85 and resource['freePhysicalMemoryKiB']>8_000_000
sp=O/'additional-bank-native-extraction-v2.json';dest=O/'additional-bank-native-v2';assert not sp.exists() and not dest.exists();dest.mkdir()
tts=read(O/'narration-07b-guide-repair-execution-v1.json');protected=tts['protectedInputs']+tts['results']
for x in protected:assert sha(ROOT/x['path'])==x['sha256']
windows=[dict(game='trailmakers',sourcePath='shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/sources/trailmakers-JvTCVUEc1ZE.mp4',nativeIn=42240,nativeOutExclusive=44100)]
old=[]
for file in ['selected-native-v1/manifest.json','repair-candidate-native-v1/manifest.json','annotation-anchor-native-v1/manifest.json','local-audit-pixels-v2/ncr/manifest.json','cross-game-native-v1/manifest.json','additional-bank-native-v1/manifest.json']:
 m=read(O/file)
 for x in m['samples']:old.append({**x,'sourceSha256':x.get('sourceSha256',m.get('sourceSha256')),'nativeFrame':x.get('nativeFrame',x.get('sourceFrame'))})
me=psutil.Process();me.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
s=dict(pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),cwd=me.cwd(),sessionId=None,resource=a.resource,startedAt=now(),cpuThreads=2,gpuJobs=0,status='preparing-new-native-only',completedSources=0,totalSources=1,exitCode=None,actualExitObserved=False,sources=[],samples=[],boards=[],freshSamples=0,reusedSamples=0,allPixelsApproved=False)
def checkpoint():
 p=sp.with_name(sp.stem+'.session.json')
 if p.exists():s['sessionId']=read(p)['sessionId']
 s['updatedAt']=now();save(sp,s);cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=now(),stage=s['status'],ownedJob=s,activeOwnedWorkers=int(s['exitCode'] is None),next='Actual exit/PTS/hash closure, then directly compare all63 later Trailmakers native samples/13boards. New bank and tracked allocation are unapproved until direct review.');save(O/'latest-checkpoint.json',cp)
 qpath=B/'queue.json';before=qpath.read_bytes();q=read(qpath);q['currentOrientationReview'].update(stage=cp['stage'],ownedJob=s,activeOwnedWorkers=cp['activeOwnedWorkers'],next=cp['next']);q['updatedAt']=now();assert qpath.read_bytes()==before;save(qpath,q)
checkpoint()
try:
 for w in windows:
  source=ROOT/w['sourcePath'];sourcehash=sha(source);probe=json.loads(subprocess.check_output([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,time_base,start_pts','-of','json',str(source)],text=True))['streams'][0]
  assert probe['time_base']=='1/15360' and probe['avg_frame_rate']=='60/1' and probe['start_pts']==0
  targets=sorted(set(range(w['nativeIn'],w['nativeOutExclusive'],30))|{w['nativeOutExclusive']-1});folder=dest/w['game'];folder.mkdir()
  reuse={f:next((x for x in old if x['nativeFrame']==f and x['sourceSha256']==sourcehash),None) for f in targets};fresh=[f for f in targets if reuse[f] is None]
  for f in targets:
   if reuse[f]:assert sha(ROOT/reuse[f]['path'])==reuse[f]['sha256'] and reuse[f]['pts']==f*256
  log=folder/'extract.log';cmd=[FF,'-hide_banner','-nostdin','-v','info','-threads','2','-filter_threads','1','-ss',str(max(0,w['nativeIn']/60-1)),'-copyts','-i',str(source),'-an','-vf',"select='"+'+'.join(f'eq(pts,{f*256})' for f in fresh)+"',showinfo,scale=1280:720",'-fps_mode','passthrough','-frames:v',str(len(fresh)),'-threads','2','-compression_level','3',str(folder/'sample-%04d.png')]
  rc=0
  if fresh:
   with log.open('x',encoding='utf-8') as stream:
    p=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT,cwd=ROOT);s.update(status='extracting-new-'+w['game'],ffmpegPid=p.pid,ffmpegCreateTime=psutil.Process(p.pid).create_time(),log=rel(log),ffmpegCommandLine=cmd);checkpoint();rc=p.wait()
   pts=[int(x) for x in re.findall(r'Parsed_showinfo_\d+.*?\bpts:\s*(-?\d+)',log.read_text('utf-8'))];files=sorted(folder.glob('sample-*.png'));assert rc==0 and pts==[f*256 for f in fresh] and len(files)==len(fresh)
   generated={f:dict(path=rel(p),sha256=sha(p)) for f,p in zip(fresh,files)}
  else:generated={}
  rows=[dict(game=w['game'],nativeFrame=f,pts=f*256,seconds=f/60,sourceSha256=sourcehash,path=(reuse[f] or generated[f])['path'],sha256=(reuse[f] or generated[f])['sha256'],reused=bool(reuse[f])) for f in targets]
  font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
  for offset in range(0,len(rows),5):
   group=rows[offset:offset+5];board=Image.new('RGB',(1280,1176),'#151515');d=ImageDraw.Draw(board)
   for j,row in enumerate(group):
    x=(j%2)*640;y=(j//2)*392
    with Image.open(ROOT/row['path']) as img:board.paste(img.resize((640,360)),(x,y))
    d.text((x+5,y+364),f'{w["game"]} f{row["nativeFrame"]} PTS{row["pts"]} {row["seconds"]:.3f}s',font=font,fill='white')
   p=folder/f'board-{offset//5+1:03}.png';board.save(p);s['boards'].append(dict(game=w['game'],path=rel(p),sha256=sha(p),samplePaths=[x['path'] for x in group]))
  s['sources'].append({**w,'sourceSha256':sourcehash,'probe':probe,'targetNativeFrames':targets,'ffmpegExitCode':rc,'exactPtsMatched':True,'log':rel(log),'command':cmd});s['samples']+=rows;s['freshSamples']+=len(fresh);s['reusedSamples']+=len(targets)-len(fresh);s['completedSources']+=1;checkpoint()
 for x in protected:assert sha(ROOT/x['path'])==x['sha256']
 manifest=dict(createdAt=now(),sources=s['sources'],samples=s['samples'],boards=s['boards'],freshSamples=s['freshSamples'],reusedSamples=s['reusedSamples'],exactSourcePtsVerified=True,sourcePlanningApproved=False,allBetweenFramesApproved=False,narrationTimedApproved=False,finalRatioApproved=False,newSourceCopies=0,newImageGit=0);save(dest/'manifest.json',manifest)
 s.update(status='new-bank-extracted-awaiting-direct-review',exitCode=0,finishedAt=now(),manifest=rel(dest/'manifest.json'),protectedShaMatched=True);checkpoint();print(json.dumps(dict(samples=len(s['samples']),boards=len(s['boards']),fresh=s['freshSamples'],reuse=s['reusedSamples'],exactPts=True)))
except BaseException as error:s.update(status='new-bank-extraction-failed-preserve',exitCode=1,error=repr(error),finishedAt=now());checkpoint();raise
