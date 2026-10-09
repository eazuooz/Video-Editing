"""Extract changed final pixels; reuse only proven identical decoded pixels."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,re,subprocess,time,traceback
import psutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
OLD=BASE/'revision-balatro60-v2/final-v3';W=BASE/'revision-balatro60-v2/final-v4'
DEST=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/final-encoded-caption-qa-v4'
STATE=W/'encoded-caption-qa-execution.json';SESSION=W/'encoded-caption-qa-session.json'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
r=read(ROOT/a.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<240
assert not STATE.exists() and not DEST.exists(),'Resume actual job; do not repeat extraction.'
done=read(W/'source-only-pair-execution.json');assert done['exitCode']==done['actualOuterExitCode']==0 and done['outerExitDirectlyObserved']
pair=read(W/'review-pair-build.json');identity=read(W/'unchanged-pixel-identity.json')
assert identity['all18848OutsideCutDecodedFramesIdentical'] and identity['changedFrames']==list(range(3142,4282))
oldex=read(OLD/'encoded-caption-qa-execution.json');assert oldex['exitCode']==oldex['outerExitCode']==0 and oldex['allActualPtsMatched']
source=W/'presenting-game-scores.captioned.mp4'
assert sha(source)==identity['newSourceSha256'] and sha(ROOT/oldex['source'])==identity['oldSourceSha256']
assert sha(ROOT/identity['oldFrameHashFile'])==identity['oldFrameHashFileSha256'] and sha(ROOT/identity['newFrameHashFile'])==identity['newFrameHashFileSha256']
for row in oldex['samples']+oldex['boards']:assert sha(ROOT/row['path'])==row['sha256']
request=read(OLD/'encoded-caption-qa-request.json');request.update(createdAt=now(),planSha256=sha(W/'plan.json'),
 correction='classic-02-equality-remainder native2250..2725',previousRequest=rel(OLD/'encoded-caption-qa-request.json'),
 previousRequestSha256=sha(OLD/'encoded-caption-qa-request.json'),decodedPixelReuseProof=rel(W/'unchanged-pixel-identity.json'),
 decodedPixelReuseProofSha256=sha(W/'unchanged-pixel-identity.json'),actualExtractionStarted=True)
assert len(request['points'])==1112
save(W/'encoded-caption-qa-request.json',request)
if os.name=='nt':ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x00004000)
DEST.mkdir();(DEST/'frames').mkdir();(DEST/'boards').mkdir();p=psutil.Process()
s=dict(schemaVersion=4,slug='presenting-game-scores',pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),sessionId=None,
 startedAt=now(),status='extracting-only-corrected-final-pixels',resourceEvidence=a.resource,cpuThreads=2,gpu=0,singleJob=True,
 exitCode=None,activeTask=None,source=rel(source),sourceSha256=sha(source),requestPath=rel(W/'encoded-caption-qa-request.json'),
 requestSha256=sha(W/'encoded-caption-qa-request.json'),samples=[],boards=[],allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,
 imagesLocalOnly=True,newGitImages=0,identicalDecodedPixelReuse=rel(W/'unchanged-pixel-identity.json'))
def checkpoint():
 if SESSION.exists():
  x=read(SESSION)
  if x['pid']==s['pid'] and abs(x['createTime']-s['createTime'])<.01:s['sessionId']=x['sessionId']
 s['observedAt']=now();save(STATE,s)
 job=dict(pid=s['pid'],createTime=s['createTime'],command=s['command'],cwd=s['cwd'],sessionId=s['sessionId'],state=rel(STATE),status=s['status'],
  cpuThreads=2,gpu=0,singleJob=True,activeTask=s['activeTask'],exitCode=s['exitCode'],workerExpectedRunning=s['exitCode'] is None)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=s['status'],ownedJob=job,recordedAt=now(),encodedPixelExecution=rel(STATE),
  allFinalPixels=False,qa=False,collected=False,private=False,nextAction='Read corrected encoded boards30..41 and all remaining unchanged boards, then seal actual current pixel coverage.');save(BASE/'latest-checkpoint.json',cp)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
 for _ in range(8):
  raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items']if x['slug']=='presenting-game-scores')
  i.update(stage=s['status'],currentExecution=job,currentJob=job,ownedJob=job,encodedPixelExecution=rel(STATE),allFinalPixels=False,qa=False,collected=False,uploaded=False,nextAction=cp['nextAction']);q['updatedAt']=now()
  if qp.read_text('utf-8-sig')==raw:save(qp,q);break
 else:raise RuntimeError('Concurrent queue preserved')
try:
 checkpoint();changed=[row for row in oldex['samples']if 3142<=row['frame']<4282];assert len(changed)==66
 expression="select='"+'+'.join(f'eq(pts,{row["frame"]*1500})'for row in changed)+"',showinfo"
 filter_path=DEST/'absolute-pts-select.filter';filter_path.write_text(expression,'utf-8')
 command=[str(FF),'-hide_banner','-v','info','-nostdin','-threads','2','-reinit_filter','0','-i',str(source),'-an',
  '-filter_threads','1','-filter_script:v',str(filter_path),'-fps_mode','passthrough','-frames:v',str(len(changed)),'-threads','2',str(DEST/'frames/changed-%04d.png')]
 log=DEST/'extract.log'
 with log.open('w',encoding='utf-8')as stream:
  child=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  s['activeTask']=dict(pid=child.pid,createTime=psutil.Process(child.pid).create_time(),command=command,log=rel(log));checkpoint();code=child.wait()
 assert code==0,(code,rel(log))
 pts=[int(x)for x in re.findall(r'\[Parsed_showinfo[^\]]*\]\s+n:\s*\d+\s+pts:\s*(\d+)',log.read_text('utf-8-sig'))]
 assert pts==[row['frame']*1500 for row in changed]
 files=sorted((DEST/'frames').glob('changed-*.png'));assert len(files)==66
 replacement={row['index']:(path,actual)for row,path,actual in zip(changed,files,pts)}
 for old in oldex['samples']:
  row=dict(old,directlyRead=False)
  if old['index']in replacement:
   path,actual=replacement[old['index']];row.update(path=rel(path),sha256=sha(path),decodedPts=actual,
    reusedIdenticalPixels=False,correctedNativeFrame=2250+(old['frame']-3142)*25//60)
  else:row.update(reusedIdenticalPixels=True,decodedPixelIdentityProof=rel(W/'unchanged-pixel-identity.json'))
  s['samples'].append(row)
 s.update(status='creating-only-corrected-review-boards',activeTask=None);checkpoint();font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
 for oldboard in oldex['boards']:
  rows=[s['samples'][i-1]for i in oldboard['sampleIndices']]
  if any(not row['reusedIdenticalPixels']for row in rows):
   board=Image.new('RGB',(1920,1740),(18,18,18));draw=ImageDraw.Draw(board)
   for slot,row in enumerate(rows):
    x,y=slot%2*960,slot//2*580
    with Image.open(ROOT/row['path'])as im:assert im.size==(1920,1080);board.paste(im.resize((960,540)),(x,y+40))
    draw.text((x+5,y+4),f'{row["index"]:04d} f{row["frame"]} {row["segment"][:32]} cue{row["visibleCueIds"]}',font=font,fill='white')
   path=DEST/f'boards/board-{oldboard["index"]:03d}.jpg';board.save(path,quality=94,subsampling=0)
   s['boards'].append(dict(index=oldboard['index'],path=rel(path),sha256=sha(path),sampleIndices=oldboard['sampleIndices'],directlyRead=False,reusedIdenticalPixels=False))
  else:s['boards'].append(dict(oldboard,directlyRead=False,reusedIdenticalPixels=True))
 s.update(status='closed-corrected-final-pixels-awaiting-full-direct-review',exitCode=0,endedAt=now(),activeTask=None,
  sampleCount=1112,boardCount=186,newExtractedSamples=66,newBoards=12,reusedSamples=1046,reusedBoards=174,allActualPtsMatched=True);checkpoint()
 print(json.dumps(dict(exitCode=0,newExtractedSamples=66,newBoards=12,reusedSamples=1046,reusedBoards=174,allFinalPixels=False)),flush=True)
except BaseException:
 s.update(status='closed-corrected-final-pixel-extraction-failed',exitCode=1,endedAt=now(),activeTask=None,error=traceback.format_exc());checkpoint();raise
