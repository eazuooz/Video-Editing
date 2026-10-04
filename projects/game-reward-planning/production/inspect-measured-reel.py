"""Inspect measured white paragraph motion, study, cat and original members."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;version=sys.argv[1] if len(sys.argv)>1 else 'v1';WORK=BASE/('measured-reel-'+version);DEST=WORK/'inspection';DEST.mkdir(exist_ok=False)
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';FP='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';FILE=ROOT/('shared/output/motion-canvas/game-reward-planning-measured-reel-'+version+'.mp4');plan=json.loads((ROOT/'motion-canvas/src/projects/game-reward-planning/measured-reel-plan.json').read_text(encoding='utf8'))
state={'pid':os.getpid(),'status':'running','startedAt':datetime.now(timezone.utc).isoformat(),'gpuJobs':0};(DEST/'execution.json').write_text(json.dumps(state)+'\n',encoding='utf8');rows=[]
for s in plan['scenes']:
 start=0
 for p,z in enumerate(s['paragraphEnds'],1):
  for phase,t in [('early',min(z-.05,start+.55)),('late',max(start,z-.16))]:rows.append({'id':s['id']+'p'+str(p)+'-'+phase,'scene':s['id'],'frame':s['startFrame']+round(t*60),'phase':phase,'paragraph':p})
  start=z
for sid,start,offsets in [('cat',0,[0,60,119]),('study',plan['studyStartFrame'],[20,90,140,220,280,359]),('members',plan['outroStartFrame'],[0,60,300,599])]:
 for n in offsets:rows.append({'id':sid+'-'+str(n),'scene':sid,'frame':start+n})
points=sorted(set(r['frame'] for r in rows));vf="select='"+'+'.join('eq(n\\,%d)'%n for n in points)+"'"
with (DEST/'extract.log').open('w') as log:subprocess.run([FF,'-v','error','-threads','2','-i',str(FILE),'-vf',vf,'-fps_mode','vfr','-q:v','2',str(DEST/'frame-%03d.jpg')],stdout=log,stderr=log,check=True)
files=sorted(DEST.glob('frame-*.jpg'));assert len(files)==len(points);mapping={n:f for n,f in zip(points,files)}
for r in rows:r['image']=mapping[r['frame']].relative_to(ROOT).as_posix();r['directlyRead']=False
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);pages=[]
for offset in range(0,len(rows),24):
 page=Image.new('RGB',(1920,1800),'#eeeeee');d=ImageDraw.Draw(page)
 for j,r in enumerate(rows[offset:offset+24]):
  x=j%4*480;y=j//4*300;page.paste(Image.open(ROOT/r['image']).resize((480,270)),(x,y));d.text((x+4,y+272),f"{r['id']} frame{r['frame']}",font=font,fill='black')
 f=DEST/f'page-{len(pages)+1:02d}.jpg';page.save(f,quality=97);pages.append(f.relative_to(ROOT).as_posix())
probe=json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(FILE)],text=True));decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(FILE),'-f','null','-'],capture_output=True,text=True);(DEST/'full-decode.log').write_text(decode.stderr,encoding='utf8');assert decode.returncode==0 and not decode.stderr
record={'source':FILE.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(FILE.read_bytes()).hexdigest(),'rows':rows,'pages':pages,'probe':probe,'fullDecodeExitCode':0,'decodeErrors':0,'silentReviewOnly':True,'finalNarratedVideoApproved':False,'directReading':'pending'};(DEST/'index.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');state.update(status='finished-awaiting-direct-reading',exitCode=0,endedAt=datetime.now(timezone.utc).isoformat());(DEST/'execution.json').write_text(json.dumps(state)+'\n',encoding='utf8');print(json.dumps({'views':len(rows),'pages':len(pages),'silent':True,'decodeErrors':0}))
