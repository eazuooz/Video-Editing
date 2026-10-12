"""Resume only extraction after the completed v324 decode; review both additional encoded differences. Historical failure preserved."""
from pathlib import Path
import importlib.util, math
from PIL import Image, ImageDraw, ImageFont
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT; R=ROOT/'production/research/game-lighting-history'; P=ROOT/'projects/game-lighting-history-04/production'
BP=P/'part1-reviewed-pair-build-v323.json'; pair=m.read(BP)
assert m.read(P/'part1-reviewed-pair-execution-v323.json')['status']=='complete'
assert pair['identicalAacPayloadPtsDuration'] and all(pair[k]['wholeDecode']['exitCode']==0 and pair[k]['frames']==89148 for k in ['clean','captioned'])
video=ROOT/pair['captioned']['path']; assert m.sha(video)==pair['captioned']['sha256']
layout=m.read(P/'part1-caption-layout-v309.json'); visual=m.read(P/'part1-final-visual-build-v322.json')
assert layout['planSha256']==visual['planSha256']==pair['planSha256'] and layout['cueCount']==335
oldEx=P/'part1-final-pixel-review-execution-v294.json'; old=m.read(oldEx)
boards=m.read(P/'part1-final-board-direct-progress-v297.json')
assert len(boards['records'])==len(old['boards'])==378 and all(x['directlyRead'] for x in boards['records'])
assert boards['sourceSha256']==old['sourceSha256'] and boards['extractionSha256']==m.sha(oldEx)
oldHash=R/'local/part1-decoded-comparison-v314/old293.framemd5'
priorHash=R/'local/part1-decoded-comparison-v314/current313.framemd5'
assert m.sha(oldHash)=='4e6219a177417d8dcb12e36aa6af8c3ce65c5a2399844401ec0a23d7e9913b55'
assert m.sha(priorHash)=='908c27552937a93f62bd4d9b07ef2258002274e82d4187bbb01f6723bdf596bf'
OUT=R/'local/part1-current-pixel-qa-v327'; SP=P/'part1-current-pixel-qa-execution-v327.json'
assert not OUT.exists() and not SP.exists(), 'Preserve prior execution; explicit resume required'
resources=m.resources(); OUT.mkdir(); FD=OUT/'frames'; FD.mkdir()
state=dict(startedAt=m.stamp(),status='comparing-current-decoded-frames',worker=m.worker(),active=None,resourceObservation=resources,commands=[],images=[],boards=[],allFinalPixelsReviewed=False,qaApproved=False,newGitImages=0)
m.save(SP,state)
def checkpoint():
 cp=R/'checkpoint.json'; j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part1CurrentPixelQaV327']=dict(execution=m.rel(SP),status=state['status'],worker=state['worker'],active=state['active'],images=len(state['images']),boards=len(state['boards']),allFinalPixelsReviewed=False)
 j['ownedActiveWork']=dict(type='current-frame-comparison-and-pixel-extraction',execution=m.rel(SP),worker=state['worker'],cpuThreads=2,gpuJobs=0,next='Read all newly encoded changed frames and normal-speed cuts; preserve historical reviews') if state['status'] not in ['complete','failed'] else dict(status='no-active-owned-media-worker',execution=m.rel(SP),next='Directly review all changed current boards and moving cuts')
 m.save(cp,j)
def parse(path):
 rows=[x.split(',') for x in path.read_text().splitlines() if x and not x.startswith('#')]
 assert len(rows)==89148
 assert [int(x[2]) for x in rows]==list(range(89148)), 'Expected one normalized presentation frame per row'
 return [x[-1].strip() for x in rows]
def runs(ns):
 out=[]
 for n in ns:
  if out and out[-1][1]==n:out[-1][1]=n+1
  else:out.append([n,n+1])
 return out
