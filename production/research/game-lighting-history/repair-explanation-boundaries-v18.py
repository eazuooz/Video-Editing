"""Hold the prior correct explanation frame for one boundary frame, without retiming."""
import importlib.util,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).with_name('review-media-common-v15.py');s=importlib.util.spec_from_file_location('review_media',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
base=m.PROD/'review-input-plan-v15.json';assert m.sha(base)=='0681e970c71de503a7de24b8172fee209b0c2df2bd70a233859942cdecd14579'
ids=['original-02','original-10','original-18','original-24','original-25','original-32','original-72','original-78']
old=m.read(base);cuts=[dict(c)for c in old['inputs']if c['id']in ids];assert len(cuts)==8
for c in cuts:
 assert c['kind']=='explanation-review-input'
 proof=m.read(m.ROOT/c['verification']);assert proof['outputSha256']==m.sha(m.ROOT/c['output']) and proof['wholeDecode']['exitCode']==0
 c['source']=c['output'];c['sourceSha256']=proof['outputSha256'];c['output']='production/research/game-lighting-history/local/explanation-boundary-repair-v18/'+c['id']+'.mp4'
 c['changedLocalFrame']=c['frames']-1;c['replacementSourceLocalFrame']=c['frames']-2
out=m.ROOT/'production/research/game-lighting-history/local/explanation-boundary-repair-v18';assert not out.exists(),'Preserve existing boundary repair'
resource=m.resources();out.mkdir();(out/'frames').mkdir()
pp=m.PROD/'explanation-boundary-repair-plan-v18.json';m.save(pp,dict(preparedAt=m.stamp(),baseline=dict(path=m.rel(base),sha256=m.sha(base)),cuts=cuts,method='Replace only the last early-next-scene frame with the immediately preceding correct explanation frame. All other frames, PCM, cuts, captions and chapter times stay unchanged.',changedFrames=8,addedFrames=0,allFinalPixelsReviewed=False))
sp=m.PROD/'explanation-boundary-repair-execution-v18.json';state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),active=None,resourceObservation=resource,results=[],images=[],boards=[],cpuThreads=2,gpuJobs=0,allFinalPixelsReviewed=False);m.save(sp,state)
cp=m.ROOT/'production/research/game-lighting-history/checkpoint.json'
def update(active):
 x=m.read(cp);x['episode03ExplanationBoundaryRepair']=dict(plan=m.rel(pp),execution=m.rel(sp),status=state['status'],worker=state['worker'],completed=len(state['results']),total=8,allFinalPixelsReviewed=False)
 x['ownedActiveWork']=dict(type='CPU-explanation-boundary-repair-v18',execution=m.rel(sp),worker=state['worker'],cpuThreads=2,gpuJobs=0)if active else None;x['updatedAt']=m.stamp();m.save(cp,x)
update(True)
layout=m.read(m.PROD/'local/captions-v15/caption-layout-measurement.json');ass=m.ROOT/layout['ass']['path'];assert m.sha(ass)==layout['ass']['sha256'];assf=ass.as_posix().replace(':',r'\:')
try:
 for c in cuts:
  output=m.ROOT/c['output'];n=c['frames']
  vf=f'trim=end_frame={n-1},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.016666667,settb=1/90000,setpts=N*1500'
  encode=m.run([m.FF,'-n','-v','error','-threads','2','-filter_threads','2','-i',m.ROOT/c['source'],'-an','-vf',vf,'-frames:v',str(n),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',output],c['id']+'-encode',state,sp,out)
  proof=m.verify_video(output,n,state,sp,out,c['id']);proof.update(encode=encode,cut=c);rp=output.with_suffix('.verification.json');m.save(rp,proof)
  state['results'].append(dict(id=c['id'],verification=m.rel(rp),sha256=proof['outputSha256'],frames=n));m.save(sp,state);update(True)
  indices=[n-3,n-2,n-1];select='+'.join(f'eq(n\\,{f})'for f in indices)
  vf=f"settb=1/90000,setpts=(N+{c['fromFrame']})*1500,ass='{assf}',setpts=N*1500,select={select}"
  m.run([m.FF,'-n','-v','error','-threads','2','-filter_threads','2','-i',output,'-an','-vf',vf,'-fps_mode','vfr','-threads','2',out/'frames'/f"{c['id']}-%02d.png"],c['id']+'-caption-qa',state,sp,out)
  files=sorted((out/'frames').glob(c['id']+'-*.png'));assert len(files)==3
  for file,f in zip(files,indices):state['images'].append(dict(path=m.rel(file),sha256=m.sha(file),input=c['id'],originalFrame=c['fromFrame']+f,localFrame=f,sourceOutputSha256=proof['outputSha256']))
  print(m.json.dumps(dict(done=len(state['results']),total=8,id=c['id'],decode=0,changedFrame=n-1)),flush=True)
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 for start in range(0,len(state['images']),6):
  group=state['images'][start:start+6];board=Image.new('RGB',(2880,1204),(25,25,25));draw=ImageDraw.Draw(board)
  for i,q in enumerate(group):
   x=i%3*960;y=i//3*602
   with Image.open(m.ROOT/q['path'])as im:assert im.size==(1920,1080);board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+62))
   draw.text((x+10,y+10),f"{q['input']} / original frame {q['originalFrame']}",font=font,fill='white');draw.text((x+10,y+34),'last three frames / unchanged fixed captions',font=font,fill='#e5c873')
  b=out/f'board-{start//6+1:03d}.png';board.save(b);state['boards'].append(dict(path=m.rel(b),sha256=m.sha(b),imageIndices=list(range(start+1,start+len(group)+1)),directlyRead=False))
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),originalCaptionAssSha256=layout['ass']['sha256']);m.save(sp,state);update(False)
except BaseException as e:
 state.update(status='failed',exitCode=1,error=str(e),failedAt=m.stamp());m.save(sp,state);update(False);raise
