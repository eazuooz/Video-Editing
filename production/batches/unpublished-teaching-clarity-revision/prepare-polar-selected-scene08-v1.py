"""Remove distracting unlock UI using disjoint, normal-speed native action."""
exec((__import__('pathlib').Path(__file__).with_name('review-polar-unused-actions-v4.py')).read_text(encoding='utf-8').split('source=ROOT/')[0])
source=ROOT/'shared/output/game-math-polar-lecture/sources/WJVRoLR6KvY.mp4'
folder=LOCAL/'selected-scene08-v1';folder.mkdir(parents=True,exist_ok=True)
cuts=[{'sourceInFrame':20040,'frames':1560,'reason':'334–360s original approach/jump/turns retained. Stop before unrelated team unlock.'},
      {'sourceInFrame':22500,'frames':510,'reason':'375–383.5s fresh normal riding/turns/approach, before later failed landing.'},
      {'sourceInFrame':23340,'frames':353,'reason':'389–394.883333s fresh steering/follow view, after recovery is already complete.'},
      {'sourceInFrame':1800,'frames':1320,'reason':'30–52s original following camera action retained.'}]
assert sum(c['frames'] for c in cuts)==3743
statefile=OUT/'selected-scene08-execution-v1.json';assert not statefile.exists()
state={'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'createTime':psutil.Process().create_time(),'commandLine':psutil.Process().cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','sourceSha256':sha(source),'cuts':cuts,'narrationChanged':False,'baselineMutations':0,'footageSelectionFinalApproved':False,'annotationFinalApproved':False,
       'selectionBasis':'Existing94 original gameplay samples and71 unused native samples directly compared. Reject original scene26–40.383333s because team-unlock notification interrupts the mathematical focus. Reject raw323–333 menu/idle and raw385–388 crash/recovery.'}
def save():statefile.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save();print(json.dumps({'pid':state['pid'],'createTime':state['createTime'],'state':rel(statefile)}),flush=True)
try:
 pieces=[];offset=0
 for j,c in enumerate(cuts):
  c['sceneStartFrame']=offset;offset+=c['frames'];a=c['sourceInFrame']*256;b=(c['sourceInFrame']+c['frames'])*256
  p=folder/f'source-{j+1}.mp4';assert not p.exists();log=folder/f'source-{j+1}.log'
  vf=f"trim=start_pts={a}:end_pts={b},showinfo,setpts=PTS-STARTPTS,setsar=1,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='Descenders - MezzyGameplay | CC BY | edited excerpt, muted':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=808,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='youtu.be/WJVRoLR6KvY | creativecommons.org/licenses/by/4.0':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.65:x=30:y=834"
  cmd=[str(FF),'-hide_banner','-nostdin','-loglevel','info','-threads','2','-filter_threads','1','-copyts','-ss',str(max(0,c['sourceInFrame']/60-2)),'-i',str(source),'-vf',vf,'-frames:v',str(c['frames']),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',str(p)]
  c['command']=cmd;save()
  with log.open('w',encoding='utf-8') as f:result=subprocess.run(cmd,stdout=f,stderr=f,check=True)
  pts=[int(m) for m in re.findall(r' n:\s*\d+\s+pts:\s*(\d+)\s+pts_time:',log.read_text(encoding='utf-8'))]
  assert pts==list(range(a,b,256)),(j,len(pts),c['frames'],pts[:2],pts[-2:])
  c.update(exitCode=result.returncode,nativeFirstPts=pts[0],nativeLastPts=pts[-1],allNativePtsVerified=True,path=rel(p),sha256=sha(p));pieces.append(p);save()
 listing=folder/'concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in pieces)+'\n',encoding='utf-8')
 clip=folder/'scene08.source-selected.mp4'
 cmd=[str(FF),'-hide_banner','-nostdin','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-c:v','copy','-an','-video_track_timescale','90000','-movflags','+faststart',str(clip)];result=subprocess.run(cmd,check=True)
 points=sorted(set(range(0,3743,60))|{0,1559,1560,2069,2070,2422,2423,3742})
 cmd=[str(FF),'-hide_banner','-nostdin','-loglevel','error','-threads','2','-filter_threads','1','-i',str(clip),'-vf','select='+ '+'.join(f'eq(pts\\,{f*1500})' for f in points),'-frames:v',str(len(points)),'-fps_mode','passthrough',str(folder/'sample-%03d.png')];result=subprocess.run(cmd,check=True)
 files=sorted(folder.glob('sample-*.png'));assert len(files)==len(points)
 records=[{'frame':f,'pts':f*1500,'path':rel(p),'sha256':sha(p)} for f,p in zip(points,files)];boards=[]
 for n in range(0,len(records),6):
  board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
  for j,r in enumerate(records[n:n+6]):
   x=j%3*640;y=j//3*390
   with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
   d.text((x+8,y+7),f"scene08 f{r['frame']} / {r['frame']/60:.3f}s",fill='white')
  p=folder/f'board-{n//6+1:02d}.png';board.save(p);boards.append({'path':rel(p),'sha256':sha(p)})
 snapshot=json.loads((OUT/'baseline-protected-sha-v1.json').read_text(encoding='utf-8-sig'));assert all(sha(ROOT/r['path'])==r['sha256'] for r in snapshot['files'])
 state.update(status='completed',exitCode=0,finishedAt=datetime.now(timezone.utc).isoformat(),sourceCandidate=rel(clip),sourceCandidateSha256=sha(clip),samples=records,boards=boards,protectedBaselineUnchanged=True,selectionContinuousPixelApproval=False,sourceAudio=False,loop=False,slowdown=False)
 save();print(json.dumps({'frames':3743,'samples':len(records),'boards':len(boards),'allNativePtsVerified':True,'exitCode':0}),flush=True)
except Exception as e:
 state.update(status='failed',exception=str(e),exitCode=1);save();raise