checkpoint()
try:
 currentHash=R/'local/part1-current-pixel-qa-v324/current323.framemd5'
 priorExecution=m.read(P/'part1-current-pixel-qa-execution-v324.json')
 assert priorExecution['status']=='failed' and priorExecution['commands'][0]['exitCode']==0
 assert m.sha(currentHash)=='a8f17b308981c3f98d55cb7a2a442c62f387743d067e0beab0845cd1e2b7f7ea'
 state['reusedCompletedCurrentDecode']=dict(execution='projects/game-lighting-history-04/production/part1-current-pixel-qa-execution-v324.json',hashFile=m.rel(currentHash),sha256=m.sha(currentHash),secondDecodeStarted=False)
 m.save(SP,state)
 cur,prev,baseline=parse(currentHash),parse(priorHash),parse(oldHash)
 changed=set(i for i,(a,b) in enumerate(zip(cur,baseline)) if a!=b)
 changedPrior=[i for i,(a,b) in enumerate(zip(cur,prev)) if a!=b]
 ids=['texture-dependent-conversion:native','cyber-surface-observation:native','mobile-device-policy:native','mobile-lod-settings:native','fortnite-mobile-test:native','fortnite-normal-material:native']
 encodedOnlyIds=['mobile-console-policy:native','mobile-compiler-availability:native']
 priorVisual=m.read(P/'part1-final-visual-build-v316.json');priorCuts={c['id']:c for c in priorVisual['cuts']}
 encodedOnly=[c for c in visual['cuts'] if c['id'] in encodedOnlyIds]
 assert len(encodedOnly)==2
 for c in encodedOnly:
  before=priorCuts[c['id']];assert c['sha256']==before['sha256']==m.sha(ROOT/c['path']) and (c['fromFrame'],c['toFrame'])==(before['fromFrame'],before['toFrame'])
 changedCuts=[c for c in visual['cuts'] if c['id'] in ids+encodedOnlyIds];assert len(changedCuts)==8
 allowed=set(f for c in changedCuts for f in range(max(0,c['fromFrame']-300),min(89148,c['toFrame']+300)))
 assert changed<=allowed, 'Unexpected decoded change beyond the eight current-review inputs'
 comparison=dict(createdAt=m.stamp(),currentSourceSha256=pair['captioned']['sha256'],historicalSourceSha256=old['sourceSha256'],frames=89148,exactToReviewed293=89148-len(changed),changedToReviewed293=len(changed),changedRangesExclusive=runs(sorted(changed)),exactTo313=89148-len(changedPrior),changedTo313=len(changedPrior),changedPriorRangesExclusive=runs(changedPrior),hashFiles=[dict(path=m.rel(p),sha256=m.sha(p)) for p in [oldHash,priorHash,currentHash]],allChangesConfinedToEightReviewedInputsAndEncoderEdges=True,encodedOnlyInputsByteIdentical=[dict(id=c['id'],sha256=c['sha256'],fromFrame=c['fromFrame'],toFrame=c['toFrame']) for c in encodedOnly],historicalIssuesPreserved=True,directApproval=False)
 m.save(P/'part1-current-decoded-comparison-v327.json',comparison)
 points={}
 def add(f,reason):
  f=int(f)
  if 0<=f<89148:
   p=points.setdefault(f,dict(frame=f,reasons=[]))
   if reason not in p['reasons']:p['reasons'].append(reason)
 for p in old['images']:
  if p['frame'] in changed:
   for reason in p['reasons']:add(p['frame'],reason)
 for c in changedCuts:
  a,b=c['fromFrame'],c['toFrame']
  for f in range(a,b,30):add(f,'changed-native-motion-'+c['id'])
  for f in [a-1,a,a+1,b-1,b,b+1]:add(f,'changed-cut-edge-'+c['id'])
  for q in layout['metrics']:
   lo,hi=max(a,q['assFirstFrame']),min(b,q['assExclusiveEndFrame'])
   if hi>lo:
    for f in [lo-1,lo,(lo+hi-1)//2,hi-1,hi]:add(f,'current-cue/cut-'+c['id'])
 for a,b in comparison['changedRangesExclusive']:
  for f in [a-1,a,a+1,b-1,b]:add(f,'actual-encoder-difference-edge')
 # Exact native edit joins, normalized to 60 fps, including loaded editor transitions and mobile diagnostics.
 for f in [68973+1043,70346+44,77755+152,77755+302,77755+462,77755+637,77755+885,77755+1045,47974+98,47974+956]:
  for offset in [-1,0,1]:add(f+offset,'native-piece-join')
 cuts=[dict(id='original-branding',kind='branding',fromFrame=0,toFrame=120),*visual['cuts'],dict(id='original-membership',kind='membership',fromFrame=88548,toFrame=89148)]
 for p in points.values():
  qs=[q for q in layout['metrics'] if q['assFirstFrame']<=p['frame']<q['assExclusiveEndFrame']]
  c=next(c for c in cuts if c['fromFrame']<=p['frame']<c['toFrame'])
  p.update(visibleCueIds=[q['id'] for q in qs],expectedCaptions=[q['text'] for q in qs],input=c['id'],kind=c['kind'],localFrame=p['frame']-c['fromFrame'])
 reused=[dict(index=p['index'],frame=p['frame'],path=p['path'],sha256=p['sha256'],currentDecodedPixelIdentical=True,originalBoard=(p['index']-1)//6+1) for p in old['images'] if p['frame'] not in changed]
 request=dict(preparedAt=m.stamp(),sourceSha256=pair['captioned']['sha256'],pairBuildSha256=m.sha(BP),captionLayoutSha256=m.sha(P/'part1-caption-layout-v309.json'),comparisonSha256=m.sha(P/'part1-current-decoded-comparison-v327.json'),points=[points[f] for f in sorted(points)],exactReviewedPixelReuse=reused,all335OriginalCueChecksAccountedFor=True,allChangedOriginalQaPointsExtracted=True,changedInputs=ids,encodedOnlyInputs=encodedOnlyIds,allFinalPixelsReviewed=False,newGitImages=0)
 m.save(P/'part1-current-pixel-qa-request-v327.json',request)
 state.update(status='extracting-changed-current-pixels');m.save(SP,state);checkpoint()
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
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None,source=m.rel(video),sourceSha256=m.sha(video),pairBuildSha256=m.sha(BP),exactReviewedPointsReused=len(reused),comparisonPath='projects/game-lighting-history-04/production/part1-current-decoded-comparison-v327.json')
 m.save(SP,state);checkpoint();print(m.json.dumps(dict(images=len(files),boards=len(state['boards']),exactReviewedPointsReused=len(reused),newGitImages=0,approved=False)))
except BaseException as e:
 state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=repr(e));m.save(SP,state);checkpoint();raise
