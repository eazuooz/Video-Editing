"""One current decode comparison and only changed road/cue pixels; preserve earlier reviews."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw,ImageFont
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;R=ROOT/'production/research/game-lighting-history';P=ROOT/'projects/game-lighting-history-04/production'
BP=P/'part1-reviewed-pair-build-v333.json';pair=m.read(BP)
assert m.read(P/'part1-reviewed-pair-execution-v333.json')['status']=='complete'
assert pair['identicalAacPayloadPtsDuration'] and all(pair[k]['wholeDecode']['exitCode']==0 and pair[k]['frames']==89148 for k in ['clean','captioned'])
video=ROOT/pair['captioned']['path'];assert m.sha(video)==pair['captioned']['sha256']
layout=m.read(P/'part1-caption-layout-v309.json');visual=m.read(P/'part1-final-visual-build-v332.json')
assert layout['planSha256']==visual['planSha256']==pair['planSha256'] and layout['cueCount']==335
priorHash=R/'local/part1-current-pixel-qa-v324/current323.framemd5'
assert m.sha(priorHash)=='a8f17b308981c3f98d55cb7a2a442c62f387743d067e0beab0845cd1e2b7f7ea'
priorEx=P/'part1-current-pixel-qa-execution-v327.json';prior=m.read(priorEx)
priorBoardsPath=P/'part1-current-board-direct-progress-v325.json';priorBoards=m.read(priorBoardsPath)
assert prior['status']=='complete' and priorBoards['allNewCurrentBoardsDirectlyRead'] and len(priorBoards['records'])==96
assert priorBoards['extractionSha256']==m.sha(priorEx) and priorBoards['sourceSha256']==prior['sourceSha256']
oldEx=P/'part1-final-pixel-review-execution-v294.json';old=m.read(oldEx)
oldBoardsPath=P/'part1-final-board-direct-progress-v297.json';oldBoards=m.read(oldBoardsPath)
assert len(oldBoards['records'])==378 and all(x['directlyRead'] for x in oldBoards['records'])
assert oldBoards['extractionSha256']==m.sha(oldEx)
oldHash=R/'local/part1-decoded-comparison-v314/old293.framemd5'
assert m.sha(oldHash)=='4e6219a177417d8dcb12e36aa6af8c3ce65c5a2399844401ec0a23d7e9913b55'
OUT=R/'local/part1-road-final-pixel-qa-v335';SP=P/'part1-road-final-pixel-qa-execution-v335.json'
assert not OUT.exists() and not SP.exists()
resources=m.resources();OUT.mkdir();FD=OUT/'frames';FD.mkdir()
state=dict(startedAt=m.stamp(),status='comparing-current-decoded-frames',worker=m.worker(),active=None,resourceObservation=resources,commands=[],images=[],boards=[],allFinalPixelsReviewed=False,qaApproved=False,newGitImages=0)
m.save(SP,state)
def checkpoint():
 cp=R/'checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part1RoadFinalPixelsV335']=dict(execution=m.rel(SP),status=state['status'],worker=state['worker'],active=state['active'],images=len(state['images']),boards=len(state['boards']),allFinalPixelsReviewed=False)
 j['ownedActiveWork']=dict(type='road-final-decoded-comparison-and-pixel-extraction',execution=m.rel(SP),worker=state['worker'],cpuThreads=2,gpuJobs=0,next='Direct road cues/motion and retained exact pixels; resolve historical issues before final QA') if state['status'] not in ['complete','failed'] else dict(status='no-active-owned-media-worker',execution=m.rel(SP),next='Directly read every new road board and moving final interval')
 m.save(cp,j)
def parse(p):
 rows=[x.split(',') for x in p.read_text().splitlines() if x and not x.startswith('#')]
 assert len(rows)==89148 and [int(x[2]) for x in rows]==list(range(89148))
 return [x[-1].strip() for x in rows]
def runs(ns):
 result=[]
 for n in sorted(ns):
  if result and result[-1][1]==n:result[-1][1]=n+1
  else:result.append([n,n+1])
 return result
checkpoint()
try:
 currentHash=OUT/'current333.framemd5'
 m.run([m.FF,'-n','-v','error','-nostdin','-threads','2','-i',video,'-map','0:v:0','-an','-fps_mode','passthrough','-c:v','rawvideo','-threads','2','-f','framemd5',currentHash],'current-decoded-frames',state,SP,OUT)
 cur,prev,baseline=parse(currentHash),parse(priorHash),parse(oldHash)
 changed={i for i,(a,b) in enumerate(zip(cur,prev)) if a!=b}
 road=next(c for c in visual['cuts'] if c['id']=='geometry-road-mask:native');a,b=road['fromFrame'],road['toFrame']
 assert road['frames']==1037 and changed and changed<=set(range(a-300,b+300)), 'Inspect unexpected distant encoder changes before pixel reuse'
 comparison=dict(createdAt=m.stamp(),currentSourceSha256=pair['captioned']['sha256'],priorSourceSha256=prior['sourceSha256'],frames=89148,exactToReviewed323=89148-len(changed),changedTo323=len(changed),changedRangesExclusive=runs(changed),allChangesConfinedToRoadAndEncoderEdges=True,hashFiles=[dict(path=m.rel(p),sha256=m.sha(p)) for p in [oldHash,priorHash,currentHash]],historicalIssuesPreserved=True,directApproval=False)
 m.save(P/'part1-road-current-decoded-comparison-v335.json',comparison)
 points={}
 def add(f,reason):
  if not 0<=f<89148:return
  p=points.setdefault(f,dict(frame=f,reasons=[]))
  if reason not in p['reasons']:p['reasons'].append(reason)
 for f in range(a,b,15):add(f,'road-current-motion')
 for f in [a-1,a,a+1,b-1,b,b+1]:add(f,'road-cut-edge')
 for q in layout['metrics']:
  lo,hi=max(a,q['assFirstFrame']),min(b,q['assExclusiveEndFrame'])
  if hi>lo:
   for f in [lo-1,lo,(lo+hi-1)//2,hi-1,hi]:add(f,'road-current-cue')
 for start,end in comparison['changedRangesExclusive']:
  for f in [start-1,start,start+1,end-1,end]:add(f,'encoder-difference-edge')
 for ex in [old,prior]:
  for p in ex['images']:
   if p['frame'] in changed:
    for reason in p['reasons']:add(p['frame'],reason)
 for f in [82994,82995,82996,82997,82998,83010,83055]:add(f,'retained-rivalry-source-fade-review')
 cuts=[dict(id='original-branding',kind='branding',fromFrame=0,toFrame=120),*visual['cuts'],dict(id='original-membership',kind='membership',fromFrame=88548,toFrame=89148)]
 for p in points.values():
  qs=[q for q in layout['metrics'] if q['assFirstFrame']<=p['frame']<q['assExclusiveEndFrame']]
  c=next(c for c in cuts if c['fromFrame']<=p['frame']<c['toFrame'])
  p.update(visibleCueIds=[q['id'] for q in qs],expectedCaptions=[q['text'] for q in qs],input=c['id'],kind=c['kind'],localFrame=p['frame']-c['fromFrame'])
 reuse=[]
 for label,ex in [('293',old),('323',prior)]:
  originalHashes=baseline if label=='293' else prev
  for p in ex['images']:
   if cur[p['frame']]==originalHashes[p['frame']]:reuse.append(dict(reviewVersion=label,index=p['index'],frame=p['frame'],path=p['path'],sha256=p['sha256'],currentDecodedPixelIdentical=True))
 request=dict(preparedAt=m.stamp(),sourceSha256=pair['captioned']['sha256'],pairBuildSha256=m.sha(BP),captionLayoutSha256=m.sha(P/'part1-caption-layout-v309.json'),comparisonSha256=m.sha(P/'part1-road-current-decoded-comparison-v335.json'),points=[points[f] for f in sorted(points)],exactReviewedPixelReuse=reuse,priorBoardReview=dict(path=m.rel(priorBoardsPath),sha256=m.sha(priorBoardsPath)),oldBoardReview=dict(path=m.rel(oldBoardsPath),sha256=m.sha(oldBoardsPath)),allChangedOriginalAndCurrentQaPointsExtracted=True,allFinalPixelsReviewed=False,newGitImages=0)
 m.save(P/'part1-road-final-pixel-qa-request-v335.json',request)
 state.update(status='extracting-current-road-pixels');m.save(SP,state);checkpoint()
 filt=OUT/'exact-current-frames.filter';filt.write_text('select='+'+'.join(f'eq(pts\\,{f*1500})' for f in sorted(points))+'\n','utf8')
 m.run([m.FF,'-n','-v','error','-threads','2','-filter_threads','2','-reinit_filter','0','-i',video,'-filter_script:v',filt,'-fps_mode','vfr','-an','-threads','2',FD/'frame-%05d.png'],'changed-frame-extraction',state,SP,OUT)
 files=sorted(FD.glob('frame-*.png'));assert len(files)==len(points)
 for i,(file,p) in enumerate(zip(files,request['points'])):
  with Image.open(file) as im:assert im.size==(1920,1080)
  state['images'].append(dict(index=i+1,path=m.rel(file),sha256=m.sha(file),**p))
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 for i in range(0,len(files),6):
  group=state['images'][i:i+6];board=Image.new('RGB',(2880,1204),(25,25,25));draw=ImageDraw.Draw(board)
  for j,p in enumerate(group):
   x,y=j%3*960,j//3*602
   with Image.open(ROOT/p['path']) as im:board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+62))
   draw.text((x+10,y+6),f"#{p['index']} f{p['frame']} {p['input']} cue {p['visibleCueIds']}",font=font,fill='white')
   draw.text((x+10,y+32),','.join(p['reasons'])[:68],font=font,fill='#e5c873')
  dest=OUT/f'board-{i//6+1:03d}.png';board.save(dest)
  state['boards'].append(dict(board=i//6+1,path=m.rel(dest),sha256=m.sha(dest),imageIndices=[p['index'] for p in group],directlyRead=False))
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None,source=m.rel(video),sourceSha256=pair['captioned']['sha256'],pairBuildSha256=m.sha(BP),exactReviewedPointsReused=len(reuse))
 m.save(SP,state);checkpoint();print(m.json.dumps(dict(images=len(files),boards=len(state['boards']),exactReviewedPointsReused=len(reuse),newGitImages=0,approved=False)))
except BaseException as e:
 state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=repr(e));m.save(SP,state);checkpoint();raise
