"""Bind the root's13 picture choices to actual103/96 caption clocks, CPU-only.

Default is read-only. --write adopts only the already selected, inspected
source windows into an immutable JSON cut record; it never renders or changes audio.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT/'projects/shorts-leveldesign-06-02'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-06-02')
CAPTION_SHA='fec20b03156cff68fa80d5d2be56a0407634fcf3287e516bb70ff3ffa8413769'
DECISIONS_SHA='90f48e7f199fd99977a0b30aa54cc93169706c84ee2af3746537fb0981389857'
class Pending(RuntimeError):pass
def require(ok,text):
 if not ok:raise Pending(text)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def make_payload(selection,timing,builder,caption_path):
 builder.validate_sentence_clock(selection,timing);builder.validate_physical_clock(selection,timing)
 clocks={(r['paragraph'],r['sentenceIndexZeroBased']):r for r in timing['sentences']};source={(p['paragraph'],r['sentenceIndexZeroBased']):r for p in selection['paragraphs']for r in p['sentences']};rows=[]
 point=lambda p,s,edge='sentence-start':dict(paragraph=p,sentenceIndexZeroBased=s,boundary=edge)
 def visual(p,s,index=0,camera=None,frame=None):
  v=copy.deepcopy(source[p,s]['visuals'][index])
  if camera:v['camera']=camera
  v['sourceFrame']=frame;v['sourceFrameRange']=None
  return v
 def add(identity,start,end,views,reason,source_range=None):
  motion=source_range is not None;row=dict(id=identity,start=start,end=end,playback='native-1x'if motion else'purposeful-still',visuals=views,reason=reason,actualSourceInspection=pin(PROJECT/'native-teaching-selection-v3.json'),sourceInspectionScope='Bound original sampled source views/sequence evidence; root picture choices are recorded separately. Not final moving/encoded/hearing approval.')
  if motion:row['sourceFrameRange']=source_range
  registry=selection['sourceRegistry'];refs=sorted({v['sourceRef']for v in views});row['sourceProofs']=[registry[k]['media']if registry[k]['sourceKind']=='independent-gameplay'else registry[k]['frameHashManifest']for k in refs]
  resolved={r['id']:r['_end']for r in rows};a=builder.context_boundary(start,clocks,resolved)if start.get('boundary')!='source-duration-before-end'else None
  if end.get('boundary')=='source-duration':b=a+source_range[1]-source_range[0]
  else:b=builder.context_boundary(end,clocks,resolved)
  if a is None:a=b-source_range[1]+source_range[0]
  require(a<b,'A root-selected result hold would have no actual speech interval: '+identity)
  row['allowedSpokenContext']=[[r['paragraph'],r['sentenceIndexZeroBased']]for r in timing['sentences']if max(a,r['startFrame'])<min(b,r['endFrameExclusive'])]
  row['_end']=b;rows.append(row);return row
 def held(identity,after,p,s,views,reason,end=None):return add(identity,dict(afterOverrideId=after),end or point(p,s,'sentence-end'),views,reason)
 def run(identity,p,s,source_range,views,reason):return add(identity,point(p,s),dict(boundary='source-duration'),views,reason,source_range)
 run('opening-d-6s',1,0,[360,720],[visual(1,0)],'Uninterrupted observed guard positions through the frame, across both opening sentences; no hidden-player/patrol claim.')
 require(rows[-1]['_end']==clocks[1,1]['endFrameExclusive'],'D6s must exactly cover the current two related opening sentences; no hold/padding fallback')
 run('scale-full-reveal',2,1,[90,540],[visual(2,1)],'Complete narrow-to-open scale reveal at native1x across the following directly related clause.')
 held('scale-result','scale-full-reveal',2,2,[visual(2,2,frame=540)],'Explain the already revealed open region, using inspected frame540 rather than loop or padding.')
 r=run('main-controlled-full-run',5,0,[0,600],[visual(5,0)],'Run both unchanged controlled tapes once through the whole captured event, continuing briefly into the camera/body explanation.')
 r['viewCuts']=[dict(at=point(5,1),visuals=[visual(5,1)])]
 held('main-camera-eye-detail','main-controlled-full-run',5,2,[visual(5,2,index=0,frame=0)],'Return to the meaningful initial camera-eye explanation; switch to the existing closeup at the actual body phrase.',end=dict(point(5,2,'phrase-start'),exactKoPhrase='적이 볼 수 있는 캐릭터의 몸은'))
 run('closeup-full-after-comparison',6,1,[90,600],[visual(6,1)],'Native same-time A/B closeup before/action/result, no replay or time warp.')
 held('closeup-result','closeup-full-after-comparison',6,2,[visual(6,2,frame=599)],'Read the two real final visibility conditions at the shared final moving state.')
 run('atrium-lower-public',7,1,[0,360],[visual(7,1)],'Show public circulation below the stationary private-room actor, continuing the same explanation.')
 held('atrium-public-private-result','atrium-lower-public',7,2,[visual(7,2,frame=360)],'Purposeful shared-space result while its relationship is explained.')
 run('atrium-height-to-ceiling',8,1,[360,720],[visual(8,1)],'Preserve the height/outlook illustration at native1x across the next related sentence.')
 held('atrium-height-result','atrium-height-to-ceiling',8,2,[visual(8,2,index=0,frame=719)],'Keep the raised observation state until the exact spoken word introducing lowered refuge.',end=dict(point(8,2,'phrase-start'),exactKoPhrase='낮추면'))
 add('lowered-refuge-section',dict(point(8,2,'phrase-start'),exactKoPhrase='낮추면'),point(8,2,'sentence-end'),[visual(8,2,index=1,frame=300)],'Switch to the actual depressed floor/interior ceiling section at the word 낮추면; the mandatory large section/height labels remain required.')
 run('courtyard-two-guards',16,1,[300,720],[visual(16,1,camera='dual')],'Continuous same-event player/observer pictures show the route, guards and changed final outlook.')
 held('courtyard-final-observation','courtyard-two-guards',16,2,[visual(16,2,camera='dual',frame=719)],'Inspect the actual final new observation state; not a guarantee of safe or undetected crossing.')
 run('alcove-reveal-through-action',18,2,[479,690],[visual(18,2)],'Allow the actual wall-to-item reveal to finish across the related following sentence; preserve target-self collider facts.')
 held('alcove-revealed-item','alcove-reveal-through-action',18,3,[visual(18,3,frame=719)],'Read the revealed item result; not a fabricated raw blocked=false claim.')
 for identity,p,s,ref,start,maximum in [('metroid-observed-trim',19,0,'M',600,1080),('hl2-already-arranged-board',23,3,'H',1320,1652)]:
  n=clocks[p,s]['endFrameExclusive']-clocks[p,s]['startFrame'];require(start+n<=maximum,'Actual related-game sentence exceeds the explicitly inspected source window: '+identity)
  add(identity,point(p,s),point(p,s,'sentence-end'),[visual(p,s)],'Observed independent gameplay native1x, only the relevant before/action/result window. HL2 board is already arranged; enemy shield in Metroid is not player refuge.',[start,start+n])
 run('flying-finish-path',20,1,[211,600],[visual(20,1)],'Finish the forward ledge/jump encounter rather than return to an earlier unrelated motion state.')
 held('flying-result','flying-finish-path',20,2,[visual(20,2,frame=599)],'Read the actual final player/ledge/enemy positions; root directly viewed both599 source cameras at375px.')
 run('boss-forward-run',22,1,[150,600],[visual(22,1)],'Finish the open encounter forward movement while the attack-reading explanation continues.')
 held('boss-result','boss-forward-run',22,2,[visual(22,2,frame=599)],'Use the last chosen moving state599, directly inspected by root;600 also exists in the720-frame capture.')
 add('footings-placement-before-game',dict(boundary='source-duration-before-end'),point(23,2,'sentence-end'),[visual(23,2)],'The whole authored tool-lift/place event ends exactly at the actual action-clause end, naturally overlapping the relevant preceding tool definition.',[90,360])
 for r in rows:r.pop('_end')
 result=dict(schemaVersion='06-02-picture-overrides-v1',topicId='06.02',status='adopted-actual-clock',baseSelection=pin(PROJECT/'native-teaching-selection-v3.json'),narration=pin(PROJECT/'narration-expanded-draft-v4.json'),captionTiming=pin(caption_path),rootRecommendations=pin(PROJECT/'picture-context-recommendations-v2.json'),additionalSourceSelections=[pin(PROJECT/'additional-source-window-review-v1.json')],overrides=rows,logicalGroups=96,physicalVoiceUnits=103,selectedMotionChoices=13,voiceModified=False,actualEncodedMotionReviewed=False,actualListening=False,humanApproval=False,platformActions=[],adoptionScope='Root-recommended exact picture edits within selected06.02. Actual timestamps derive only from current source-bound raw ASR/sample clocks; --write materializes the internal cut record, never final visual/listening approval.')
 compiled=builder.compile_picture_overrides(result,selection,timing)
 result['compiledSegments']=[dict(id=r['id'],startFrame=r['startFrame'],endFrameExclusive=r['endFrameExclusive'],sourceStartFrame=r['sourceStartFrame'],frameCount=r['frameCount'],sourceRefs=[p['sourceRef']for p in r['panels']])for r in compiled]
 result['fingerprint']=digest(result);return result

def prepare(caption_path):
 cp=HERE/'build-prospect-refuge-caption-timing-v3.py';require(sha(cp)==CAPTION_SHA,'Final captionV3 helper changed')
 decision=PROJECT/'picture-context-recommendations-v2.json';require(sha(decision)==DECISIONS_SHA,'Root13 picture decisions changed; review before adoption')
 cap=module('prospect_picture_current_caption',cp);verified=cap.verify_existing(caption_path);builder=module('prospect_picture_film_builder',HERE/'build-prospect-refuge-film-timeline-v2.py');selection=read(PROJECT/'native-teaching-selection-v3.json')
 result=make_payload(selection,verified['timing'],builder,caption_path);result['sourceHelpers']=[pin(__file__),pin(cp),pin(HERE/'build-prospect-refuge-film-timeline-v2.py')];result.pop('fingerprint');result['fingerprint']=digest(result);return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--caption-timing');p.add_argument('--write',action='store_true');a=p.parse_args()
 try:
  require(a.caption_timing,'ActualV3 caption clock is required; no picture choices materialized');r=prepare(a.caption_timing);path=MEDIA/'picture-overrides-v2'/r['fingerprint'][:24]/'picture-overrides.json'
  if a.write:
   data=json.dumps(r,ensure_ascii=False,indent=2)+'\n';path.parent.mkdir(parents=True,exist_ok=True);require(not path.exists()or path.read_text(encoding='utf8')==data,'Preserve previous immutable picture record')
   if not path.exists():path.write_text(data,encoding='utf8')
  print(json.dumps(dict(ready=True,path=str(path),fingerprint=r['fingerprint'],motionChoices=r['selectedMotionChoices'],overrideRows=len(r['overrides']),compiledSegments=len(r['compiledSegments']),written=a.write,mediaStarted=False)))
 except(RuntimeError,AssertionError,FileNotFoundError,KeyError,ValueError)as error:
  if a.write:raise
  print(json.dumps(dict(ready=False,pending=str(error),written=False,mediaStarted=False)))
if __name__=='__main__':main()
