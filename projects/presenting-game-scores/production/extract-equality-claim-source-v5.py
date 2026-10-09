"""Inspect a new 90..109s normal-speed source candidate; no adoption or approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, re, subprocess, psutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent/'revision-balatro60-v2'
OUT=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/equality-claim-source-v5'
FF=Path('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe')
read=lambda p:json.loads(p.read_text('utf-8-sig')); rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+'.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
ap=argparse.ArgumentParser();ap.add_argument('--resource',required=True);a=ap.parse_args()
r=read(ROOT/a.resource);assert r['ownHeavyJobs']==0 and r['cpuLoadPercent']<85 and r['freePhysicalMemoryKiB']>8000000
assert (datetime.now(timezone.utc)-datetime.fromisoformat(r['observedAt'])).total_seconds()<180
assert not (B/'equality-claim-source-extraction-v5.json').exists()
assert not OUT.exists() or not any(x.is_file() for x in OUT.rglob('*')), 'Preserve any existing extraction'
OUT.mkdir(exist_ok=True);(OUT/'frames').mkdir(exist_ok=True);(OUT/'boards').mkdir(exist_ok=True)
source=ROOT/'shared/assets/presenting-game-scores/raw/TEC_B-roll_MP-ClassicScoreAttack.mp4'
assert sha(source)=='8271e3dd4e6e3e0a13046471c553516f432f0fcdd767a840f01fcb3bb776c946'
f=read(B/'final-v3/encoded-caption-qa-request.json')
# Native25fps: ceiling maps each final60fps observation to the first source frame at/after that moment.
native={2250+i*10 for i in range(48)}|{2724}
for sample in f['points']:
 final=sample['frame']
 if 3142<=final<4282:native.add(2250+((final-3142)*25+59)//60)
native=sorted(x for x in native if 2250<=x<2725)
expr='+'.join(f'eq(pts\\,{n*1000})' for n in native)
vf=f'select={expr},showinfo,split=2[b][f];[b]gblur=sigma=24:steps=2[bg];[f]crop=1920:960:0:120[fg];[bg][fg]overlay=0:0:shortest=1[v]'
cmd=[str(FF),'-nostdin','-v','info','-threads','2','-filter_threads','1','-filter_complex_threads','1','-reinit_filter','0','-i',str(source),'-filter_complex',vf,'-map','[v]','-an','-fps_mode','vfr','-threads','2',str(OUT/'frames/native-%04d.png')]
p=psutil.Process();state=dict(startedAt=now(),pid=p.pid,createTime=p.create_time(),command=p.cmdline(),cwd=p.cwd(),resource=a.resource,source=rel(source),sourceSha256=sha(source),candidateNativeFrames=[2250,2725],candidateSeconds=[90,109],cpuThreads=2,gpuJobs=0,adopted=False,approved=False,allFinalPixels=False,exitCode=None,sessionId=None)
ep=B/'equality-claim-source-extraction-v5.json';save(ep,state)
try:
 log=OUT/'extraction.log'
 with log.open('w',encoding='utf-8') as stream:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  state.update(childPid=child.pid,childCreateTime=psutil.Process(child.pid).create_time(),childCommand=cmd,log=rel(log));save(ep,state);code=child.wait()
 assert code==0,log
 observed=[int(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*(\d+)',log.read_text('utf-8-sig'))]
 assert observed==[n*1000 for n in native],(observed,native)
 paths=sorted((OUT/'frames').glob('native-*.png'));assert len(paths)==len(native)
 rows=[dict(path=rel(path),sha256=sha(path),nativeFrame=n,nativePts=n*1000,seconds=n/25,nominalFinalFrame=3142+(n-2250)*60/25) for path,n in zip(paths,native)]
 boards=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
 for i in range(0,len(rows),6):
  group=rows[i:i+6];im=Image.new('RGB',(1920,1740),(18,18,18));d=ImageDraw.Draw(im)
  for j,row in enumerate(group):
   x=j%2*960;y=j//2*580;im.paste(Image.open(ROOT/row['path']).convert('RGB').resize((960,540)),(x,y+40));d.text((x+8,y+8),f'native f{row["nativeFrame"]} PTS{row["nativePts"]} t{row["seconds"]:.3f} -> final{row["nominalFinalFrame"]:.1f}',font=font,fill='white')
  path=OUT/'boards'/f'board-{i//6+1:03d}.jpg';im.save(path,quality=94);boards.append(dict(path=rel(path),sha256=sha(path),nativeFrames=[x['nativeFrame'] for x in group]))
 state.update(completedAt=now(),exitCode=0,childExitCode=code,samples=rows,boards=boards,sampleCount=len(rows),boardCount=len(boards),exactNativePtsVerified=True)
 save(ep,state);print(json.dumps({k:state[k] for k in ['exitCode','sampleCount','boardCount','adopted','approved']}))
except BaseException as e:
 state.update(exitCode=1,error=repr(e));save(ep,state);raise
