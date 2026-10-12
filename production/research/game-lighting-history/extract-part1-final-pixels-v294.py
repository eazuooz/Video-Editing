"""Plan complete cue/cut, spatial-motion and repaired-marker QA; extract only the final pair."""
from pathlib import Path
import argparse,importlib.util,math,psutil,os
from PIL import Image,ImageDraw,ImageFont
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT;P=ROOT/'projects/game-lighting-history-04/production'
ap=argparse.ArgumentParser();ap.add_argument('--plan-only',action='store_true');args=ap.parse_args()
PP=P/'part1-final-input-plan-v288.json';LP=P/'part1-caption-layout-v288.json';OP=P/'part1-input-overrides-v289.json'
plan,layout,overrides=m.read(PP),m.read(LP),m.read(OP)
assert overrides['inputPlan']['sha256']==m.sha(PP) and layout['planSha256']==m.sha(PP) and layout['cueCount']==335
points={}
def add(frame,reason):
 frame=int(frame)
 if not 0<=frame<plan['finalFrames']:return
 p=points.setdefault(frame,{'frame':frame,'reasons':[]})
 if reason not in p['reasons']:p['reasons'].append(reason)
cuts=[dict(id='original-branding',kind='branding',fromFrame=0,toFrame=120),*overrides['effectiveCuts'],
 dict(id='original-membership',kind='membership',fromFrame=plan['finalFrames']-600,toFrame=plan['finalFrames'])]
