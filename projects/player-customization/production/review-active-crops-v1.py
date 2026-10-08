"""One CPU research job. Exact incoming PTS samples, not final caption QA or quota approval."""
import os,sys,json,subprocess,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
R=Path('D:/Github/Video-Editing');P=R/'projects/player-customization/production';O=R/'shared/output/player-customization/research/active-crop-review-v1'
if O.exists():raise SystemExit('Existing review evidence preserved; inspect rather than rerun.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
sources={
'gauss':R/'shared/output/player-customization/research/gauss-profile-v1/gb9JKmJ5-6g.mp4',
'jade':R/'shared/output/player-customization/research/jade-demo-v1/ovxaYxLbUNE-jade-1280-1898.mp4'}
expected={'gauss':'dc1c979cfab57fab126d13e385e9f2b8657036307190d6d122bdab025b241b20','jade':'18e18801dc315747bdd098111c64946e387ed95b73685b2e9998399d60fcc303'}
for k,p in sources.items():assert sha(p)==expected[k],k
groups=[
('gauss-rush','gauss',25.5,32,(0,0,1920,1080)),
('gauss-plating','gauss',39.5,46.5,(0,0,1920,1080)),
('gauss-sunder','gauss',50,65,(0,0,1920,1080)),
('gauss-redline','gauss',71.5,93,(0,0,1920,1080)),
('jade-ground-a','jade',44,54,(634,150,1152,648)),
('jade-ground-b','jade',72,84,(634,150,1152,648)),
('jade-support','jade',134,171,(634,150,1152,648)),
('jade-air','jade',171,194,(634,150,1152,648)),
('yareli-trial','jade',517,550,(664,138,1120,630))]
O.mkdir();(O/'boards').mkdir()
state=dict(schemaVersion=1,status='running',startedAt=now(),pid=os.getpid(),commandLine=[sys.executable,*sys.argv],cpuThreads=2,gpu=0,singleJob=True,resourcesEvidence='shared/output/player-customization/research/resources-before-active-crops-v1.json',sourceSha256=expected,operations=[],samples=[],boards=[],allRasterLocalOnly=True,sourceAudioUsed=False,directPixelsReviewed=False,continuousMotionApproved=False,exactFinalCutBoundariesApproved=False,footageQuotaApproved=False,finalCaptionPixelsApproved=False)
def save(): (P/'active-crop-execution-v1.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
lines=['선택한 능력의 범위와 움직임을 봅니다.','이 문구는 고정 자막 자리만 확인하는 시험입니다.']
for name,source,start,end,crop in groups:
 d=O/name;d.mkdir();x,y,w,h=crop;assert w*9==h*16
 log=O/(name+'.log');vf=f"select='isnan(prev_selected_t)+gte(t-prev_selected_t,1)',crop={w}:{h}:{x}:{y},scale=1920:1080:flags=lanczos,showinfo"
 cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-nostdin','-v','info','-threads','2','-ss',str(start),'-t',str(end-start),'-i',str(sources[source]),'-vf',vf,'-fps_mode','vfr','-an','-threads','2',str(d/'sample-%03d.png')]
 with log.open('w',encoding='utf-8') as f:
  proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);op=dict(name=name,pid=proc.pid,startedAt=now(),commandLine=cmd,log=log.relative_to(R).as_posix());state['operations'].append(op);save();code=proc.wait()
 op.update(exitCode=code,finishedAt=now());save()
 if code:raise SystemExit(f'{name} failed {code}; preserve completed outputs')
 pts=[float(v) for v in re.findall(r'Parsed_showinfo[^\n]*\bn:\s*\d+[^\n]*\bpts_time:([^ ]+)',log.read_text(encoding='utf-8'))]
 files=sorted(d.glob('sample-*.png'));assert len(files)==len(pts),(name,len(files),len(pts))
 for f,t in zip(files,pts):
  im=Image.open(f).convert('RGB');dr=ImageDraw.Draw(im);tw=max(dr.textlength(s,font=font) for s in lines);box=(round(960-tw/2-22),round(970-62-11),round(960+tw/2+22),round(970+62+11))
  dr.rectangle(tuple(v+14 if i%2==0 else v+14 for i,v in enumerate(box)),fill='#073c32');dr.rectangle(box,fill='white',outline='#161b18',width=3)
  for i,s in enumerate(lines):dr.text((960,970-62+62*i),s,anchor='mt',fill='#080b09',font=font)
  im.save(f)
  state['samples'].append(dict(group=name,source=source,sourcePath=sources[source].relative_to(R).as_posix(),sourceSha256=expected[source],requestedLocalRange=[start,end],selectedInputPtsRelative=t,selectedLocalSecond=round(start+t,6),nominalOriginalSecond=round(start+t+(1280 if source=='jade' else 0),6),cropXYWH=crop,path=f.relative_to(R).as_posix(),sha256=sha(f),caption='Prototype position/worst two-line box only, not final cue',directlyRead=False))
 print(json.dumps({'group':name,'samples':len(files),'pid':os.getpid()}),flush=True);save()
for offset in range(0,len(state['samples']),4):
 rows=state['samples'][offset:offset+4];can=Image.new('RGB',(1920,1170),'white');dr=ImageDraw.Draw(can)
 for k,row in enumerate(rows):
  x=k%2*960;y=k//2*585;can.paste(Image.open(R/row['path']).resize((960,540)),(x,y+45));dr.text((x+8,y+8),f"{row['group']} | local {row['selectedLocalSecond']:.3f}s",font=label,fill='black')
 f=O/'boards'/f'board-{offset//4+1:02d}.png';can.save(f);state['boards'].append(dict(path=f.relative_to(R).as_posix(),sha256=sha(f),samplePaths=[r['path'] for r in rows],directlyRead=False))
state.update(status='extracted-direct-review-pending',finishedAt=now(),exitCode=0,sampleCount=len(state['samples']),boardCount=len(state['boards']));save()
print(json.dumps({'status':state['status'],'pid':state['pid'],'sampleCount':state['sampleCount'],'boardCount':state['boardCount'],'next':'Read every board and continuous actions; select unique exact cuts. This is not final QA.'}),flush=True)
