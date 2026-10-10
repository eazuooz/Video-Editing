"""Single CPU worker: compare current seven action chapters before editing them."""
exec((__import__('pathlib').Path(__file__).with_name('prepare-polar-source-review-v1.py')).read_text(encoding='utf-8').split('OUT.mkdir')[0])
import psutil
timeline=json.loads((BASE/'production/timeline.json').read_text(encoding='utf-8-sig'))
folder=LOCAL/'all-action-v3';folder.mkdir(parents=True,exist_ok=True)
state={'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'createTime':psutil.Process().create_time(),'commandLine':psutil.Process().cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','jobs':[],'next':'directly compare every new board; native-review specific clear actions, then editable tracked annotations'}
statefile=OUT/'action-clarity-execution-v3.json'
def save():statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not statefile.exists();save();print(json.dumps({'pid':state['pid'],'createTime':state['createTime'],'state':rel(statefile)}),flush=True)
try:
 for s in timeline['scenes']:
  if s['classification']!='actual':continue
  source=ROOT/f"shared/output/game-math-polar-3d/clips/{s['id']}.mp4"
  if s['id']=='02':continue # 38 directly reviewed samples already cover this chapter.
  points=set(range(0,s['frames'],240));points.add(s['frames']-1)
  if s.get('cuts') and len(s['cuts'])>1:
   boundary=s['cuts'][0]['frames'];points.update([boundary-1,boundary,boundary+1])
  frames=sorted(points);dir=folder/s['id'];dir.mkdir(exist_ok=True)
  cmd=[str(FF),'-hide_banner','-nostdin','-loglevel','error','-threads','2','-filter_threads','1','-i',str(source),'-vf','select='+ '+'.join(f'eq(n\\,{f})' for f in frames),'-frames:v',str(len(frames)),'-fps_mode','passthrough',str(dir/'sample-%03d.png')]
  job={'scene':s['id'],'command':cmd,'sourceSha256':sha(source),'sampleFrames':frames,'status':'running'};state['jobs'].append(job);save()
  result=subprocess.run(cmd,check=True);files=sorted(dir.glob('sample-*.png'));assert len(files)==len(frames)
  records=[{'frame':f,'seconds':f/60,'path':rel(p),'sha256':sha(p)} for f,p in zip(frames,files)]
  boards=[]
  for n in range(0,len(records),6):
   board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
   for j,r in enumerate(records[n:n+6]):
    x=(j%3)*640;y=(j//3)*390
    with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
    d.text((x+8,y+7),f"scene{s['id']} f{r['frame']} / {r['seconds']:.3f}s",fill='white')
   p=dir/f'board-{n//6+1:02d}.png';board.save(p);boards.append({'path':rel(p),'sha256':sha(p)})
  job.update(status='completed',exitCode=result.returncode,records=records,boards=boards);save();print(json.dumps({'scene':s['id'],'samples':len(records),'boards':len(boards)}),flush=True)
 state.update(status='completed',exitCode=0,finishedAt=datetime.now(timezone.utc).isoformat());save()
except Exception as e:
 state.update(status='failed',exception=str(e),exitCode=1);save();raise
