"""Seal already observed coarse boards; extract only new native target pixels."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,time,hashlib,subprocess,psutil,argparse
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
 for i in range(40):
  try:os.replace(t,p);return
  except PermissionError:
   if i==39:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);args=ap.parse_args();now=datetime.now(timezone.utc).isoformat()
resource=read(ROOT/args.resource);assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'].replace('Z','+00:00'))).total_seconds()<240
p=BASE/'fresh-primary-engineer02-inspection-v1.json';s=read(p)
assert s['exitCode']==0 and s['wholeDecodeExitCode']==0 and len(s['frames'])==162 and len(s['boards'])==27
assert not psutil.pid_exists(s['pid']) or abs(psutil.Process(s['pid']).create_time()-s['createTime'])>.01
for x in s['frames']+s['boards']:assert sha(ROOT/x['path'])==x['sha256']
for b in s['boards']:b['directlyRead']=True
s.update(allBoardsDirectlyRead=True,actualExitObserved=True,actualExitCodeObserved=0,processIdentityAbsentVerifiedAt=now)
save(p,s);sp=BASE/'fresh-primary-engineer02-inspection-v1.session.json';ss=read(sp);ss.update(status='closed-exit0-direct162-coarse-frames-read',actualExitObserved=True,exitCode=0,observedAt=now);save(sp,ss)
proof=BASE/'fresh-primary-engineer02-coarse-direct-review-v1.json';assert not proof.exists()
save(proof,dict(schemaVersion=1,reviewedAt=now,sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],sourceUrl=s['sourceUrl'],officialFolderUrl=s['officialFolderUrl'],all162FramesAnd27BoardsDirectlyRead=True,boards=s['boards'],wholeDecodeExitCode=0,actualExitObserved=0,sourceVersion=s['sourceVersion'],
 observationsKo='전체 162개 1Hz 프레임/27보드를 직접 읽었다. 전반의 적 회피/드론·발사체, 30초 이후 밝은 광물과 바위 채굴, 43–59초 좁은 길 추격, 61–73초 금빛 광물 접근·소실/Gold 증가, 79–90초 표시된 원과 중앙 장치 접근을 관찰했다. 28–29초/75초 LEVEL UP, 91–97초 SUPPLY POD, 156초 이후 LEVEL UP/OVERCLOCK 선택 화면은 실제 행동 배정에서 제외한다. 메뉴의 수치·이름은 효과·최적 전략 증거로 쓰지 않는다. 피해/성공/제작 의도/매출은 추정하지 않는다.',
 proposedNewIntervalsSeconds=[[43,59.7],[59.7,74],[77,90.8]],nativeEdgesAndFinalCaptionPixelsApproved=False,finalSourceAllocationApproved=False,publicRightsApproval='pending',localOnly=True,newGitRasterFiles=0))
dest=ROOT/'shared/output/similar-game-design/preflight/fresh-engineer02-native-v1';statep=BASE/'fresh-engineer02-native-extraction-v1.json';assert not dest.exists() and not statep.exists();dest.mkdir()
frames=sorted(set([2580,2581,2699,2700,2880,3060,3300,3390,3438,3581,3582,3583,3660,3780,3840,3900,4020,4260,4380,4427,4428,4439,4440,4599,4600,4620,4740,4800,4890,4980,5160,5280,5400,5447,5448,5460]))
me=psutil.Process();cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-hide_banner','-v','error','-threads','2','-i',str(ROOT/s['sourcePath']),'-an','-vf',"select='"+'+'.join(f'eq(n,{n})' for n in frames)+"',crop=2272:1278:144:0,scale=640:360",'-vsync','0','-filter_threads','2','-threads','2','-q:v','2',str(dest/'frame-%04d.jpg')]
state=dict(schemaVersion=1,pid=me.pid,createTime=me.create_time(),commandLine=me.cmdline(),startedAt=now,status='single-CPU2-native-target-extraction',cpuThreads=2,gpuJobs=0,sourcePath=s['sourcePath'],sourceSha256=s['sourceSha256'],resource=resource,wholeDecodeRepeated=False,coarseExtractionRepeated=False,exitCode=None,frames=[],boards=[],allBoardsDirectlyRead=False,localOnly=True);save(statep,state)
with (dest/'extract.log').open('w') as f:
 child=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);state.update(childPid=child.pid,currentCommand=cmd);save(statep,state);code=child.wait()
assert code==0
imgs=sorted(dest.glob('frame-*.jpg'));assert len(imgs)==len(frames)
state['frames']=[dict(path=rel(p),sha256=sha(p),sourceFrame=n,sourceSeconds=n/60) for p,n in zip(imgs,frames)]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
for offset in range(0,len(imgs),6):
 board=Image.new('RGB',(1280,1158),'white');d=ImageDraw.Draw(board)
 for j,img in enumerate(imgs[offset:offset+6]):
  x=j%2*640;y=j//2*386;board.paste(Image.open(img),(x,y+26));d.text((x+4,y),f'Engineer02 f{frames[offset+j]} / {frames[offset+j]/60:.6f}s',font=font,fill='black')
 p=dest/f'board-{offset//6+1:02d}.jpg';board.save(p,quality=96);state['boards'].append(dict(path=rel(p),sha256=sha(p),frames=frames[offset:offset+6],directlyRead=False))
state.update(status='closed-native-targets-awaiting-direct-review',exitCode=0,childPid=None,finishedAt=datetime.now(timezone.utc).isoformat());save(statep,state)
print(json.dumps(dict(frames=len(imgs),boards=len(state['boards']),exitCode=0,coarseFramesSealed=162)))
