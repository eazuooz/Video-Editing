"""Trial narrower cues and source-only reframing on the affected v5 cuts.

No final video, audio change, caption relocation or approved pixel gate here.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,subprocess,time,traceback
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
WORK=BASE/'measured-edit-v5';DEST=WORK/'remaining-two-motion-framing-local-v3'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
 temp=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(20):
  try:temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p);return
  except PermissionError:
   if n==19:raise
   time.sleep(.1)
assert not DEST.exists();DEST.mkdir()
plan=read(WORK/'plan.json');compiled=read(WORK/'native-review-v1/compiled.json');layout=read(WORK/'caption-layout-v1.json')
flagged={'02-p4-action-21-1410-1455','06-p2-action-31-900-945'}
cuts=[c for s in plan['scenes'] for c in s['segments'] if c['id'] in flagged]
assert len(cuts)==2
state={'startedAt':now(),'pid':os.getpid(),'sessionId':None,'status':'CPU-two-motion-framing-only','threads':2,
 'activeTasks':[],'images':[],'sheets':[],'completedCuts':0,'totalCuts':len(cuts),
 'planSha256':sha(WORK/'plan.json'),'captionLayoutSha256':sha(WORK/'caption-layout-v1.json'),'allFinalPixelsApproved':False,'newGitImages':0}
def save():
 state['updatedAt']=now();write(DEST/'execution.json',state)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);i=next(i for i in q['items'] if i['slug']=='avoid-game-comparisons')
 i.update(stage='current15-two-targeted-motion-framing-repair',updatedAt=state['updatedAt'])
 i['execution'].update(observedAt=state['updatedAt'],phase=i['stage'],status=state['status'],pid=state['pid'],sessionId=state['sessionId'],alive='endedAt' not in state,
  activeTasks=state['activeTasks'],gpuSynthesisJobs=0,cpuProductionJobs=0 if 'endedAt' in state else 1,renderJobs=0,uploads=0,
  remainingTwoMotionFraming={'state':rel(DEST/'execution.json'),'completedCuts':state['completedCuts'],'totalCuts':len(cuts),'images':len(state['images'])})
 i['nextAction']='Directly inspect v5 corrected flight/Pepper-name alignment, single-line cues and source reframing. Preserve all15 PCM; final mix and every final cue approval remain pending.'
 q['updatedAt']=state['updatedAt'];write(qp,q)
 cp=read(BASE/'latest-checkpoint.json');cp.update(stage=i['stage'],updatedAt=state['updatedAt'],execution=i['execution'],nextAction=i['nextAction']);write(BASE/'latest-checkpoint.json',cp)
try:
 save()
 for c in cuts:
  m=next(x for x in compiled['cuts'] if x['id']==c['id']);assert sha(ROOT/m['video'])==m['sha256']
  frames={0:{'anchors':['start'],'cues':[]},c['frames']//2:{'anchors':['middle'],'cues':[]},c['frames']-1:{'anchors':['last'],'cues':[]}}
  for r in layout['rows']:
   if r['segment']==c['id']:frames.setdefault(r['localFrame'],{'anchors':[],'cues':[]})['cues'].append(r['cue'])
  for n in range(0,c['frames'],6):frames.setdefault(n,{'anchors':['motion-10fps'],'cues':[]})
  crop='crop=1440:810:480:0,'
  if c['id']=='02-p1-action-10-600-630':crop='crop=1280:720:0:360,'
  if c['id']=='02-p4-action-21-1410-1455':crop="crop=1440:810:480:0,"
  if c['id']=='06-p2-action-31-900-945':crop="crop=1120:630:0:'450*min(1,n/89)',"
  context=c.get('requiredContextLabel');label=''
  if context:label=f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='{context}':fontsize=26:fontcolor=black:box=1:boxcolor=white@0.94:boxborderw=12:x=38:y=36,"
  select='+'.join(f'eq(n\\,{f})' for f in sorted(frames))
  vf=f"{crop}scale=1920:1080,setsar=1,{label}setpts=PTS+{c['startFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.ass,select='{select}'"
  folder=DEST/c['id'];folder.mkdir();log=folder/'extraction.log'
  cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-v','error','-nostdin','-threads','2','-i',str(ROOT/m['video']),'-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(frames)),str(folder/'sample-%03d.png')]
  with log.open('wb') as fh:
   child=subprocess.Popen(cmd,cwd=WORK,stdout=fh,stderr=fh,creationflags=subprocess.CREATE_NO_WINDOW)
   state['activeTasks']=[{'kind':'CPU-framing-correction','pid':child.pid,'command':cmd,'log':rel(log)}];save();code=child.wait()
  state['activeTasks']=[];assert code==0 and not log.read_text().strip()
  files=sorted(folder.glob('sample-*.png'));assert len(files)==len(frames)
  for f,n in zip(files,sorted(frames)):
   state['images'].append({'path':rel(f),'sha256':sha(f),'cut':c['id'],'localFrame':n,'globalFrame':c['startFrame']+n,
    'anchorRoles':frames[n]['anchors'],'cueIds':frames[n]['cues'],'trialCrop':crop,'directlyRead':False,'finalApproved':False})
  state['completedCuts']+=1;save()
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23)
 for off in range(0,len(state['images']),6):
  subset=state['images'][off:off+6];im=Image.new('RGB',(1920,1740),'white');d=ImageDraw.Draw(im)
  for k,r in enumerate(subset):
   x,y=(k%2)*960,(k//2)*580
   with Image.open(ROOT/r['path']) as a:im.paste(a.resize((960,540)),(x,y+40))
   d.text((x+8,y+7),f'{off+k+1:03d} {r["cut"]} n{r["localFrame"]} cue{r["cueIds"]}',font=font,fill='black')
  out=DEST/f'review-sheet-{off//6+1:03d}.jpg';im.save(out,quality=94);state['sheets'].append({'path':rel(out),'sha256':sha(out),'imageIndices':list(range(off+1,off+len(subset)+1)),'directlyRead':False})
 state.update(status='closed-remaining-two-motion-framing-awaiting-direct-read',endedAt=now(),exitCode=0);save()
 print(json.dumps({'pid':os.getpid(),'cuts':len(cuts),'images':len(state['images']),'sheets':len(state['sheets']),'newGitImages':0}))
except Exception:
 state.update(status='closed-remaining-two-motion-framing-failed',endedAt=now(),exitCode=1,error=traceback.format_exc(),activeTasks=[]);save();raise
