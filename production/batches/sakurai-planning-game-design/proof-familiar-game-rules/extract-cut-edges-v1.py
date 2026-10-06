import json,pathlib,hashlib,subprocess,os,datetime,time,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[4]
BASE=pathlib.Path(__file__).resolve().parent
REL=BASE.relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 t=p.with_suffix(p.suffix+'.'+str(os.getpid())+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for attempt in range(20):
  try:t.replace(p);return
  except PermissionError:
   if attempt==19:raise
   time.sleep(.15)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bank=read(BASE/'source-action-bank-v1.json');resource=read(BASE/'resource-observation-v4.json')
assert bank['clipCount']==39 and not bank['allEdgesDirectlyRead']
assert resource['ownHeavyJobs']==0 and resource['cpuLoadPercent']<=85
assert (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(resource['observedAt'])).total_seconds()<240
out=ROOT/'shared/output/familiar-game-rules/research/cut-edges-v1'
resume='--resume' in sys.argv
if resume:
 assert out.exists() and (BASE/'cut-edges-execution-v1.json').exists()
 prior=read(BASE/'cut-edges-execution-v1.json');assert prior['status']=='cut-edge-extraction-failed'
 write(BASE/'cut-edges-execution-v1.initial-failure.json',prior)
 state=prior;state['history']=[{'pid':prior['pid'],'status':prior['status'],'error':prior.get('error'),'sessionId':45019}];state.update(pid=os.getpid(),resumedAt=now(),boards=[])
 state.pop('error',None)
else:
 assert not out.exists(),'Inspect existing edge outputs, never repeat.'
 out.mkdir();(out/'boards').mkdir()
 state={'schemaVersion':1,'slug':'familiar-game-rules','pid':os.getpid(),'startedAt':now(),'status':'initializing','cpuThreads':2,'gpuJobs':0,'children':[],'boards':[],'resourceObservation':'resource-observation-v4.json','finalPixelApproval':False}
def save(status):
 state['status']=status;state['updatedAt']=now();write(BASE/'cut-edges-execution-v1.json',state)
 q=read(ROOT/'production/batches/sakurai-planning-game-design/queue.json');item=next(x for x in q['items'] if x['slug']==state['slug']);assert not item.get('videoId')
 item['stage']=status;item['updatedAt']=state['updatedAt'];item['execution']={'phase':'candidate-native-cut-edge-extraction','status':status,'pid':state['pid'],'commandLine':[os.sys.executable,*os.sys.argv],'state':REL+'/cut-edges-execution-v1.json','activeTasks':[c for c in state['children'] if c['status']=='running'],'cpuThreads':2,'gpuJobs':0,'foreignWorkPreserved':True};item['nextAction']='Directly read all39 candidate edge boards; approve exact intervals/framing, then write independent full KO/EN/MC before TTS.';q['updatedAt']=state['updatedAt'];q['lastProgressAt']=state['updatedAt'];write(ROOT/'production/batches/sakurai-planning-game-design/queue.json',q)
 for p in [ROOT/'projects/familiar-game-rules/production/latest-checkpoint.json',BASE/'latest-checkpoint.json']:
  x=read(p);x.update(updatedAt=state['updatedAt'],stage=status,execution=item['execution'],nextAction=item['nextAction']);write(p,x)
ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
try:
 save('cut-edge-extraction-running')
 # Decode each source once for all requested boundaries; never rerun full decode QA.
 frame_paths={}
 for sid in dict.fromkeys(c['sourceVideoId'] for c in bank['clips']):
  clips=[c for c in bank['clips'] if c['sourceVideoId']==sid];source=ROOT/clips[0]['sourcePath'];assert sha(source)==clips[0]['sourceSha256']
  frames=sorted(set(n for c in clips for n in [max(0,c['inFrameInclusive']-1),c['inFrameInclusive'],c['inFrameInclusive']+1,c['outFrameExclusive']-2,c['outFrameExclusive']-1,c['outFrameExclusive']]))
  directory=out/sid
  if directory.exists():
   assert resume,'Do not overwrite existing source frames.'
   files=sorted(directory.glob('*.jpg'));assert len(files)==len(frames),f'Incomplete preserved source {sid}'
   for file in files:
    with Image.open(file) as im:im.verify()
   previous=next(c for c in state['children'] if c['sourceId']==sid)
   previous.update(status='finished-preserved',frameCount=len(files),preservedAt=now(),exitCodeObserved=previous.get('exitCode') is not None)
   frame_paths[sid]={n:p for n,p in zip(frames,files)};save('cut-edge-extraction-running');continue
  directory.mkdir();expr='+'.join('eq(n,'+str(n)+')' for n in frames)
  cmd=[ff,'-hide_banner','-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(source),'-an','-vf',"select='"+expr+"',scale=960:540",'-vsync','0','-q:v','3','-threads','2',str(directory/'%04d.jpg')]
  log=BASE/'logs'/f'{sid}-cut-edges.log'
  with log.open('xb') as f:
   p=subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW);child={'sourceId':sid,'pid':p.pid,'commandLine':cmd,'log':log.relative_to(ROOT).as_posix(),'startedAt':now(),'status':'running'};state['children'].append(child);save('cut-edge-extraction-running');code=p.wait();child.update(exitCode=code,endedAt=now(),status='finished' if code==0 else 'failed');assert code==0
  files=sorted(directory.glob('*.jpg'));assert len(files)==len(frames);frame_paths[sid]={n:p for n,p in zip(frames,files)}
 for c in bank['clips']:
  board=Image.new('RGB',(1920,1710),'white');d=ImageDraw.Draw(board);tiles=[];num,den=map(int,c['sourceFrameRate'].split('/'))
  for i,(tag,n) in enumerate(zip(['before-start','first','after-start','before-last','last','outside-end'],[max(0,c['inFrameInclusive']-1),c['inFrameInclusive'],c['inFrameInclusive']+1,c['outFrameExclusive']-2,c['outFrameExclusive']-1,c['outFrameExclusive']])):
   p=frame_paths[c['sourceVideoId']][n];im=Image.open(p);x=(i%2)*960;y=(i//2)*570;board.paste(im,(x,y+30));d.text((x+8,y+3),f'{c["id"]} {tag} n={n} t={n*den/num:.6f}',font=font,fill='black');tiles.append({'tag':tag,'sourceFrame':n,'seconds':n*den/num,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
  target=out/'boards'/f'{c["id"]}.jpg';board.save(target,quality=95);state['boards'].append({'actionId':c['id'],'board':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'tiles':tiles,'directlyRead':False})
 state['boardCount']=len(state['boards']);state['frameSlots']=sum(len(b['tiles']) for b in state['boards']);state['allDirectlyRead']=False;state['imagesGitPolicy']='local-only';save('cut-edges-extracted-awaiting-direct-review');print(json.dumps({'pid':state['pid'],'boards':state['boardCount'],'frameSlots':state['frameSlots'],'status':state['status']}))
except Exception as e:
 state['error']=repr(e);save('cut-edge-extraction-failed');raise
