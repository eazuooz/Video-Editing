"""Bind the complete V8 bilingual clause plan to measured source speech.

--plan-only checks source identity, source offsets, complete paragraph coverage,
atomic normalized numbers and approved48px geometry without requiring audio.
--build reads the actual timing.Clock after source-alignment/timeline exist.
No narration, PCM, speech speed, source alignment or font size is modified.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,math
from PIL import ImageFont

H=Path(__file__).resolve().parent
def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
c=load_module('v8_captions_common',H/'common.py')
N=load_module('v8_captions_normalizer',H/'voice-normalize.py').normalized
FOLDER=c.O/'captions'
GEOM_PATH=c.P/'production/revision-v6/captions.py'
def evidence(path):return dict(file=c.rel(path),sha256=c.sha(path))
def source_inputs():
 return dict(captionPlan=evidence(H/'caption-plan.json'),implementation=evidence(Path(__file__)),
   approvedGeometry=evidence(GEOM_PATH),normalizer=evidence(H/'voice-normalize.py'),
   sourceKo=evidence(c.S/'narration.ko.json'),sourceEnCompanion=evidence(c.S/'narration.en.json'))
def verify_plan():
 c.authorized();plan=c.read(H/'caption-plan.json');ko=c.read(c.S/'narration.ko.json')
 assert plan['inputs']['koSha256']==c.sha(c.S/'narration.ko.json')
 assert plan['inputs']['enSha256']==c.sha(c.S/'narration.en.json')
 assert plan['inputs']['normalizerSha256']==c.sha(H/'voice-normalize.py')
 assert plan['inputs']['designSha256']==c.sha(H/'caption-design.py')
 assert plan['inputs']['approvedGeometrySha256']==c.sha(GEOM_PATH)
 assert plan['sceneCount']==13 and plan['paragraphCount']==76 and len(plan['cues'])==475
 assert not plan['layoutNeeds'] and plan['sourceKoUnchanged'] and plan['sourceEnCompanionUnchanged']
 by={};ids=set();geometry=load_module('v8_captions_geometry',GEOM_PATH);design=load_module('v8_captions_design_wrap',H/'caption-design.py')
 font=ImageFont.truetype(str(geometry.FONT),48);bold=ImageFont.truetype(str(geometry.BOLD),48)
 for row in plan['cues']:
  assert row['id'] not in ids;ids.add(row['id']);key=(row['scene'],row['line']);by.setdefault(key,[]).append(row)
  for language in ('ko','en'):
   lines=design.caption_lines(geometry,row[language],font,bold,row['emphasis'+language.title()],language)
   assert lines==row[language+'Lines'] and 1<=len(lines)<=2
   assert not any(ch in row[language] for ch in ('{','}','\\')),'Plain caption text must not inject ASS markup'
   span=row['emphasis'+language.title()]
   assert not span or 0<=span['start']<span['end']<=len(row[language])
 coverage=[]
 for scene in ko['scenes']:
  for line,text in enumerate(scene['paragraphs'],1):
   rows=by[(scene['id'],line)];assert ' '.join(row['sourceKo'] for row in rows)==text
   count=0
   for row in rows:
    a,b=row['sourceKoOffset'],row['sourceKoEnd'];assert text[a:b]==row['sourceKo']
    lo,hi=len(N(text[:a])),len(N(text[:b]))
    assert lo==count and 0<=lo<hi<=len(N(text))
    assert N(text[:a])+N(row['sourceKo'])==N(text[:b])
    assert N(text[:b])+N(text[b:])==N(text)
    assert row['normalizedSourceOffset']==lo and row['normalizedSourceEnd']==hi
    count=hi
   assert count==len(N(text))
   para=next(p for p in plan['paragraphs'] if p['scene']==scene['id'] and p['line']==line)
   assert ' '.join(row['sourceEn'] for row in rows)==para['captionEnglish']
   coverage.append(dict(paragraphId=f'{scene["id"]}.L{line:02}',scene=scene['id'],line=line,cueIds=[r['id'] for r in rows],
       sourceKoUnicodeCharacters=len(text),normalizedCharacters=count,sourceKoFullyCovered=True,captionEnglishFullyCovered=True))
 assert len(coverage)==76 and set(by)=={(p['scene'],p['line']) for p in coverage}
 return plan,coverage,geometry
def planned_manifest(plan,coverage):
 return dict(schemaVersion=1,revision='orientation-matrix-v8',status='plan-validated-awaiting-measured-source-alignment',
   inputs=source_inputs(),sceneCount=13,paragraphCount=76,cueCount=475,geometry=plan['geometry'],font=plan['font'],
   sourceKoUnchanged=True,sourceEnCompanionUnchanged=True,sourceAudioUnchanged=True,addedSilenceFrames=0,
   intendedOutputs=dict(fullKoSrt=c.rel(FOLDER/'full/captions.ko.srt'),fullEnSrt=c.rel(FOLDER/'full/captions.en.srt'),
     fullKoASS=c.rel(FOLDER/'full/captions.ko.ass'),captionsJson=c.rel(FOLDER/'captions.json'),
     sceneASSDirectory=c.rel(FOLDER/'scenes'),paragraphASSDirectory=c.rel(FOLDER/'paragraphs')),
   outputsCreated=False,paragraphCoverage=coverage,sceneASS={},paragraphASS={},
   waitingFor=[c.rel(c.O/'audio/source-alignment.json'),c.rel(H/'timeline.json')],
   nativePixelReview='pending actual encoded output',mobileMovingReview='pending',humanWholeListening='pending')
def frame_centiseconds(seconds):
 # ASS has only0.01s precision; flooring the exact60fps edge makes the
 # first active image F, not F+1. Keep the original box geometry untouched.
 value=math.floor(seconds*100+1e-7);hours,value=divmod(value,360000);minutes,value=divmod(value,6000);sec,cs=divmod(value,100)
 return f'{hours}:{minutes:02}:{sec:02}.{cs:02}'
def write_ass(geometry,path,rows,origin_frame):
 path.parent.mkdir(parents=True,exist_ok=True);local=[]
 for row in rows:
  x=copy.deepcopy(row)
  x['start']=(row['startFrame']-origin_frame)/60;x['end']=(row['endFrame']-origin_frame)/60
  assert 0<=x['start']<x['end'];local.append(x)
 geometry.O=path.parent;geometry.ass_time=frame_centiseconds
 result=geometry.ass(local,'ko');generated=path.parent/'captions.ko.ass'
 if generated!=path:generated.replace(path)
 return result
def write_srt(geometry,path,rows,language):
 text='\n\n'.join(str(i)+'\n'+geometry.timestamp(row['start'])+' --> '+geometry.timestamp(row['end'])+'\n'+'\n'.join(row[language+'Lines']) for i,row in enumerate(rows,1))+'\n'
 assert '\\' not in text and '{' not in text and '}' not in text
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf8')
def build(plan,coverage,geometry):
 assert (c.O/'audio/source-alignment.json').exists() and (H/'timeline.json').exists(),'Run --plan-only until root provides actual source alignment and timeline'
 timing=load_module('v8_caption_actual_clock',H/'timing.py');clock=timing.Clock()
 assert clock.timeline['inputs']['koSha256']==c.sha(c.S/'narration.ko.json')
 assert clock.timeline['inputs']['enSha256']==c.sha(c.S/'narration.en.json')
 rows=[];short=[];density=[];overlaps=[];counts={};previous=None
 for source in plan['cues']:
  row=copy.deepcopy(source);sid,line=row['scene'],row['line'];a,b=row['sourceKoOffset'],row['sourceKoEnd']
  text=clock.script[sid]['paragraphs'][line-1];data=clock.raw[sid]['lines'][line-1]
  assert text[a:b]==row['sourceKo']
  lo,hi=len(N(text[:a])),len(N(text[:b]));assert lo==counts.get((sid,line),0) and hi-lo==len(N(row['sourceKo']))
  assert hi<=len(data['characterStarts'])==len(data['characterEnds'])
  start=clock.word(sid,line,a);end=clock.word(sid,line,b,True)
  start_frame=clock.frame(sid,line,a);end_frame=clock.frame(sid,line,b,True)
  assert end>start and end_frame>start_frame,(row['id'],'Zero/reversed current cue needs source timing review',start,end)
  if previous and (start<previous['end']-1/24000 or start_frame<previous['endFrame']):
   overlaps.append(dict(before=previous['id'],after=row['id'],beforeEnd=previous['end'],afterStart=start,beforeEndFrame=previous['endFrame'],afterStartFrame=start_frame))
  raw_start=start-clock.scenes[sid]['start'];raw_end=end-clock.scenes[sid]['start']
  duration=end-start;reading={lang:len(row[lang].replace(' ',''))/duration for lang in ('ko','en')}
  row.update(start=round(start,8),end=round(end,8),startFrame=start_frame,endFrame=end_frame,endFrameExclusive=end_frame,
      rawStart=round(raw_start,8),rawEnd=round(raw_end,8),duration=duration,renderedDurationFrames=end_frame-start_frame,
      readingCharactersPerSecond=reading,assClock='60fps-rounded word edges, centisecond floor; first active frame stays exact',
      nativePixelReview='pending actual encoded output',mobileMovingReview='pending',humanPaceListening='pending')
  if duration<.7:short.append(dict(id=row['id'],scene=sid,line=line,duration=duration,frames=end_frame-start_frame,ko=row['ko'],en=row['en'],sourceKoOffset=a,sourceKoEnd=b,
      reason='Measured cue shorter than0.7s; inspect actual speech/context, do not inflate voice, shrink text or silently drop it.'))
  if reading['ko']>20 or reading['en']>24:density.append(dict(id=row['id'],duration=duration,charactersPerSecond=reading,ko=row['ko'],en=row['en']))
  rows.append(row);previous=row;counts[(sid,line)]=hi
 assert not overlaps,('Overlapping exact word cues need root timing review',overlaps[:5])
 for key in coverage:
  text=clock.script[key['scene']]['paragraphs'][key['line']-1];assert counts[(key['scene'],key['line'])]==len(N(text))
 FOLDER.mkdir(parents=True,exist_ok=True)
 full=FOLDER/'full'
 for lang in ('ko','en'):write_srt(geometry,full/f'captions.{lang}.srt',rows,lang)
 full_geometry=write_ass(geometry,full/'captions.ko.ass',rows,0)
 c.save(FOLDER/'geometry.ko.json',dict(style='boxed-white-forest-v1',rows=full_geometry,font=plan['font'],pixelReview='pending actual current encoded output'))
 scene_ass={};paragraph_ass={}
 for sid,s in clock.scenes.items():
  selected=[x for x in rows if x['scene']==sid]
  assert all(s['startFrame']<=x['startFrame']<x['endFrame']<=s['endFrame'] for x in selected)
  path=FOLDER/'scenes'/sid/'captions.ko.ass';write_ass(geometry,path,selected,s['startFrame'])
  scene_ass[sid]=dict(evidence(path),startFrame=s['startFrame'],endFrame=s['endFrame'],cueCount=len(selected),timeBase='scene-relative60fps')
  for i in range(1,len(s['lines'])+1):
   a,b=clock.paragraph(sid,i);part=[x for x in selected if x['line']==i]
   assert all(a<=x['startFrame']<x['endFrame']<=b for x in part),(sid,i,'caption crosses exact paragraph output cut')
   path=FOLDER/'paragraphs'/f'{sid}-L{i:02}.ass';write_ass(geometry,path,part,a)
   paragraph_ass[f'{sid}.L{i:02}']=dict(evidence(path),startFrame=a,endFrame=b,cueCount=len(part),timeBase='paragraph-relative60fps; origin Clock.paragraph')
 report=dict(schemaVersion=1,revision='orientation-matrix-v8',fps=60,sceneCount=13,paragraphCount=76,cueCount=len(rows),
    inputs=dict(source_inputs(),timeline=evidence(H/'timeline.json'),alignment=evidence(c.O/'audio/source-alignment.json'),clockImplementation=evidence(H/'timing.py')),
    cues=rows,paragraphCoverage=coverage,identicalBilingualSemanticTimes=True,noSourceTextDeletion=True,
    paceFlags=dict(shortCues=short,denseCues=density,unresolvedZeroOrOverlapCues=overlaps),
    subtitleTimes='Measured raw source-word seconds; bilingual SRT identical times. KO ASS uses exact output frame edges floored to centiseconds.',
    pixelReview='pending current encoded output',humanWholeListening='pending',sourceAudioUnchanged=True)
 c.save(FOLDER/'captions.json',report)
 timing_review=dict(schemaVersion=1,status='measured-captions-built;actual-pacing-review-pending',shortCueThresholdSeconds=.7,
    denseCueThreshold=dict(koCharactersPerSecond=20,enCharactersPerSecond=24),shortCues=short,denseCues=density,
    overlapIssues=overlaps,sourceKoCoverageComplete=True,englishCaptionCoverageComplete=True,
    unchangedVoice=True,noAutomaticTextShrink=True,noAutomaticSpeedChange=True,noAutomaticAddedSilence=True,
    currentEncodedNativeAndMobileReview='pending',humanPaceListening='pending')
 c.save(FOLDER/'timing-review.json',timing_review)
 manifest=dict(schemaVersion=1,revision='orientation-matrix-v8',status='measured-captions-built-with-pacing-flags' if short or density else 'measured-captions-built',
    inputs=report['inputs'],sceneCount=13,paragraphCount=76,cueCount=475,fps=60,geometry=plan['geometry'],font=plan['font'],
    full=dict(koSrt=evidence(full/'captions.ko.srt'),enSrt=evidence(full/'captions.en.srt'),koASS=evidence(full/'captions.ko.ass')),
    captions=evidence(FOLDER/'captions.json'),geometryReport=evidence(FOLDER/'geometry.ko.json'),timingReview=evidence(FOLDER/'timing-review.json'),
    sceneASS=scene_ass,paragraphASS=paragraph_ass,shortCueCount=len(short),denseCueCount=len(density),
    sourceKoUnchanged=True,sourceEnCompanionUnchanged=True,sourceAudioUnchanged=True,addedSilenceFrames=0,
    nativePixelReview='pending actual encoded output',mobileMovingReview='pending',humanWholeListening='pending')
 c.save(H/'captions-manifest.json',manifest)
 print(json.dumps(dict(cues=len(rows),paragraphASS=len(paragraph_ass),sceneASS=len(scene_ass),shortCues=len(short),denseCues=len(density),manifest=c.rel(H/'captions-manifest.json')),ensure_ascii=False))
def main():
 ap=argparse.ArgumentParser(description=__doc__);group=ap.add_mutually_exclusive_group(required=True)
 group.add_argument('--plan-only',action='store_true');group.add_argument('--build',action='store_true');args=ap.parse_args()
 plan,coverage,geometry=verify_plan()
 if args.plan_only:
  result=planned_manifest(plan,coverage);c.save(FOLDER/'plan-validation.json',result)
  # Never replace an actual timed manifest with the untimed preflight report.
  if not (H/'captions-manifest.json').exists():c.save(H/'captions-manifest.json',result)
  print(json.dumps(dict(status=result['status'],paragraphs=76,cues=475,sourceAudioUsed=False),ensure_ascii=False))
 else:build(plan,coverage,geometry)
if __name__=='__main__':main()
