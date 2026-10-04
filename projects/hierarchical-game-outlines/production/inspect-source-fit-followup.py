"""Bounded native-frame inspection for speech/action fit; never final-cut approval."""
from pathlib import Path
import json, subprocess, hashlib, os, re, sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/hierarchical-game-outlines/production/source-fit-followup/native-fit-v2'
if '--curve-action-reserve' in sys.argv:
 BASE=ROOT/'projects/hierarchical-game-outlines/production/source-fit-followup/native-reserve-v3'
if '--remaining-fit-boundaries' in sys.argv:
 BASE=ROOT/'projects/hierarchical-game-outlines/production/source-fit-followup/native-remaining-v4'
if '--entrance-collision-fit' in sys.argv:
 BASE=ROOT/'projects/hierarchical-game-outlines/production/source-fit-followup/native-entrance-collision-v5'
if '--selected-support-fit' in sys.argv:
 BASE=ROOT/'projects/hierarchical-game-outlines/production/source-fit-followup/native-selected-support-v6'
BASE.mkdir(parents=True,exist_ok=True)
if (BASE/'index.json').exists():raise RuntimeError('Review existing source-fit inspection instead of repeating it.')
SOURCE=ROOT/'shared/assets/game-footage/hierarchical-game-outlines/I-ccSZ5J1Bo.mp4'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
ranges=[('curve-extension',2688,2716,[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]),
 ('camera-reserve',3160,3186,list(range(26))),
 ('late-menu-boundary',3272,3284,list(range(12)))]
if '--curve-action-reserve' in sys.argv:
 ranges=[('curve-action-reserve',2668,2692,list(range(24)))]
if '--remaining-fit-boundaries' in sys.argv:
 ranges=[('station-return',3183,3193,list(range(10))),
  ('entrance-extension',4622,4635,list(range(13))),
  ('flower-extension',4680,4696,list(range(16)))]
if '--entrance-collision-fit' in sys.argv:
 ranges=[('collision-tail',3045,3083,list(range(38))),
  ('entrance-reserve',4635,4662,list(range(27))),
  ('decoration-reserve',4696,4724,list(range(28)))]
if '--selected-support-fit' in sys.argv:
 ranges=[('support-return',3202,3210,[i/2 for i in range(16)]),
  ('support-shape-reserve',3233,3238,[i/2 for i in range(10)]),
  ('entrance-transition',4625.5,4628.5,[i/2 for i in range(6)]),
  ('entrance-menu-return',4632,4635,[i/2 for i in range(6)])]
rows=[];processes=[]
for name,start,end,points in ranges:
 dest=BASE/name;dest.mkdir(exist_ok=True)
 expr='+'.join(f'eq(n,{round(t*60)})' for t in points)
 # Bound the input before sparse selection, then cap the output frame count.
 # An output-only -t cannot stop when the last selected PTS precedes its end.
 command=[FF,'-hide_banner','-threads','1','-ss',str(start),'-t',str(end-start),'-i',str(SOURCE),'-map','0:v:0','-an','-vf',f"select='{expr}',showinfo,crop=1376:774:0:0",'-frames:v',str(len(points)),'-fps_mode','vfr','-q:v','3',str(dest/'frame-%03d.jpg')]
 log=BASE/(name+'.log')
 with log.open('w',encoding='utf-8') as out:
  child=subprocess.Popen(command,stdout=out,stderr=out);print(f'{name} PID {child.pid}',flush=True);code=child.wait()
 files=sorted(dest.glob('frame-*.jpg'));assert code==0 and len(files)==len(points),(name,code,len(files))
 text=log.read_text(encoding='utf-8');pts=[float(v) for v in re.findall(r'\bpts_time:([0-9.]+)',text)]
 assert len(pts)==len(points)
 for i,(f,t,actual) in enumerate(zip(files,points,pts),1):
  assert abs(actual-t)<1/60
  rows.append({'range':name,'sourceId':'I-ccSZ5J1Bo','sourceSeconds':start+t,'boundedDecodePts':actual,'frameOffset':round(t*60),'file':f.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 for page in range(0,len(files),12):
  selected=files[page:page+12];sheet=Image.new('RGB',(1920,((len(selected)+2)//3)*390),'white');draw=ImageDraw.Draw(sheet)
  for k,f in enumerate(selected):
   im=Image.open(f);im.thumbnail((640,360));x=(k%3)*640;y=(k//3)*390
   sheet.paste(im,(x,y+28));draw.text((x+8,y+6),f'{name} source {start+points[page+k]:.3f}s',fill='black')
  sheet.save(dest/f'sheet-{page//12+1:02d}.jpg',quality=94)
 processes.append({'range':name,'pid':child.pid,'exitCode':code,'command':command,'log':log.relative_to(ROOT).as_posix()})
report={'pid':os.getpid(),'method':'accurate bounded input seek, native 60fps frame selection and recorded relative PTS; face-free 1376x774 crop','status':'inspection-images-ready-for-direct-review','source':SOURCE.relative_to(ROOT).as_posix(),'processes':processes,'frames':rows,'finalSourceCutsApproved':False,'captionsApproved':False,'ratioApproved':False}
(BASE/'index.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Prepared {len(rows)} native fit/boundary research views; final action/caption approval remains pending.',flush=True)