assert all(a['toFrame']==b['fromFrame'] for a,b in zip(cuts,cuts[1:])) and len(cuts)==96
for q in layout['metrics']:
 a,b=q['assFirstFrame'],q['assExclusiveEndFrame']-1
 for f in [a-1,a,(a+b)//2,b,b+1]:add(f,'cue-'+str(q['id']))
for c in cuts:
 a,b=c['fromFrame'],c['toFrame']-1
 for f in [a-1,a,a+1,(a+b)//2,b]:add(f,'cut-'+c['id'])
 for q in layout['metrics']:
  lo,hi=max(a,q['assFirstFrame']),min(b+1,q['assExclusiveEndFrame'])
  if hi>lo:add((lo+hi-1)//2,'cue/cut-'+c['id'])
 if c['kind']=='explanation':
  for fraction in [.2,.4,.6,.8]:add(a+round((b-a)*fraction),'spatial-motion-'+c['id'])
 change=overrides['changes'].get(c['id'])
 if change:
  for f in range(a,b+1,30):add(f,'corrected-native-motion-'+c['id'])
  offset=0
  for pc in c['proposedCuts']:
   for n in [-1,0,1]:add(a+offset+n,'native-piece-join-'+c['id'])
   offset+=pc['outFrame']-pc['inFrame']
  assert offset==c['frames']
  for box in change.get('tracking',{}).get('boxes',[]):
   for t in [box['from'],box['to']]:
    edge=math.ceil(t*60-1e-8)
    for n in [-1,0,1]:add(a+edge+n,'marker-enable-edge-'+c['id'])
for p in plan['paragraphs']:
 a=min(q['fromFrame'] for q in p['koCues'])
 for offset in [-1,0,1]:add(a+offset,'narration-onset-'+p['id'])
for f in [0,119,120,plan['finalFrames']-601,plan['finalFrames']-600,plan['finalFrames']-300,plan['finalFrames']-1]:add(f,'branding/membership-edge')
covered=set()
for p in points.values():
 p['visibleCueIds']=[q['id'] for q in layout['metrics'] if q['assFirstFrame']<=p['frame']<q['assExclusiveEndFrame']]
 p['expectedCaptions']=[q['text'] for q in layout['metrics'] if q['id'] in p['visibleCueIds']]
 c=next(c for c in cuts if c['fromFrame']<=p['frame']<c['toFrame'])
 p.update(input=c['id'],kind=c['kind'],localFrame=p['frame']-c['fromFrame'])
 p['expectedMarkerRegions']=[b for b in overrides['changes'].get(c['id'],{}).get('tracking',{}).get('boxes',[]) if b['from']<=p['localFrame']/60<b['to']]
 covered.update(p['visibleCueIds'])
assert covered==set(range(1,336))
request={'preparedAt':m.stamp(),'planSha256':m.sha(PP),'inputOverridesSha256':m.sha(OP),'captionLayoutSha256':m.sha(LP),
 'points':[points[f] for f in sorted(points)],'uniqueFrames':len(points),'cueCount':335,'paragraphs':77,'bodyInputCuts':94,'inputCuts':96,
 'allCueCutIntersectionsIncluded':True,'allCorrectedNativeMarkerEdgesIncluded':True,'allImagesLocalOnly':True,'newGitImages':0,'allFinalPixelsReviewed':False,'qaApproved':False}
RP=P/'part1-final-pixel-review-request-v294.json'
if RP.exists():
 old=m.read(RP);assert old['points']==request['points'] and old['planSha256']==request['planSha256'] and old['inputOverridesSha256']==request['inputOverridesSha256']
else:m.save(RP,request)
if args.plan_only:
 print(m.json.dumps({'framesPlanned':len(points),'allCues':335,'allBodyCuts':94,'imagesCreated':0,'approved':False}));raise SystemExit
BP=P/'part1-reviewed-pair-build-v293.json';pair=m.read(BP)
assert pair['planSha256']==m.sha(PP) and pair['captionAssSha256']==layout['ass']['sha256']
assert pair['inputOverrides']['sha256']==m.sha(OP) and pair['identicalAacPayloadPtsDuration'] and pair['captioned']['wholeDecode']['exitCode']==0
video=ROOT/pair['captioned']['path'];assert m.sha(video)==pair['captioned']['sha256']
for proc in psutil.process_iter(['pid','name','cmdline','create_time']):
 d=proc.info;cmd=' '.join(d['cmdline'] or [])
 if d['pid']!=os.getpid() and (d['name'] or '').lower().startswith('python') and any(t in cmd for t in ['review-part1-final-mix-v243.py','review-part1-artifact-contexts-v255.py','repair-part1-observed-native-pixels-v250.py','build-part1-reviewed-pair-v252.py']):
  raise RuntimeError('Preserve the actual single owned media worker; no overlapping extraction.')
resources=m.resources();OUT=ROOT/'production/research/game-lighting-history/local/part1-final-pixel-qa-v294';SP=P/'part1-final-pixel-review-execution-v294.json'
assert not OUT.exists() and not SP.exists(),'Preserve prior execution/images; explicit resume required'
OUT.mkdir(parents=True);FD=OUT/'frames';FD.mkdir()
state={'startedAt':m.stamp(),'status':'extracting','worker':m.worker(),'active':None,'resourceObservation':resources,'commands':[],'results':[],'images':[],'boards':[],
 'newGitImages':0,'allFinalPixelsReviewed':False,'qaApproved':False}
m.save(SP,state)
def checkpoint():
 cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=m.read(cp);j['updatedAt']=m.stamp()
 j['episode04Part1FinalPixelExtractionV294']={'execution':m.rel(SP),'status':state['status'],'worker':state['worker'],'active':state['active'],'images':len(state['images']),'boards':len(state['boards']),'allFinalPixelsReviewed':False}
 j['ownedActiveWork']={'type':'part1-final-caption-cue-cut-extraction','execution':m.rel(SP),'worker':state['worker'],'cpuThreads':2,'gpuJobs':0,'next':'Directly read every encoded board and normal-speed final motion; then QA/collection/private settings'} if state['status']=='extracting' else {'status':'no-active-owned-media-worker','execution':m.rel(SP),'next':'Directly read all encoded boards and final motion'}
 m.save(cp,j)
checkpoint()
try:
 filt=OUT/'exact-frames.filter';filt.write_text('select='+'+'.join(f'eq(pts\\,{f*1500})' for f in sorted(points))+'\n','utf8')
 extraction=m.run([m.FF,'-n','-v','error','-threads','2','-filter_threads','2','-reinit_filter','0','-i',video,'-filter_script:v',filt,'-fps_mode','vfr','-an','-threads','2',FD/'frame-%05d.png'],'final-frame-extraction',state,SP,OUT)
 files=sorted(FD.glob('frame-*.png'));assert len(files)==len(points)
 for i,(file,p) in enumerate(zip(files,request['points'])):
  with Image.open(file) as im:assert im.size==(1920,1080)
  state['images'].append({'index':i+1,'path':m.rel(file),'sha256':m.sha(file),**p})
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
 for i in range(0,len(files),6):
  group=state['images'][i:i+6];board=Image.new('RGB',(2880,1204),(25,25,25));draw=ImageDraw.Draw(board)
  for j,p in enumerate(group):
   x,y=j%3*960,j//3*602
   with Image.open(ROOT/p['path']) as im:board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+62))
   draw.text((x+10,y+6),f"#{p['index']} f{p['frame']} {p['input']} cue {p['visibleCueIds']}",font=font,fill='white')
   draw.text((x+10,y+32),','.join(p['reasons'])[:67],font=font,fill='#e5c873')
  file=OUT/f'board-{i//6+1:03d}.png';board.save(file)
  state['boards'].append({'board':i//6+1,'path':m.rel(file),'sha256':m.sha(file),'imageIndices':[p['index'] for p in group],'directlyRead':False})
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None,extraction=extraction,source=m.rel(video),sourceSha256=m.sha(video),pairBuildSha256=m.sha(BP),requestSha256=m.sha(RP))
 m.save(SP,state);checkpoint();print(m.json.dumps({'images':len(files),'boards':len(state['boards']),'newGitImages':0,'approved':False}))
except BaseException as e:
 state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=repr(e));m.save(SP,state);checkpoint();raise
