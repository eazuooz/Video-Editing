import os,json,hashlib,subprocess,pathlib,datetime,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[3];os.chdir(ROOT)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
plan_path='projects/game-lighting-history-04/production/word-clock-proof-plan-v3.json';plan=read(plan_path)
session=read('production/research/game-lighting-history/local/episode04-word-clock-session-v3.json')
if session['status']!='complete' or session['actualIdentityLive'] or session['exitCode']!=0:raise RuntimeError('Actual closed render required')
for model in plan['models']:
 if sha(model['path'])!=model['sha256']:raise RuntimeError('Current rendered model changed')
media=session['actualOutput'];out=pathlib.Path('production/research/game-lighting-history/local/episode04-word-clock-proof-v3/encoded-qa-v3');resume='--resume-pixels-only' in sys.argv
if out.exists() and not resume:raise RuntimeError('Existing extracted proof preserved')
old=read(out/'execution.json') if resume else None
if resume and (old['status']!='failed-preserving-proof-and-logs' or old.get('wholeDecodeExit')!=0 or not old.get('allPts1500StepApproved') or old['media']['sha256']!=sha(media) or old['plan']['sha256']!=sha(plan_path) or list(out.glob('pixel-*.png'))):raise RuntimeError('Resume only current completed decode/PTS and zero pixel outputs')
guard=subprocess.run(['powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'game-lighting-history' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
if guard.returncode or guard.stdout.strip():raise RuntimeError('Another owned heavy worker live')
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True).strip()
out.mkdir(exist_ok=resume);bin=pathlib.Path('C:/ProgramData/HP/LCDDisplayHelper/bin');ff=str(bin/'ffmpeg.exe');probe=str(bin/'ffprobe.exe')
state={'startedAt':now(),'coordinatorPid':os.getpid(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'gpuObservation':gpu,'status':'prepared','current':None,'media':{'path':media,'sha256':sha(media)},'plan':{'path':plan_path,'sha256':sha(plan_path)},'exitCode':None,'localOnly':True,'newGitImages':0,'allFinalPixelsReviewed':False}
state_path=out/'execution.json'
if resume:
 (out/'initial-filter-failure.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');state['previousFailure']='initial-filter-failure.json';state['resumeScope']='Only selected pixel extraction; completed whole decode and exact PTS preserved';state['probe']=old['probe'];state['allPtsCount']=old['allPtsCount'];state['allPts1500StepApproved']=True;state['wholeDecodeExit']=0
def write():
 state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 cp_path=ROOT/'production/research/game-lighting-history/checkpoint.json';c=read(cp_path);c['updatedAt']=now();c['stage']='episode04-six-word-clock-encoded-QA-v3';c['episode04WordClockQa']=state;c['ownedJobsRunning']=[state] if state.get('exitCode') is None else [];c['ownedGpuJobs']=0
 tmp=pathlib.Path(str(cp_path)+'.writing');tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,cp_path)
def run(label,args):
 with (out/(label+'.log')).open('w',encoding='utf-8') as log:
  p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1','OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'2'})
  state['status']=label;state['current']={'pid':p.pid,'command':args,'startedAt':now(),'log':str(out/(label+'.log'))};write();code=p.wait();state['lastExit']={**state['current'],'exitCode':code,'endedAt':now()};state['current']=None;write()
  if code:raise RuntimeError(f'{label} exit {code}')
try:
 if not resume:
  info=json.loads(subprocess.check_output([probe,'-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_frames,duration,start_time:format=duration,size','-of','json',media],text=True));state['probe']=info
  v=next(s for s in info['streams'] if s['codec_type']=='video')
  if v['time_base']!='1/90000' or v['r_frame_rate']!='60/1' or int(v['nb_frames'])!=plan['totalFrames']:raise RuntimeError('Exact rendered stream failed')
  packet=json.loads(subprocess.check_output([probe,'-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',media],text=True))['packets'];pts=sorted(int(p['pts']) for p in packet)
  if pts!=[i*1500 for i in range(plan['totalFrames'])]:raise RuntimeError('Exact all-frame PTS failed')
  state['allPtsCount']=len(pts);state['allPts1500StepApproved']=True
  run('whole-proof-decode',[ff,'-v','error','-threads','2','-i',media,'-f','null','-']);state['wholeDecodeExit']=0
 targets={}
 def add(n,label):
  if 0<=n<plan['totalFrames']:targets.setdefault(n,[]).append(label)
 for i,s in enumerate(plan['scenes']):
  start=s['fromFrame'];add(start-1,f'S{i} expected before');add(start,f'S{i} expected start');add(start+1,f'S{i} +1');add(start+3,f'S{i} +3');add(start+5,f'S{i} +5');add(s['toFrame']-1,f'S{i} expected last')
  for j,c in enumerate(s['cues']):add(start+(c['fromFrame']+c['toFrame'])//2,f'S{i} cue{j} midpoint')
  for j,t in enumerate(s['stages']):add(start+t['fromFrame'],f'S{i} stage{j} start');add(start+t['toFrame']-1,f'S{i} stage{j} last')
 frames=sorted(targets);expr='+'.join(f'eq(n,{f})' for f in frames)
 run('selected-encoded-pixels-resume' if resume else 'selected-encoded-pixels',[ff,'-v','error','-threads','2','-i',media,'-vf',f"select='{expr}',scale=960:540",'-filter_threads','2','-vsync','0','-threads','2',str(out/'pixel-%04d.png')])
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);records=[];boards=[]
 for k,f in enumerate(frames):
  p=out/f'pixel-{k+1:04d}.png';records.append({'frame':f,'labels':targets[f],'path':str(p).replace('\\','/'),'sha256':sha(p),'directlyRead':False})
 for page in range((len(records)+3)//4):
  board=Image.new('RGB',(1920,1160),'#252525');d=ImageDraw.Draw(board)
  for j,r in enumerate(records[page*4:page*4+4]):
   x=(j%2)*960;y=(j//2)*580;d.text((x+8,y+6),str(r['frame'])+' '+', '.join(r['labels'])[:94],font=font,fill='white');board.paste(Image.open(r['path']),(x,y+40))
  p=out/f'board-{page+1:02d}.png';board.save(p);boards.append({'path':str(p).replace('\\','/'),'sha256':sha(p),'pixelIndices':list(range(page*4,min(page*4+4,len(records)))),'directlyRead':False})
 state.update({'status':'encoded-frames-extracted-awaiting-direct-review','pixels':records,'boards':boards,'exitCode':0,'endedAt':now(),'actualSceneStartsDirectlyVerified':False,'allEncodedProofPixelsDirectlyRead':False});write();print(json.dumps({'frames':plan['totalFrames'],'pts':state['allPtsCount'],'wholeDecodeExit':0,'pixels':len(records),'boards':len(boards),'approved':False}))
except Exception as e:
 state.update({'status':'failed-preserving-proof-and-logs','exitCode':1,'error':repr(e),'endedAt':now()});write();raise
