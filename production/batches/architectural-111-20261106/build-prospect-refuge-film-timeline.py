"""06.02 CPU timeline preparation. Default is read-only; no media/model processes.

Actual96 sentence PCM/ASR clocks, accepted mix and both real MC outputs are
required. Source windows never acquire invented seconds or character ratios.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,sys
from fractions import Fraction
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PROJECT=ROOT/'projects/shorts-leveldesign-06-02'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')/PROJECT.name
FPS=60;TOPIC='06.02'
CAPTION_SHA='e5cfcc3994a2d52bced9ee66b9ff6213355acbaef45286d31aa3e1461d7ef609'
AUDIO_SHA='69a8fba6881c4161b7fa4a3ece4d4fad875f037d4e72ec3333e3b0adbbdef3b5'
MC_RUNNER_SHA='c526b58eeffeddecfa71582615f93d368efb523dd2339713cd0425f89e14c3bf'
MC_CUE_SHA='0c535c08a5d1af11cd28cac890bc49ec125ed0ae36db29e0ea271e2d14c8f2c1'
MC_NODE_SHA='59d03e71eeeb566d9f32a1599a9c97d57175395708f03659b8dfad9ee703fb47'
class Pending(RuntimeError):pass
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p,role=None):
 r=dict(path=str(Path(p).resolve()),sha256=sha(p))
 if role:r['role']=role
 return r
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def bound(r):
 if not isinstance(r,dict)or not r.get('path')or sha(r['path'])!=r.get('sha256'):raise Pending('Changed/missing actual input '+str(r))
 return Path(r['path']).resolve()

def validate_sentence_clock(selection,timing):
 if timing.get('topicId')!=TOPIC:raise Pending('Actual06.02 caption timing required')
 rows=timing.get('sentences',[]);expected=[(p['paragraph'],r['sentenceIndexZeroBased'],r['canonicalKo'])for p in selection['paragraphs']for r in p['sentences']]
 if len(rows)!=96 or [(r['paragraph'],r['sentenceIndexZeroBased'],r['canonicalKo'])for r in rows]!=expected:raise Pending('Exact ordered25paragraph/96canonical sentence clocks required')
 if type(timing.get('totalFrames'))is not int or timing['totalFrames']<1:raise Pending('Actual final PCM frame clock required')
 cursor=0;sample=0
 for r in rows:
  if any(type(r.get(k))is not int for k in('startFrame','endFrameExclusive','startSample','endSample')):raise Pending('Sentence timing must retain integer sample and frame bounds')
  if r['startFrame']!=cursor or r['endFrameExclusive']<=cursor or r['startSample']!=sample or r['endSample']<=sample:raise Pending('Sentence sample/frame clock gap/reorder')
  cursor=r['endFrameExclusive'];sample=r['endSample']
 if cursor!=timing['totalFrames']:raise Pending('Last actual video-ceil frame must belong to final sentence')
 return rows

def view_descriptors(visual,registry):
 """Resolve an authored logical view to real camera/mode paths; no IO."""
 key=visual['sourceRef'];source=registry[key];camera=visual['camera'];result=[]
 if key in('main','close'):
  parts=camera.split('-');modes=['baseline','shifted']if parts[0]=='AB'else[parts[0]];cams=['player','observer']if parts[-1]=='dual'else[parts[-1]]
  for mode in modes:
   for cam in cams:result.append(dict(sourceRef=key,sourceKind=source['sourceKind'],mode=mode,camera=cam,modeFolder=str(Path(source['output'])/mode),cropXYXY=None))
 elif source['sourceKind']=='independent-gameplay':return[dict(sourceRef=key,sourceKind=source['sourceKind'],camera='native',sourcePath=source['media']['path'],sourceSHA256=source['media']['sha256'],sourceId=source['id'],cropXYXY=None)]
 else:
  folder=source.get('modeFolder')
  if not folder:raise Pending('Actual native output not bound: '+key)
  cams=['player','observer']if camera=='dual'else[camera]
  for cam in cams:
   crop=None
   framing=visual.get('cameraFraming',{}).get(cam,{})
   if cam=='observer'and framing.get('sourceCropXYXY')is not None:crop=list(framing['sourceCropXYXY'])
   result.append(dict(sourceRef=key,sourceKind=source['sourceKind'],mode=source.get('mode',key.removeprefix('c-')),camera=cam,modeFolder=folder,cropXYXY=crop))
 return result

def term_for(paragraph,sentence):
 terms={(3,3):('Prospect–Refuge','조망–은신처','몸을 두는 자리와 밖을 보는 공간의 관계'),(9,1):('Pilotis','필로티','기둥으로 위를 받쳐 아래를 여는 구성'),(10,0):('Ribbon Window','띠창','가로로 길게 이어진 창'),(10,1):('Free Plan','자유평면','구조벽에 덜 매인 내부 배치'),(11,0):('Ramp','경사로','높이가 다른 바닥을 잇는 비탈길')}
 item=terms.get((paragraph,sentence));return dict(english=item[0],korean=item[1],meaning=item[2])if item else None

def compile_guide_cues(annotations,timing,caption_helper):
 """Reveal at an actual blind-ASR word boundary, never a text/time ratio."""
 clocks={(r['paragraph'],r['sentenceIndexZeroBased']):r for r in timing['sentences']};out=[]
 for i,row in enumerate(annotations.get('cueTriggers',[])):
  key=(row['paragraph'],row['sentenceIndexZeroBased'])
  if key not in clocks:raise Pending('Guide refers to an unknown actual sentence')
  sentence=clocks[key]
  try:
   boundary=caption_helper.resolve_literal_start(sentence,row['revealPhraseKo'])
   end=sentence['endFrameExclusive']if row.get('clearAt')=='sentence-end'else caption_helper.resolve_literal_interval(sentence,row['endPhraseKo'])['endFrameExclusive']
  except (AssertionError,ValueError,RuntimeError,KeyError)as error:raise Pending('Guide has no supported exact spoken-word boundary: '+str(error))from error
  start=boundary['frame']
  if type(start)is not int or type(end)is not int or not sentence['startFrame']<=start<end<=sentence['endFrameExclusive']:raise Pending('Guide cue escapes its actual sentence clock')
  if row.get('kind')not in('anchor-label','native-ray','span-leader','height-leader','section-label'):raise Pending('Unsupported editorial guide kind')
  if not row.get('sourceRef')or not isinstance(row.get('anchorIds'),list)or not row['anchorIds']:raise Pending('Guide must name actual source and attached anchors')
  out.append(dict(copy.deepcopy(row),id=row.get('id',f'guide-{i+1:03}'),startFrame=start,endFrameExclusive=end,wordBoundaryProof=boundary))
 return out

def verify_annotations(annotations,selection,timing,caption_helper):
 if annotations.get('schemaVersion')!='06-02-source-annotation-plan-v1'or annotations.get('topicId')!=TOPIC or annotations.get('selectionSHA256')!=sha(PROJECT/'native-teaching-selection-v2.json'):raise Pending('Exact source-coordinate native/game annotation plan required')
 if annotations.get('nativeVisibilityFile'):
  draft=read(bound(annotations['nativeVisibilityFile']))
  if draft.get('topicId')!=TOPIC or draft.get('selection')!=pin(PROJECT/'native-teaching-selection-v2.json'):raise Pending('Native visibility proof belongs to another selected scene version')
  for q in draft['inputs'].values():bound(q)
  for row in draft['directlyViewedSourceImages']:bound(row['sourceImage'])
  active=[r for r in draft['nativeGuidePolicies']if r['method']=='recorded-camera-ray'or r.get('visibleFrames')];pending=[r for r in draft['nativeGuidePolicies']if r not in active]
  if annotations.get('nativeExtraVisibilityFile'):
   extra=read(bound(annotations['nativeExtraVisibilityFile']))
   if extra.get('topicId')!=TOPIC or extra.get('selection')!=pin(PROJECT/'native-teaching-selection-v2.json'):raise Pending('Supplemental source-pixel review is stale')
   for q in extra['inputs']:bound(q)
   for q in extra['actuallyViewedSourceImages']:bound(q)
   active+=[dict(r,actualSourceReview=r.get('actualSourceReview',annotations['nativeExtraVisibilityFile']))for r in extra['extraNativeGuidePolicies']]
  if annotations.get('nativeGuidePolicies')!=active or annotations.get('pendingNativeGuidePolicies')!=pending:raise Pending('Native visibility policies must preserve reviewed versus pending source scope')
 for row in annotations.get('nativeGuidePolicies',[]):
  if row.get('method')not in('reviewed-frame-set','recorded-camera-ray'):raise Pending('Unknown native occlusion proof policy')
  if row.get('method')=='reviewed-frame-set':
   if not row.get('visibleFrames')or not row.get('actualSourceReview'):raise Pending('Sampled visibility requires actual source/frame review proof')
   bound(row['actualSourceReview'])
  if row.get('method')=='recorded-camera-ray'and row.get('targetSurfaceColliders')and not row.get('actualSourceReview'):raise Pending('Self-target ray exception requires an actual review pin')
  if row.get('actualSourceReview'):bound(row['actualSourceReview'])
  if row.get('anchorTrace'):bound(row['anchorTrace'])
  for image in row.get('reviewedSourceImages',[]):bound(image.get('sourceImage',image))
 for row in annotations.get('gameKeyframes',[]):
  source=selection['sourceRegistry'].get(row.get('sourceRef'),{})
  if source.get('sourceKind')!='independent-gameplay'or row.get('sourceMediaSHA256')!=source['media']['sha256']or type(row.get('sourceFrame'))is not int:raise Pending('Gameplay editorial marks must bind exact source media and decoded frame')
  if row.get('visible')is True:
   if not row.get('rgbSHA256')or len(row['rgbSHA256'])!=64 or not row.get('actualSourceReview'):raise Pending('Gameplay mark requires directly inspected exact decoded RGB hash')
   bound(row['actualSourceReview'])
   box=row.get('bboxXYXY',[])
   if len(box)!=4 or not 0<=box[0]<box[2]<=1920 or not 0<=box[1]<box[3]<=1080:raise Pending('Gameplay focus box outside actual FHD source')
 return compile_guide_cues(annotations,timing,caption_helper)

def manual_game_guides(annotations,selection):
 """Manual editorial regions are not a detector or every-frame pixel review."""
 record=annotations.get('gameGuidesFile')
 if not record:raise Pending('Current actual-game editorial region/source proof required')
 data=read(bound(record));rows=data.get('guides',[])
 if data.get('schemaVersion')!='06.02-source-game-guides-v1'or data.get('topicId')!=TOPIC or not rows:raise Pending('Actual selected06 game guide file required')
 ledger=data.get('sourceLedger',{});review_pin=data.get('sourceReview',{})
 if not ledger.get('path')or Path(ledger['path']).resolve()!=(PROJECT/'source-footage.json').resolve():raise Pending('Manual guide source ledger must be selected06 footage')
 bound(ledger);review=read(bound(review_pin))
 if review.get('schemaVersion')!='06.02-source-game-manual-region-review-v1'or review.get('topicId')!=TOPIC or review.get('sourceLedger')!=ledger or review.get('sourceFramePtsVerifiedFromSoftwareShowinfo')is not True:raise Pending('Manual guide actual source/PTS review is absent or stale')
 for proof in review.get('decodeEvidence',[]):bound(proof)
 if not review.get('decodeEvidence')or not review.get('actualContactSheetsViewed'):raise Pending('Actual decode and sampled viewing evidence required')
 for proof in review['actualContactSheetsViewed']:bound(proof)
 if data.get('sourcePlaybackRate')!=1 or data.get('sourceAspect')!='full16:9'or data.get('sourceMediaModified')is not False or data.get('continuousTrackerVerified')is not False:raise Pending('Manual guide must preserve native source and honest review limits')
 for row in rows:
  key=row.get('sourceRef');source=selection['sourceRegistry'].get(key,{})
  media=row.get('sourceFile',{})
  if source.get('sourceKind')!='independent-gameplay'or not media.get('path')or Path(media['path']).resolve()!=Path(source['media']['path']).resolve()or media.get('sha256')!=source['media']['sha256']or row.get('guideType')!='manual-editorial-region':raise Pending('Manual region source identity/type differs')
  if row.get('actualSourceReview')!=review_pin or row.get('sourceId')!=source['id']or row.get('sourceDimensions')!=[1920,1080]or row.get('sourceFps')!='60/1':raise Pending('Manual region FHD60/source review identity differs')
  if row.get('nativePlaybackRate')!=1 or row.get('preserveFullSourceAspect')is not True or row.get('clearAtSourceCut')is not True or row.get('editorialNotDetector')is not True:raise Pending('Manual region needs native/aspect/cut/editorial limits')
  coverage=row.get('reviewedTemporalCoverage',{});a,b=coverage.get('sourceFrameRange',[None,None])
  available=[round(x*60)for x in source['selectedRange']]
  if type(a)is not int or type(b)is not int or not available[0]<=a<b<=available[1]or coverage.get('sourceSHA256')!=source['media']['sha256']:raise Pending('Editorial region must stay inside the inspected selected source window')
  if coverage.get('continuousTrackerVerified')is not False or coverage.get('finalMovingOutputReviewPending')is not True or coverage.get('interpolation')!='linear-between-inspected-keys-no-extrapolation'or not coverage.get('reason'):raise Pending('Manual coverage must retain its honest review/interpolation limits')
  for off in coverage.get('visibilityOffRanges',[]):
   if len(off)!=2 or any(type(x)is not int for x in off)or not a<=off[0]<off[1]<=b:raise Pending('Manual visibility-off interval escapes reviewed temporal range')
  inspected={}
  for proof in coverage.get('inspectedKeyframes',[]):
   f=proof['frame'];image=bound(proof['sourceImage'])
   from PIL import Image
   with Image.open(image)as im:
    if im.size!=(1920,1080)or hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()!=proof['rgbSHA256']:raise Pending('Inspected guide PNG does not match recorded native RGB')
   if f in inspected:raise Pending('Duplicate inspected guide keyframe')
   inspected[f]=proof
  for mark in row.get('marks',[]):
   if mark.get('type')not in('rectangle','ellipse')or not mark.get('label'):raise Pending('Manual guide shape/label required')
   anchor=mark.get('labelDisplayAnchor',[488,970]);font=mark.get('labelFontPx',40);stroke=mark.get('strokeWidthOutputPixels',8)
   if len(anchor)!=2 or any(type(v)not in(int,float)or not math.isfinite(v)for v in anchor)or not 48<=anchor[0]<=936 or not 300<=anchor[1]<=1480 or type(font)is not int or not 30<=font<=48 or type(stroke)is not int or not 4<=stroke<=12 or mark.get('fill')is not None:raise Pending('Manual guide label/stroke must fit the output safe area and stay hollow')
   keys=mark.get('keyframes',[])
   if not keys or [q['frame']for q in keys]!=sorted(set(q['frame']for q in keys)):raise Pending('Guide keyframes must be ordered and unique')
   for q in keys:
    if type(q['frame'])is not int or not a<=q['frame']<=b or q['frame']not in inspected or type(q.get('visible'))is not bool:raise Pending('Manual guide key lacks actual inspected source proof or visibility decision')
    if q.get('visible')is True:
     box=q.get('bboxXYXY',[])
     if len(box)!=4 or not 0<=box[0]<box[2]<=1920 or not 0<=box[1]<box[3]<=1080:raise Pending('Manual guide box outside source')
  if not row.get('marks'):raise Pending('No meaningful reviewed region in source guide')
 return rows

def exact_phrase_boundary(clock,phrase,edge):
 text=clock['canonicalKo']
 if text.count(phrase)!=1:raise Pending('Actual phrase must be unique canonical text')
 offset=text.index(phrase)+(len(phrase)if edge=='end'else 0);rows=[r for r in clock.get('canonicalWordBoundaries',[])if r['charOffset']==offset]
 if len(rows)!=1 or not clock['startFrame']<=rows[0]['frame']<=clock['endFrameExclusive']:raise Pending('Exact actual word boundary unsupported; never interpolate within one ASR word')
 return rows[0]

def verify_mc_manifest(path,caption_timing):
 """Recompute the current trusted cue/SDK recipe without rendering anything."""
 path=Path(path).resolve();row=read(path);segment=row.get('segment');runner_path=HERE/'run-prospect-refuge-diagrams.py'
 if sha(runner_path)!=MC_RUNNER_SHA or sha(HERE/'build-prospect-refuge-diagram-cues.py')!=MC_CUE_SHA or sha(HERE/'render-prospect-refuge-diagrams.cjs')!=MC_NODE_SHA:raise Pending('Audit changed selected06 MC runner/cue/SDK source')
 if row.get('schemaVersion')!='06-02-mc-crop-render-v1'or row.get('topicId')!=TOPIC or segment not in('p04','p25')or row.get('complete')is not True or not path.is_relative_to((MEDIA/'mc-render-attempts').resolve()):raise Pending('Actual selected06 MC render manifest required')
 pins=row.get('inputPins',[])
 for q in pins:bound(q)
 cues=[q for q in pins if Path(q['path']).name==segment+'.json'and Path(q['path']).resolve().is_relative_to((MEDIA/'diagram-cue-plans').resolve())]
 if len(cues)!=1:raise Pending('Actual MC must pin exactly one content-addressed selected cue plan')
 old_path=list(sys.path)
 try:
  sys.path.insert(0,str(HERE));runner=module('prospect_verified_mc_recipe',runner_path);prov=runner.prepare(bound(cues[0]))
 finally:sys.path[:]=old_path
 if not prov.get('ready')or any(row.get(k)!=prov.get(k)for k in('fingerprint','contract','inputPins','segment')):raise Pending('MC manifest differs from freshly verified current word/sample cue recipe')
 caption=pin(caption_timing)
 if not any(Path(q['path']).resolve()==Path(caption['path'])and q['sha256']==caption['sha256']for q in prov['inputPins']):raise Pending('MC recipe belongs to another actual caption clock')
 # Current Node manifest omits this field. Preserve that fact; derive it from
 # the exact reverified recipe rather than fabricating a manifest assertion.
 if 'actualCaptionBinding'in row and row['actualCaptionBinding']!=prov['actualCaptionBinding']:raise Pending('MC declared caption binding differs from its current recipe')
 if bound(row['output'])!=(path.parent/f'{segment}.silent.mp4').resolve():raise Pending('Actual MC output path differs from its owned attempt')
 encoded=row.get('encoded',{});c=prov['contract']
 if encoded.get('fullDecodePassed')is not True or encoded.get('ptsStrictlyIncreasing')is not True or(encoded.get('width'),encoded.get('height'),encoded.get('fps'),encoded.get('frames'),encoded.get('audioStreams'))!=(1080,900,'60/1',c['frames'],0):raise Pending('Actual silent MC decode/PTS proof differs from contract')
 row['_pin']=pin(path);row['_currentProvenance']=prov;return row

def context_boundary(spec,clocks,resolved,allow_source_duration=False):
 if not isinstance(spec,dict):raise Pending('A picture boundary must name an actual sentence/word boundary')
 if 'afterOverrideId'in spec:
  if spec['afterOverrideId']not in resolved:raise Pending('Unknown/forward context override dependency')
  return resolved[spec['afterOverrideId']]
 key=(spec.get('paragraph'),spec.get('sentenceIndexZeroBased'))
 if key not in clocks:raise Pending('Picture boundary names an unknown actual sentence')
 clock=clocks[key];kind=spec.get('boundary')
 if kind=='sentence-start':return clock['startFrame']
 if kind=='sentence-end':return clock['endFrameExclusive']
 if kind in('phrase-start','phrase-end'):return exact_phrase_boundary(clock,spec['exactKoPhrase'],'start'if kind.endswith('start')else'end')['frame']
 raise Pending('Unsupported picture boundary; fixed seconds/character fractions are not accepted')

def additional_source_windows(data,selection):
 result={}
 for record in data.get('additionalSourceSelections',[]):
  value=read(bound(record));key=value.get('sourceRef');source=selection['sourceRegistry'].get(key,{});media=value.get('sourceFile',{})
  if value.get('schemaVersion')!='06-02-additional-source-window-review-v1'or value.get('topicId')!=TOPIC or source.get('sourceKind')!='independent-gameplay'or not media.get('path')or Path(media['path']).resolve()!=Path(source['media']['path']).resolve()or media.get('sha256')!=source['media']['sha256']:raise Pending('Additional inspected window must use exactly the same selected source file')
  if value.get('sourceDimensions')!=[1920,1080]or value.get('sourceFps')!='60/1'or value.get('playbackRate')!=1 or value.get('preserveFullAspect')is not True or value.get('sourceMediaModified')is not False or value.get('frameRangeConvention')!='start-inclusive/end-exclusive':raise Pending('Additional inspected source FHD/native/aspect contract differs')
  a,b=value.get('additionalAvailableFrameRange',[None,None])
  if type(a)is not int or type(b)is not int or not 0<=a<b<=source['nativeFrames']:raise Pending('Additional inspected window escapes actual source frame count')
  for name in('sourceLedger','rightsReview'):bound(value[name])
  if Path(value['sourceLedger']['path']).resolve()!=(PROJECT/'source-footage.json').resolve()or Path(value['rightsReview']['path']).resolve()!=(PROJECT/'footage-rights-review-v1.json').resolve():raise Pending('Additional source window must retain selected source/rights ledgers')
  def nested_pins(item):
   if isinstance(item,dict):
    if'path'in item and'sha256'in item:bound(item)
    else:
     for v in item.values():nested_pins(v)
   elif isinstance(item,list):
    for v in item:nested_pins(v)
  nested_pins(value['actualSourceInspection']);nested_pins(value['decodeEvidence']);frames=set()
  for proof in value.get('sourceFramePtsProofs',[]):
   f=proof['sourceFrame'];n,d=proof['timeBase']
   if type(f)is not int or Fraction(proof['pts']*n,d)!=Fraction(f,60):raise Pending('Additional source sample PTS is not its decoded60fps frame index')
   bound(proof['sourceImage']);frames.add(f)
  if not{a,b-1}.issubset(frames):raise Pending('Additional window needs actual first/last source frame PTS/image proofs')
  result.setdefault(key,[]).append(dict(sourceRef=key,frameRange=[a,b],record=record))
 return result

def compile_picture_overrides(data,selection,timing):
 """Compile explicit adopted context carry/trim decisions, never propose trims."""
 if data.get('schemaVersion')!='06-02-picture-overrides-v1'or data.get('topicId')!=TOPIC or data.get('status')!='adopted-actual-clock':raise Pending('Provisional picture choices cannot become an actual timeline')
 clocks={(r['paragraph'],r['sentenceIndexZeroBased']):r for r in timing['sentences']};registry=selection['sourceRegistry'];resolved={};sections=[];extra=additional_source_windows(data,selection)
 for row in data.get('overrides',[]):
  identity=row.get('id')
  if not identity or identity in resolved or not row.get('reason')or not row.get('actualSourceInspection'):raise Pending('Each context override needs identity, reason and actual source inspection proof')
  bound(row['actualSourceInspection']);start=context_boundary(row['start'],clocks,resolved);motion=row.get('playback')=='native-1x';source_range=row.get('sourceFrameRange')
  if motion:
   if not isinstance(source_range,list)or len(source_range)!=2 or any(type(f)is not int for f in source_range)or not 0<=source_range[0]<source_range[1]:raise Pending('1x override requires an explicit integer source-frame subrange')
   if row.get('end',{}).get('boundary')=='source-duration':end=start+source_range[1]-source_range[0]
   else:end=context_boundary(row['end'],clocks,resolved)
   if end-start!=source_range[1]-source_range[0]:raise Pending('Source/context duration differs; no padding, slowdown or speedup')
  elif row.get('playback')=='purposeful-still':end=context_boundary(row['end'],clocks,resolved)
  else:raise Pending('Override playback must be native-1x or a reasoned purposeful still')
  if not 0<=start<end<=timing['totalFrames']:raise Pending('Picture override escapes actual PCM clock')
  context=[[r['paragraph'],r['sentenceIndexZeroBased']]for r in timing['sentences']if max(start,r['startFrame'])<min(end,r['endFrameExclusive'])]
  if row.get('allowedSpokenContext')!=context:raise Pending('Context carry must explicitly list exactly the actual sentences it covers')
  cuts=[dict(frame=start,visuals=row.get('visuals',[]))]
  for cut in row.get('viewCuts',[]):cuts.append(dict(frame=context_boundary(cut['at'],clocks,resolved),visuals=cut['visuals']))
  if[c['frame']for c in cuts]!=sorted(set(c['frame']for c in cuts))or any(not start<=c['frame']<end for c in cuts):raise Pending('View cuts must be ordered actual boundaries inside the same source clock')
  used=set()
  for i,cut in enumerate(cuts):
   a=cut['frame'];b=cuts[i+1]['frame']if i+1<len(cuts)else end;panels=[]
   for visual in cut['visuals']:
    for view in view_descriptors(visual,registry):
     source=registry[view['sourceRef']];used.add(view['sourceRef']);limit=source.get('frames',source.get('contract',{}).get('frames'))
     actual=source['sourceKind']=='independent-gameplay'
     extra_window=None
     if actual:
      allowed=[round(v*60)for v in source['selectedRange']]
      if motion and not allowed[0]<=source_range[0]<source_range[1]<=allowed[1]:extra_window=next((v for v in extra.get(view['sourceRef'],[])if v['frameRange'][0]<=source_range[0]<source_range[1]<=v['frameRange'][1]),None)
      if not motion or(not allowed[0]<=source_range[0]<source_range[1]<=allowed[1]and extra_window is None):raise Pending('Actual game override must stay inside a selected or additionally inspected source window')
     elif not isinstance(limit,int)or(motion and not 0<=source_range[0]<source_range[1]<=limit):raise Pending('Native override escapes actual captured frame range')
     f=visual.get('sourceFrame')
     if not motion and(type(f)is not int or not 0<=f<limit):raise Pending('Purposeful still needs an actual captured frame')
     panels.append(dict(view,sourceFrame=f,sourceFrameRange=source_range if motion else None,targetAnchors=visual.get('targetAnchors',[]),focusKo=visual.get('focusKo',row['reason']),framing=visual.get('cameraFraming',{}).get(view['camera'],{}),bodyPointLabelLayout=visual.get('bodyPointLabelLayout'),additionalSourceWindow=extra_window))
   if not 1<=len(panels)<=4:raise Pending('Override must contain1..4 actual views')
   kinds={p['sourceKind']=='independent-gameplay'for p in panels}
   if len(kinds)!=1 or(True in kinds and len(panels)!=1):raise Pending('Do not mix actual game and own implementation in an ambiguous picture override')
   kind='gameplay'if True in kinds else'native';clock=next(r for r in timing['sentences']if r['startFrame']<=a<r['endFrameExclusive'])
   sections.append(dict(id=f'override-{identity}-{i:02}',startFrame=a,endFrameExclusive=b,kind=kind,paragraph=clock['paragraph'],sentenceIndexZeroBased=clock['sentenceIndexZeroBased'],panels=panels,sourceStartFrame=source_range[0]+a-start if motion else None,frameCount=b-a if motion else 1,rate=1 if motion else None,holdReason=None if motion else row['reason'],term=None,sourceKind=panels[0]['sourceKind'],explicitContextOverrideId=identity,allowedSpokenContext=context,actualSourceInspection=row['actualSourceInspection'],timingDecisionReason=row['reason']))
  expected=[]
  for ref in sorted(used):
   src=registry[ref];expected.append(src['media']if src['sourceKind']=='independent-gameplay'else src['frameHashManifest'])
  normalize=lambda pins:sorted((str(Path(q['path']).resolve()),q['sha256'])for q in pins)
  if normalize(row.get('sourceProofs',[]))!=normalize(expected):raise Pending('Override must explicitly pin exactly the selected source media/capture proofs')
  for q in row['sourceProofs']:bound(q)
  resolved[identity]=end
 sections.sort(key=lambda s:s['startFrame'])
 if any(a['endFrameExclusive']>b['startFrame']for a,b in zip(sections,sections[1:])):raise Pending('Overlapping picture decisions are ambiguous')
 if not sections:raise Pending('No adopted picture overrides')
 return sections

def prepare_picture_overrides(path,selection,timing,caption_timing):
 data=read(path)
 if data.get('baseSelection')!=pin(PROJECT/'native-teaching-selection-v2.json')or data.get('narration')!=pin(PROJECT/'narration-expanded-draft-v3.json')or data.get('captionTiming')!=pin(caption_timing):raise Pending('Picture overrides bind another source lesson/actual voice clock')
 for key in('baseSelection','narration','captionTiming'):bound(data[key])
 return compile_picture_overrides(data,selection,timing)

def apply_picture_overrides(base,overrides):
 result=[]
 for source in base:
  chunks=[(source['startFrame'],source['endFrameExclusive'])]
  for row in overrides:
   new=[]
   for a,b in chunks:
    if row['endFrameExclusive']<=a or row['startFrame']>=b:new.append((a,b));continue
    if a<row['startFrame']:new.append((a,row['startFrame']))
    if row['endFrameExclusive']<b:new.append((row['endFrameExclusive'],b))
   chunks=new
  if chunks and source.get('pendingTimingConflict'):raise Pending('Unresolved base picture timing remains after explicit overrides: '+source['pendingTimingConflict'])
  for a,b in chunks:
   row=copy.deepcopy(source);row['startFrame']=a;row['endFrameExclusive']=b
   if row.get('rate')==1:row['sourceStartFrame']+=a-source['startFrame'];row['frameCount']=b-a
   if row.get('transition')and(a,b)!=(source['startFrame'],source['endFrameExclusive']):raise Pending('Do not silently clip an approved editorial transition')
   result.append(row)
 result+=copy.deepcopy(overrides);result.sort(key=lambda r:r['startFrame']);cursor=0
 for i,row in enumerate(result):
  if row['startFrame']!=cursor:raise Pending('Overrides produced a picture gap/overlap')
  row['id']=f's{i+1:04}';cursor=row['endFrameExclusive']
 if not base or cursor!=base[-1]['endFrameExclusive']:raise Pending('Overrides changed final actual PCM picture clock')
 return result

def plan(selection,timing,mc_manifests,decisions=None,picture_overrides=None):
 """Pure deterministic routing; actual derived timestamps are the only clock."""
 clocks=validate_sentence_clock(selection,timing);lookup={(r['paragraph'],r['sentenceIndexZeroBased']):r for r in clocks};registry=selection['sourceRegistry'];sections=[];cats=[];cursor=0
 def add(start,end,**value):
  nonlocal cursor
  if start!=cursor or type(end)is not int or end<=start:raise Pending('Picture clock gap/zero interval')
  sections.append(dict(id=f's{len(sections)+1:04}',startFrame=start,endFrameExclusive=end,**value));cursor=end
 if not decisions or decisions.get('schemaVersion')!='06-02-film-asbuilt-decisions-v1':raise Pending('Selected root-authorized camera/body and closinghero choices required')
 for para in selection['paragraphs']:
  p=para['paragraph'];sentences=para['sentences']
  if p in(4,25):
   first=lookup[p,0]['startFrame'];last=lookup[p,len(sentences)-1]['endFrameExclusive'];mc=mc_manifests.get(p)
   if not mc or mc['contract']['frames']!=last-first:raise Pending(f'Actual speech-bound P{p:02} MC duration required')
   binding=mc.get('_currentProvenance',{}).get('actualCaptionBinding',mc.get('actualCaptionBinding',{}))
   if(binding.get('startFrame'),binding.get('endFrameExclusive'))!=(first,last):raise Pending('MC crop does not bind exact actual paragraph clock')
   adopted_end=lookup[25,2]['endFrameExclusive']if p==25 else last
   add(first,adopted_end,kind='mc',paragraph=p,sourcePath=mc['output']['path'],sourceSHA256=mc['output']['sha256'],sourceStartFrame=0,frameCount=adopted_end-first,rate=1,mcManifest=mc['_pin'],actualCaptionBinding=binding,captionBindingDerivedFromCurrentRecipe='_currentProvenance'in mc,rawManifestContainedCaptionBinding='actualCaptionBinding'in mc,criticalContentSourceBoxes=mc.get('criticalContentSourceBoxes',[]),destinationXYWH=[56,360,864,720],sourceKind='our-authored-abstract-diagram',catPolicy='off-dense-relationship-map',fullRenderedParagraphPreserved=True)
   if p==25:
    c=lookup[25,3];hero=decisions['closingHero']
    if c['canonicalKo']!=hero['canonicalKo']or(hero['beforeMode'],hero['afterMode'],hero['sourceFrame'],hero['transitionFrames'])!=('baseline','shifted',599,12):raise Pending('Root-authorized closinghero source/text changed')
    boundary=exact_phrase_boundary(c,hero['cutAtExactPhraseEndKo'],'end');cut=boundary['frame'];start,end=c['startFrame'],c['endFrameExclusive']
    if not start<cut<cut+12<end:raise Pending('Actual closing word boundary needs room for the12frame same-position transition; do not add time')
    panel=lambda mode:dict(sourceRef='close',sourceKind=registry['close']['sourceKind'],mode=mode,camera='closeup',modeFolder=str(Path(registry['close']['output'])/mode),cropXYXY=None,sourceFrame=599,sourceFrameRange=None,targetAnchors=['body-head','body-torso','body-hips'],focusKo='같은경로/다른엄폐 결과',framing={},bodyPointLabelLayout='body-point-label-layout-v2')
    before,after=panel('baseline'),panel('shifted')
    for a,b,current,transition in[(start,cut,before,None),(cut,cut+12,after,dict(kind='same-position-crossfade',fromPanel=before,frameCount=12)),(cut+12,end,after,None)]:add(a,b,kind='native',paragraph=25,sentenceIndexZeroBased=3,panels=[current],sourceStartFrame=None,frameCount=1,rate=None,holdReason='Return to the actual same-input cover comparison while the final sentence states the thesis.',term=None,sourceKind=registry['close']['sourceKind'],transition=transition,closingHero=True,spokenSubbeatBoundary=boundary)
    cats.append(dict(startFrame=start,endFrameExclusive=end,pose=hero['catPose'],purpose=hero['catPurpose'],easeInFrames=9,easeOutFrames=12))
   continue
  for sentence in sentences:
   j=sentence['sentenceIndexZeroBased'];clock=lookup[p,j];start,end=clock['startFrame'],clock['endFrameExclusive'];visuals=sentence['visuals'];panels=[]
   for v in visuals:
    for view in view_descriptors(v,registry):
     panels.append(dict(view,sourceFrame=v.get('sourceFrame'),sourceFrameRange=v.get('sourceFrameRange'),targetAnchors=v['targetAnchors'],focusKo=v['focusKo'],framing=v.get('cameraFraming',{}).get(view['camera'],{}),bodyPointLabelLayout=v.get('bodyPointLabelLayout')))
   if(p,j)==(5,2):
    boundary=exact_phrase_boundary(clock,decisions['cameraBodyClause']['cutAtExactPhraseStartKo'],'start');cut=boundary['frame']
    if not start<cut<end:raise Pending('Actual camera/body word boundary is at a sentence edge')
    views=[[p for p in panels if p['sourceRef']=='main'],[p for p in panels if p['sourceRef']=='close']]
    if[len(x)for x in views]!=[2,1]:raise Pending('Camera/body view contract changed')
    for a,b,chosen in[(start,cut,views[0]),(cut,end,views[1])]:add(a,b,kind='native',paragraph=p,sentenceIndexZeroBased=j,panels=chosen,sourceStartFrame=None,frameCount=1,rate=None,holdReason='Explain the actual camera eye, then the same-state body at the exact spoken word boundary.',term=None,sourceKind=chosen[0]['sourceKind'],spokenSubbeatBoundary=boundary)
    continue
   motion=[x for x in panels if x['sourceFrameRange']is not None]
   # Simultaneous real cameras share one motion clock. Multi-example grids are
   # deliberately still comparisons, never a duration-ratio montage.
   if motion:
    spans={tuple(x['sourceFrameRange'])for x in motion}
    if len(spans)!=1 or len(motion)!=len(panels):raise Pending(f'P{p:02}s{j} needs explicit actual subcue boundaries for unequal simultaneous clips')
    a,b=next(iter(spans));count=b-a
    actual=panels[0]['sourceKind']=='independent-gameplay'
    if count>end-start or(actual and count!=end-start):
     conflict=f'P{p:02}s{j}: native1x {count}frames versus actual spoken {end-start}; explicit inspected trim/contextcarry required, never speed/loop or automaticfreeze'
     if not picture_overrides:raise Pending(conflict)
     add(start,end,kind='gameplay'if actual else'native',paragraph=p,sentenceIndexZeroBased=j,panels=panels,sourceStartFrame=a,frameCount=count,rate=1,holdReason=None,term=term_for(p,j),sourceKind=panels[0]['sourceKind'],pendingTimingConflict=conflict)
     continue
    add(start,start+count,kind='gameplay'if actual else'native',paragraph=p,sentenceIndexZeroBased=j,panels=panels,sourceStartFrame=a,frameCount=count,rate=1,holdReason=None,term=term_for(p,j),sourceKind=panels[0]['sourceKind'])
    if start+count<end:
     if actual:raise Pending(f'P{p:02}s{j}: availableactual6/8/8swindow differs fromnaturalcomponent; requires explicit inspectedtrim/contextcarry decision, never automaticfreeze/silence')
     add(start+count,end,kind='native',paragraph=p,sentenceIndexZeroBased=j,panels=panels,sourceStartFrame=b-1,frameCount=1,rate=None,holdReason='Read the narrated result with progressive actual-object labels for the exact remaining spoken interval.',term=term_for(p,j),sourceKind=panels[0]['sourceKind'])
   else:
    if any(x['sourceFrame']is None for x in panels):raise Pending('Unrendered/cueless source cannot enter native timeline')
    add(start,end,kind='native',paragraph=p,sentenceIndexZeroBased=j,panels=panels,sourceStartFrame=None,frameCount=1,rate=None,holdReason='Purposeful actual-state explanation: '+sentence['visuals'][0]['focusKo'],term=term_for(p,j),sourceKind=panels[0]['sourceKind'])
   if(p,j)in((1,2),(9,3),(25,3)):
    # Cat is an intentional reaction/point/closing request. Renderer checks
    # actual protectedcontent boxes, never shrinks/moves the approved mascot.
    section=sections[-1]
    if len(panels)==1 and section['kind']=='native'and end-start>=60:cats.append(dict(startFrame=max(start,end-120),endFrameExclusive=end,pose='puzzled'if p==1 else'realize',purpose='reveal'if p==1 else'point',easeInFrames=9,easeOutFrames=12))
 # Source-authored dense relationship maps remain mascot-free. A closing
 # hero would be a separate explicit as-built visual choice, not a map cover.
 if cursor!=timing['totalFrames']:raise Pending('Final exactPCM rounding frame is uncovered')
 if picture_overrides:sections=apply_picture_overrides(sections,picture_overrides)
 return dict(schemaVersion='06-02-final-timeline-v1',topicId=TOPIC,status='actual-asr-aligned',format=dict(width=1080,height=1920,fps=60),totalFrames=cursor,sections=sections,catCues=cats,appliedPictureOverrideIds=list(dict.fromkeys(s['explicitContextOverrideId']for s in picture_overrides or[])),closingCatDecision='root-authorized baseline599→shifted599 singlehero at actual word END; cat OFF on dense maps',captions=copy.deepcopy(timing['captions']),paragraphs=copy.deepcopy(timing['paragraphs']),sentenceClocks=copy.deepcopy(clocks),actualListening=False,actualRealtimePlayback=False,humanApproval=False,platformActions=[])

def prepare(caption_timing,audio_build,mc_paths,annotation_plan,picture_overrides=None):
 cp=HERE/'build-prospect-refuge-caption-timing.py';ap=HERE/'prepare-prospect-refuge-audio.py'
 if not cp.exists()or not ap.exists()or sha(cp)!=CAPTION_SHA or sha(ap)!=AUDIO_SHA:raise Pending('Audit changed selected06 caption/audio adapters before use')
 captions=module('prospect_actual_caption_binding',cp);audio=module('prospect_actual_mix_binding',ap)
 verified=captions.verify_existing(caption_timing);timing=verified['timing'];voice=verified['voice'];mix=audio.verified_audio_build(audio_build)
 if isinstance(mix,dict)and'audioBuild'in mix:mix=mix['audioBuild']
 selection=read(PROJECT/'native-teaching-selection-v2.json');narration=read(PROJECT/'narration-expanded-draft-v3.json')
 for i,p in enumerate(selection['paragraphs']):
  if p['canonicalKo']!=narration['narrationKo'][i]or p['canonicalEn']!=narration['paragraphsEn'][i]:raise Pending('Changed approved learning prose')
 if mix['topicId']!=TOPIC or mix['rawVoiceFingerprint']!=voice['fingerprint']or mix['canonicalTiming']!=voice['timing']:raise Pending('Accepted mix/voice canonical clock differs')
 registry=selection['sourceRegistry'];mc={}
 for path in mc_paths:
  row=verify_mc_manifest(path,caption_timing);segment=row['segment'];p=int(segment[1:])
  if p in mc:raise Pending('Exactly one actual MC render per P04/P25 required')
  if row['contract'].get('audio')is not False or(row['contract']['width'],row['contract']['height'],row['contract']['fps'])!=(1080,900,60):raise Pending('MC must be actualsilent1080x900/60 source')
  bound(row['output'])
  for q in row['inputPins']:bound(q)
  mc[p]=row
 if set(mc)!={4,25}:raise Pending('Both actual speech-bound MC outputs required')
 annotations=read(annotation_plan);guide_cues=verify_annotations(annotations,selection,timing,captions);game_guides=manual_game_guides(annotations,selection)
 decisions=read(PROJECT/'film-asbuilt-decisions-v1.json')
 for q in decisions['inputs']:bound(q)
 overrides=prepare_picture_overrides(picture_overrides,selection,timing,caption_timing)if picture_overrides else None
 result=plan(selection,timing,mc,decisions,overrides);result['sourceRegistry']=registry;result['annotationPlan']=annotations;result['asBuiltDecisions']=pin(PROJECT/'film-asbuilt-decisions-v1.json')
 result['pictureOverrides']=pin(picture_overrides)if picture_overrides else None
 result['guideCues']=guide_cues
 result['manualGameGuides']=game_guides
 result['audio']=dict(voice=voice['aggregateWav'],mix=mix['mixWav'],build=pin(audio_build));result['subtitles']={lang:pin(Path(caption_timing).parent/f'captions.{lang}.srt')for lang in('ko','en')}
 result['titleKo']=narration['titleKo'];result['sourceSelection']=pin(PROJECT/'native-teaching-selection-v2.json');result['bodyPointLabelLayout']=read(PROJECT/'body-point-label-layout-v2.json')
 roles={'narration':PROJECT/'narration-expanded-draft-v3.json','selection':PROJECT/'native-teaching-selection-v2.json','as-built-decisions':PROJECT/'film-asbuilt-decisions-v1.json','caption-timing':Path(caption_timing),'caption-helper':cp,'audio-build':Path(audio_build),'audio-helper':ap,'annotation-plan':Path(annotation_plan),'body-labels':PROJECT/'body-point-label-layout-v2.json','timeline-helper':Path(__file__),'renderer':HERE/'render-prospect-refuge-film.py','style':ROOT/'projects/shorts-leveldesign-03-02/visual-layout-v1.json','style-helper':ROOT/'projects/shorts-leveldesign-03-02/production/composite-native-frame.py','stream-helper':HERE/'render-zen-view-film.py','encoder-helper':HERE/'render-first-film.py','resource-helper':HERE/'run-prospect-refuge-corrections-native.py'}
 result['inputs']=[pin(path,role)for role,path in roles.items()]+[pin(v['_pin']['path'],'mc-p%02d'%p)for p,v in mc.items()]
 result['inputs'].append(pin(HERE/'run-prospect-refuge-diagrams.py','mc-recipe-helper'))
 if picture_overrides:result['inputs'].append(pin(picture_overrides,'picture-overrides'))
 renderer=module('prospect_renderer_contract',HERE/'render-prospect-refuge-film.py');renderer.verify_inputs(result);result['fingerprint']=digest(result);return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--caption-timing');p.add_argument('--audio-build');p.add_argument('--mc-manifest',action='append',default=[]);p.add_argument('--annotation-plan');p.add_argument('--picture-overrides');p.add_argument('--write',action='store_true');a=p.parse_args()
 try:
  if not a.caption_timing or not a.audio_build or len(a.mc_manifest)!=2 or not a.annotation_plan:raise Pending('Requires actual96PCM/ASR captiontiming, acceptedmix, twoactualMC manifests and source-coordinate annotationplan; nothing generated')
  t=prepare(a.caption_timing,a.audio_build,a.mc_manifest,a.annotation_plan,a.picture_overrides)
  if a.write:
   out=MEDIA/'film-timelines'/t['fingerprint'][:24];out.mkdir(parents=True,exist_ok=True);path=out/'timeline.json';data=json.dumps(t,ensure_ascii=False,indent=2)+'\n'
   if path.exists()and path.read_text(encoding='utf8')!=data:raise Pending('Preserve previous timeline bytes')
   if not path.exists():path.write_text(data,encoding='utf8')
  print(json.dumps(dict(ready=True,fingerprint=t['fingerprint'],written=a.write,mediaStarted=False)))
 except(RuntimeError,AssertionError,FileNotFoundError,KeyError)as error:
  if a.write:raise
  print(json.dumps(dict(ready=False,pending=str(error),written=False,mediaStarted=False)))
if __name__=='__main__':main()
