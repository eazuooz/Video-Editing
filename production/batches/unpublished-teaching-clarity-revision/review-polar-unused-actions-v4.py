"""Compare unused native actions; absolute PTS, single CPU2, no baseline mutations."""
exec((__import__('pathlib').Path(__file__).with_name('prepare-polar-source-review-v1.py')).read_text(encoding='utf-8').split('OUT.mkdir')[0])
import psutil,re
source=ROOT/'shared/output/game-math-polar-lecture/sources/WJVRoLR6KvY.mp4'
folder=LOCAL/'unused-native-v4';folder.mkdir(parents=True,exist_ok=True)
windows=[(318,334),(375,400),(583,613)]
frames=sorted({s*60 for a,b in windows for s in range(a,b)})
statefile=OUT/'unused-native-execution-v4.json';assert not statefile.exists()
state={'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'createTime':psutil.Process().create_time(),'commandLine':psutil.Process().cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','sourceSha256':sha(source),'nativeTimebase':'1/15360','nativeStep':256,'windows':windows,'plannedNativeFrames':frames,'selectionApproved':False,'finalPixelsApproved':False}
def save():statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save();print(json.dumps({'pid':state['pid'],'createTime':state['createTime'],'state':rel(statefile)}),flush=True)
try:
 cmd=[str(FF),'-hide_banner','-nostdin','-loglevel','info','-threads','2','-filter_threads','1','-copyts','-i',str(source),'-vf','select='+ '+'.join(f'eq(pts\\,{f*256})' for f in frames)+',showinfo','-frames:v',str(len(frames)),'-fps_mode','passthrough',str(folder/'native-%03d.png')]
 log=folder/'ffmpeg-showinfo.log';state['command']=cmd;save()
 with log.open('w',encoding='utf-8') as stream:result=subprocess.run(cmd,stdout=stream,stderr=stream,check=True)
 observed=[int(m) for m in re.findall(r' n:\s*\d+\s+pts:\s*(\d+)\s+pts_time:',log.read_text(encoding='utf-8'))]
 assert observed==[f*256 for f in frames],observed
 files=sorted(folder.glob('native-*.png'));assert len(files)==len(frames)
 records=[{'nativeFrame':f,'nativePts':p,'seconds':f/60,'path':rel(image),'sha256':sha(image)} for f,p,image in zip(frames,observed,files)]
 boards=[]
 for n in range(0,len(records),6):
  board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
  for j,r in enumerate(records[n:n+6]):
   x=j%3*640;y=j//3*390
   with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
   d.text((x+8,y+7),f"native f{r['nativeFrame']} pts{r['nativePts']} / {r['seconds']:.3f}s",fill='white')
  p=folder/f'board-{n//6+1:02d}.png';board.save(p);boards.append({'path':rel(p),'sha256':sha(p)})
 snapshot=json.loads((OUT/'baseline-protected-sha-v1.json').read_text(encoding='utf-8-sig'))
 assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
 state.update(status='completed',exitCode=result.returncode,finishedAt=datetime.now(timezone.utc).isoformat(),records=records,boards=boards,absoluteNativePtsMatched=True,protectedBaselineUnchanged=True,sourcePlaybackContinuousApproval=False)
 save();print(json.dumps({'samples':len(records),'boards':len(boards),'absoluteNativePtsMatched':True,'exitCode':result.returncode}),flush=True)
except Exception as e:
 state.update(status='failed',exception=str(e),exitCode=1);save();raise
