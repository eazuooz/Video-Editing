"""One CPU-only source composition check. These are stress masks, not final cue pixels."""
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib,subprocess,time
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
bank=read(PROOF/'source-action-bank-v4.json');assert len(bank['clips'])==60 and bank['allEdgesDirectlyRead']
resource=read(PROOF/'resource-observation-v17.json');assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
out=ROOT/'shared/output/familiar-game-rules/research/framing-stress-v1';assert not out.exists(),'Preserve existing extraction'
out.mkdir();(out/'boards').mkdir();ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
state=dict(schemaVersion=1,slug='familiar-game-rules',pid=os.getpid(),commandLine=[os.sys.executable,*os.sys.argv],startedAt=now(),cpuThreads=2,gpuJobs=0,children=[],boards=[],clips=[],bankSha256=sha(PROOF/'source-action-bank-v4.json'),resourceObservation=rel(PROOF/'resource-observation-v17.json'),allDirectlyRead=False,framingApproved=False,finalCuePixelApproval=False,imagesGitPolicy='local-only',stressMask={'style':'boxed-white-forest-v1','center':[960,970],'fontPx':48,'maximumTextWidth':1570,'padding':[22,11],'maximumLines':2,'boxSize':[1614,146],'shadowOffset':[14,14],'purpose':'worst-case caption envelope over native full-frame source; not a final cue'})
def save(status):
 state.update(status=status,updatedAt=now());write(PROOF/'source-framing-execution-v1.json',state)
 qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(i for i in q['items'] if i['slug']=='familiar-game-rules')
 item.update(stage=status,updatedAt=state['updatedAt'],sourceFramingExecution={'pid':state['pid'],'commandLine':state['commandLine'],'sessionId':None,'alive':status=='source-framing-stress-running','state':rel(PROOF/'source-framing-execution-v1.json'),'log':rel(BASE/'source-framing-v1.log'),'cpuThreads':2,'gpuJobs':0,'activeTasks':[c for c in state['children'] if c['status']=='running'],'foreignWorkPreserved':True},nextAction='Read every source composition board; keep final cue/render/ratio/private gates false. Then write independent additive KOEN guides preserving original11PCM and147.2s white explanation.')
 q.update(updatedAt=state['updatedAt'],lastProgressAt=state['updatedAt']);write(qp,q)
 for p in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
  d=read(p)
  for k in ['stage','updatedAt','sourceFramingExecution','nextAction']:d[k]=item[k]
  write(p,d)
def samples(c):return [c['inFrameInclusive'],(c['inFrameInclusive']+c['outFrameExclusive']-1)//2,c['outFrameExclusive']-1]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
try:
 save('source-framing-stress-running');paths={}
 for sid in dict.fromkeys(c['sourceVideoId'] for c in bank['clips']):
  clips=[c for c in bank['clips'] if c['sourceVideoId']==sid];source=ROOT/clips[0]['sourcePath'];assert sha(source)==clips[0]['sourceSha256']
  frames=sorted(set(n for c in clips for n in samples(c)));directory=out/sid;directory.mkdir()
  expr='+'.join(f'eq(n,{n})' for n in frames)
  cmd=[ff,'-hide_banner','-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(source),'-an','-vf',f"select='{expr}',scale=1920:1080",'-vsync','0','-q:v','3','-threads','2',str(directory/'%04d.jpg')]
  log=PROOF/'logs'/f'{sid}-framing-stress-v1.log'
  with log.open('xb') as h:
   p=subprocess.Popen(cmd,cwd=ROOT,stdout=h,stderr=h,creationflags=subprocess.CREATE_NO_WINDOW);child=dict(sourceVideoId=sid,pid=p.pid,commandLine=cmd,log=rel(log),startedAt=now(),status='running');state['children'].append(child);save('source-framing-stress-running')
   code=p.wait();child.update(status='finished' if code==0 else 'failed',exitCode=code,endedAt=now());assert code==0
  files=sorted(directory.glob('*.jpg'));assert len(files)==len(frames);paths[sid]=dict(zip(frames,files))
 rendered=[]
 for c in bank['clips']:
  tiles=[];num,den=map(int,c['sourceFrameRate'].split('/'))
  for tag,n in zip(['first','middle','last'],samples(c)):
   p=paths[c['sourceVideoId']][n];im=Image.open(p).convert('RGB');draw=ImageDraw.Draw(im)
   draw.rectangle((167,911,1781,1057),fill='#073c32');draw.rectangle((153,897,1767,1043),fill='white',outline='#161b18',width=3)
   for text,y in [('몸의 이동과 총의 방향을 따로 따라가 보세요.',908),('이동하며 목표를 바꾸는 기능을 확인합니다.',970)]:
    draw.text((960,y),text,font=font,fill='#080b09',anchor='mt')
   target=out/f'{c["id"]}-{tag}.jpg';im.save(target,quality=95)
   tiles.append({'tag':tag,'sourceFrame':n,'seconds':n*den/num,'nativePath':rel(p),'nativeSha256':sha(p),'path':rel(target),'sha256':sha(target)})
  state['clips'].append({'id':c['id'],'sourceVideoId':c['sourceVideoId'],'sourceCrop':[0,0,1920,1080],'scaleOnly':True,'samples':tiles,'directlyRead':False,'fullScreenFramingApproved':False});rendered.extend((c['id'],t) for t in tiles)
 for start in range(0,len(rendered),6):
  board=Image.new('RGB',(1920,1710),'white');draw=ImageDraw.Draw(board);tiles=[]
  for i,(cid,t) in enumerate(rendered[start:start+6]):
   x=i%2*960;y=i//2*570;draw.text((x+8,y+3),f'{cid} {t["tag"]} n={t["sourceFrame"]} t={t["seconds"]:.4f} caption STRESS',font=label,fill='black')
   with Image.open(ROOT/t['path']) as im:board.paste(im.resize((960,540)),(x,y+30))
   tiles.append({'id':cid,**t})
  target=out/'boards'/f'{start//6+1:02d}.jpg';board.save(target,quality=95);state['boards'].append({'path':rel(target),'sha256':sha(target),'tiles':tiles,'directlyRead':False})
 state.update(finishedAt=now(),boardCount=len(state['boards']),sampleCount=len(rendered));save('source-framing-stress-extracted-awaiting-direct-review')
 print(json.dumps({'pid':state['pid'],'boards':state['boardCount'],'samples':state['sampleCount'],'allApproval':False}))
except Exception as e:
 state['error']=repr(e);save('source-framing-stress-failed');raise
