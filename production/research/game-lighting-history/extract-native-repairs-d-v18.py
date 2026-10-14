"""Exact changed native pixels with the existing final caption events, local only."""
import importlib.util
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).with_name('review-media-common-v15.py');s=importlib.util.spec_from_file_location('review_media',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
cuts=[];input_hashes=[]
for suffix in ['d']:
 pp=m.PROD/f'native-repair-{suffix}-plan-v18.json';sp=m.PROD/f'native-repair-{suffix}-execution-v18.json';plan=m.read(pp);execution=m.read(sp)
 assert execution['status']=='complete'and execution['exitCode']==0
 input_hashes+=[dict(path=m.rel(pp),sha256=m.sha(pp)),dict(path=m.rel(sp),sha256=m.sha(sp))]
 for c in plan['cuts']:
  proof=m.read((m.ROOT/c['output']).with_suffix('.verification.json'))
  assert proof['wholeDecode']['exitCode']==0 and m.sha(m.ROOT/c['output'])==proof['outputSha256'];cuts.append(c)
request=m.read(m.PROD/'encoded-pixel-review-request-v15.json');layout=m.read(m.PROD/'local/captions-v15/caption-layout-measurement.json')
ass=m.ROOT/layout['ass']['path'];assert m.sha(ass)==layout['ass']['sha256'];assf=ass.as_posix().replace(':',r'\:')
out=m.ROOT/'production/research/game-lighting-history/local/native-repair-d-pixel-qa-v18';assert not out.exists(),'Preserve existing QA';resource=m.resources();out.mkdir();(out/'frames').mkdir()
sp=m.PROD/'native-repair-d-pixel-execution-v18.json';state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resourceObservation=resource,inputHashes=input_hashes,originalCaptionAssSha256=layout['ass']['sha256'],results=[],images=[],boards=[],cpuThreads=2,gpuJobs=0,newGitImages=0,allFinalPixelsReviewed=False);m.save(sp,state)
cp=m.ROOT/'production/research/game-lighting-history/checkpoint.json'
def update(active):
 x=m.read(cp);x['episode03NativeRepairDPixelExecution']=dict(path=m.rel(sp),status=state['status'],worker=state['worker'],completed=len(state['results']),total=len(cuts),allFinalPixelsReviewed=False);x['ownedActiveWork']=dict(type='CPU-native-repair-d-pixel-v18',execution=m.rel(sp),worker=state['worker'],cpuThreads=2,gpuJobs=0)if active else None;x['updatedAt']=m.stamp();m.save(cp,x)
update(True)
try:
 for c in cuts:
  points={q['frame']:dict(q)for q in request['points']if c['fromFrame']<=q['frame']<c['toFrame']}
  for f in [c['fromFrame'],c['fromFrame']+1,(c['fromFrame']+c['toFrame'])//2,c['toFrame']-2,c['toFrame']-1]:
   if f not in points:points[f]=dict(frame=f,reasons=['changed-input-boundary-or-motion'],visibleCueIds=[])
  points=[dict(points[f],input=c['id'],localFrame=f-c['fromFrame'])for f in sorted(points)]
  select='+'.join(f'eq(n\\,{q["localFrame"]})'for q in points)
  vf=f"settb=1/90000,setpts=(N+{c['fromFrame']})*1500,ass='{assf}',setpts=N*1500,select={select}"
  m.run([m.FF,'-n','-v','error','-threads','2','-filter_threads','2','-i',m.ROOT/c['output'],'-an','-vf',vf,'-fps_mode','vfr','-threads','2',out/'frames'/f"{c['id']}-%03d.png"],c['id']+'-qa',state,sp,out)
  files=sorted((out/'frames').glob(c['id']+'-*.png'));assert len(files)==len(points)
  for file,q in zip(files,points):state['images'].append(dict(q,index=len(state['images'])+1,path=m.rel(file),sha256=m.sha(file)))
  state['results'].append(dict(id=c['id'],images=len(files),sourceSha256=m.sha(m.ROOT/c['output'])));m.save(sp,state);update(True)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 for start in range(0,len(state['images']),6):
  group=state['images'][start:start+6];board=Image.new('RGB',(2880,1204),(25,25,25));draw=ImageDraw.Draw(board)
  for i,q in enumerate(group):
   x=i%3*960;y=i//3*602
   with Image.open(m.ROOT/q['path'])as im:assert im.size==(1920,1080);board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+62))
   draw.text((x+10,y+6),f"#{q['index']} / f{q['frame']} / {q['input']}",font=font,fill='white');draw.text((x+10,y+32),'original fixed captions / '+','.join(map(str,q['visibleCueIds'])),font=font,fill='#e5c873')
  b=out/f'board-{start//6+1:03d}.png';board.save(b);state['boards'].append(dict(path=m.rel(b),sha256=m.sha(b),imageIndices=[q['index']for q in group],directlyRead=False))
 state.update(status='complete',exitCode=0,completedAt=m.stamp());m.save(sp,state);update(False);print(m.json.dumps(dict(images=len(state['images']),boards=len(state['boards']),finalApproval=False)),flush=True)
except BaseException as e:
 state.update(status='failed',exitCode=1,error=str(e),failedAt=m.stamp());m.save(sp,state);update(False);raise
