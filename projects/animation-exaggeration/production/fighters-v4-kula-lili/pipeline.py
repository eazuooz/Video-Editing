"""Run the same hash-bound A02 audio/caption and encoding routines in a separate scope.

No writes to a previous revision. The original audio/scene sources remain immutable.
"""
import sys, types, json, hashlib, copy, os, shutil, datetime
from pathlib import Path
H=Path(__file__).resolve().parent
R=H.parents[3]; P=H.parents[1]; V=H.name; OLD=H.parent/'fighters-v3'
L=P/'production/local'/V; O=P/'production/local/fighters-v3'; S=P/'script'/V
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def rel(p):return Path(p).relative_to(R).as_posix()
def artifact(p):return {'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size}
def module(name,extra=None):
 if name in sys.modules and getattr(sys.modules[name],'__package__','')=='a02v4':return sys.modules[name]
 f=OLD/(name+'.py');src=f.read_text(encoding='utf-8').replace('fighters-v3',V)
 if extra: src=extra(src)
 m=types.ModuleType(name);m.__file__=__file__;m.__package__='a02v4';sys.modules[name]=m
 exec(compile(src,str(f),'exec'),m.__dict__);return m
def libs():
 for s in ('storage_paths','audio_pipeline','caption_pipeline','video_pipeline'):module(s)
 vp=sys.modules['video_pipeline']
 if not getattr(vp,'v4LayoutApplied',False):
  original=vp.explanation_kind_label
  def classify(c,p):
   text,geo=original(c,p)
   if c.get('unrealCapture'):
    # The new right header holds the actual units and joint-mark legend.
    text=text.replace('1740,73','750,68').replace('해설용 시연','언리얼 · 해설 시연')
    geo['fixedLabel'].update(text='언리얼 · 해설 시연',center=[750,68],protectedRect=[545,30,950,106])
   return text,geo
  vp.explanation_kind_label=classify;vp.v4LayoutApplied=True
 return sys.modules['audio_pipeline'],vp
def setup():
 (L/'edit').mkdir(parents=True,exist_ok=True);(L/'voice').mkdir(parents=True,exist_ok=True)
 auth=read(OLD/'authorization.json');auth.update(revision=V,scope='Replace all old fighter examples by Kula Diamond and Lili; rebuild six native Unreal demonstrations with a clearly readable 1:1.8 authored joint amplitude comparison. Retain all 14 unchanged lesson paragraphs.')
 auth['userEvidence'].append('병렬로 A02 영상 캐릭터 킹오파 쿨라랑 철권 리리로 수정해서 다시 만들어줘~')
 auth['rendererSelection'].update(currentAmplitudeRevision='Existing 1.0× versus comparison 1.8×: same human mesh/scale, 500 cm orthographic camera and duration. Independent Unreal wrist displacement from prepared to peak pose: 30 cm and 54 cm. Identical target applies only to the final convergence phase.',stageManifest=rel(H/'unreal-stage/editable-stages.json'),measurements=rel(H/'unreal-stage/motion-measurements.json'))
 auth['userDirectedAdditionalRequirement']='Show substantially larger movement in the two Unreal comparison performances, baseline amplitude 1.0× and comparison 1.8×.'
 auth['preservation'].update(previousRevision='fighters-v3',captionedMasterSha256='e4b925266ff80eb046246a108b031da0b17e0fe0d54d1cb0b85db4e994bca7e0')
 auth['playbackException']['scope']=f'A02 {V} only';save(H/'authorization.json',auth)
 g=read(OLD/'execution-grant.json');g['revision']=V;save(H/'execution-grant.json',g)
 q=(OLD/'qwen-manifest.json').read_text(encoding='utf-8').replace('fighters-v3',V);(H/'qwen-manifest.json').write_text(q,encoding='utf-8')
 save(H/'checkpoint.json',{'episode':'A02','revision':V,'status':'source-review-in-progress','baseline':auth['preservation'],'unrealRevision':'Six new Game Animation Sample clips: original amplitude 1.0× versus 1.8×. Never reuse previous captures for these six cuts.','voice':'Existing14 unchanged + three replacement local Qwen own-voice passages only, after verifying the actual movies.','platformMutation':False,'humanFinalReview':False})
def copy_verified(src,dest):
 if dest.exists():assert sha(src)==sha(dest);return
 try: os.link(src,dest)
 except OSError: shutil.copyfile(src,dest)
def runmain():
 stage=sys.argv[1]
 if stage=='setup':return setup()
 ap,vp=libs()
 if stage in ('prepare_qwen_audio','recognize_additions','normalize_mix','review_encoded_audio','review_frames','register_script'):
  if stage=='review_frames':sys.argv=['review_frames.py',sys.argv[2]]
  if stage=='register_script':
   def adapt(s):
    s=s.replace("j['fightersSourceMap']=(H.relative_to(R)/'source-review.json').as_posix()", "j['fightersSourceMap']=(H.relative_to(R)/'sources/reviewed-footage.json').as_posix();j['openingFootageStatus']='inspected-FHD-independent-gameplay';j['productionBoundary']='Local A02 review only; research reference footage excluded. The original paragraph order and fourteen recordings are preserved.'")
    k=s.index(" save(H/'lesson-retention-plan.json'");z=s.index(" print(",k)
    return s[:k]+" save(H/'lesson-retention-plan.json',{'referenceRetained':'projects/animation-exaggeration/script/grid-v1/narration.ko.json','originalParagraphs':mapping,'observedAdditions':load(H/'analysis-beats.json'),'newUnrealComparisons':6,'unchangedBodyPcm':True})\n"+s[z:]
  else:adapt=None
  return module(stage,adapt).main()
 if stage=='assemble':
  import build_cut_plan
  return module('build_revision',lambda s:s.replace("aliases={'킹오브파이터즈15'", "aliases={'더킹오브파이터즈피프틴':'더킹오브파이터즈십오','철권8':'철권에이트','철권팔':'철권에이트','킹오브파이터즈15'")).main()
 if stage=='aac':return module('prepare_pair_audio')
 if stage=='retime':
  import build_cut_plan
  prev=read(H/'edit-plan.json');ins=read(H/'narration-insert-map.json')['inserts'];b=read(H.parent/'grid-v1/edit-plan.json');cues=read(L/'edit/captions.json')['cues']
  build_cut_plan.build(b,ins,prev['totalFrames'],prev['bodyFrames'],cues)
  new=read(H/'edit-plan.json');new['mixFile']=prev['mixFile'];assert new['totalFrames']==prev['totalFrames']
  save(H/'edit-plan.json',new);return
 if stage=='native_pre':
  import build_cut_plan
  ap.require_authorized('video-cuts');b=read(H.parent/'grid-v1/edit-plan.json')
  pre=build_cut_plan.build(b,[],b['totalFrames'],b['bodyFrames'],[],True)
  ids=[c['id'] for c in pre['cuts'] if c['kind']=='independent-gameplay' and c['id']!='A02-E023'];return vp.render_cuts(pre,L/'edit',ids)
 plan=read(H/'edit-plan.json');edit=L/'edit'
 if stage=='bind_unreal':
  for c in plan['cuts']:
   if not c.get('unrealCapture'):continue
   receipt=L/'unreal'/(c['id']+'-capture.json');j=read(receipt)
   assert j['status']=='complete' and j['frames']==c['frames'] and j['revision']==V and j['movie']==c['renderedSource'] and j['movieSha256']==sha(R/j['movie'])
   c.update(renderedSourceSha256=j['movieSha256'],unrealCapture=artifact(receipt))
  plan['unrealMotionComparison']={'nativeStages':artifact(H/'unreal-stage/editable-stages.json'),'measurements':artifact(H/'unreal-stage/motion-measurements.json'),'leftWristTravelCm':30,'rightWristTravelCm':54,'amplitudeRatio':1.8,'sameMeshScaleCameraDuration':True,'orthoWidthCm':500,'sharedEndTarget':'Final convergence phase only.'}
  vp.validate_plan(plan);save(H/'edit-plan.json',plan);return
 if stage in ('cuts','ue_cuts'):
  ap.require_authorized('video-cuts')
  old={c['id']:c for c in read(OLD/'edit-plan.json')['cuts']};render=[]
  for cut in plan['cuts']:
   if cut.get('unrealCapture') and stage=='cuts':continue
   if not cut.get('unrealCapture') and stage=='ue_cuts':continue
   cid=cut['id'];base=old.get(cid,{})
   localreceipt=edit/(cid+'-render.json');localmovie=edit/(cid+'.mp4')
   if localreceipt.exists() and localmovie.exists():
    r=read(localreceipt);prec=r['signature']['cut']
    def key(c):
     row=copy.deepcopy(c);row.pop('startFrame');row.pop('endFrame')
     if row.get('sourceAttribution'):row['sourceAttribution'].pop('license',None)
     return row
    if key(prec)==key(cut) and r['outputSha256']==sha(localmovie):
     r['signature']['cut']=cut;r['preflightReuse']='Identical source bytes, media interval, labels, marks and encoding. Only global origin and descriptive recording license metadata may differ.';save(localreceipt,r);continue
   if not base or {k:v for k,v in cut.items() if k not in ('startFrame','endFrame')}!={k:v for k,v in base.items() if k not in ('startFrame','endFrame')}:
    render.append(cid);continue
   source=O/'edit'/(cid+'.mp4');record=read(O/'edit'/(cid+'-render.json'))
   assert record['outputSha256']==sha(source) and record['signature']['cut']==base
   copy_verified(source,edit/(cid+'.mp4'));record['signature']['cut']=cut
   record['reusedFrom']={'source':artifact(source),'onlyGlobalPlacementChanged':True};save(edit/(cid+'-render.json'),record)
  for name in ['branding','membership']:copy_verified(O/'edit'/(name+'.mp4'),edit/(name+'.mp4'))
  if render:return vp.render_cuts(plan,edit,render)
  return
 if stage=='pair':ap.require_authorized('video-pair');return vp.render_pair(plan,edit)
 if stage=='verify':ap.require_authorized('video-verify');return vp.verify(plan,edit)
 raise ValueError(stage)
if __name__=='__main__':runmain()
