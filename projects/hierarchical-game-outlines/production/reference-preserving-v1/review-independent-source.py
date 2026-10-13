from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,psutil,argparse
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4]
N=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--session',type=int,required=True);ap.add_argument('--initial',required=True);ap.add_argument('--completion',required=True);args=ap.parse_args()
MEDIA=ROOT/f'shared/assets/game-footage/hierarchical-game-outlines-smash/{args.source}.mp4'
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
OUT=N/f'qa-independent-{args.source}-v1'
OUT.mkdir(exist_ok=False)
resources={'at':datetime.now(timezone.utc).isoformat(),'cpuPercent':psutil.cpu_percent(interval=1),'availableRam':psutil.virtual_memory().available,'gpu':subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader'],text=True).strip(),'processes':[]}
for p in psutil.process_iter(['pid','name','cmdline','create_time','cwd']):
 if any(x in (p.info['name'] or '').lower() for x in ['python','ffmpeg','node','falcor','mogwai']):resources['processes'].append(p.info)
(N/f'resources-extract-{args.source}-v1.json').write_text(json.dumps(resources,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cmd=[FF,'-hide_banner','-loglevel','error','-threads','2','-i',str(MEDIA),'-vf','fps=1/10,scale=480:-2','-an','-threads','2',str(OUT/'frame-%03d.jpg')]
r=subprocess.run(cmd);assert r.returncode==0
paths=sorted(OUT.glob('frame-*.jpg'))
for i in range(0,len(paths),12):
 board=Image.new('RGB',(1440,4*306),'#172025');d=ImageDraw.Draw(board)
 for k,p in enumerate(paths[i:i+12]):
  im=Image.open(p);x=(k%3)*480;y=(k//3)*306;board.paste(im,(x,y));d.text((x+8,y+274),f'Approx. source {((i+k)*10)+5:.0f}s',fill='white')
 board.save(OUT/f'board-{i//12+1:02}.jpg',quality=92)
receipt={'at':datetime.now(timezone.utc).isoformat(),'source':str(MEDIA.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(MEDIA.read_bytes()).hexdigest(),'download':{'session':args.session,'initial':args.initial,'completion':args.completion,'exit':0},'extractionExit':0,'samples':len(paths),'cadenceSeconds':10,'samplingOffsetApproximately':5,'boards':[str(p.relative_to(ROOT)).replace('\\','/') for p in sorted(OUT.glob('board-*.jpg'))],'productionAdopted':False,'directReview':'pending','publicRightsApproved':False}
(N/f'acquisition-{args.source}-v1.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt,ensure_ascii=False))
