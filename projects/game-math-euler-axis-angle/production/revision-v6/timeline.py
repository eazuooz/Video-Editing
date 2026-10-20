"""Build one measured V6 timeline; no media rendering or PCM mutation.

All original samples are retained. Motion and observation occupy a verified
complete-word gap; only the missing duration is inserted at its quiet seam.
Time fields on teachingBeats are GLOBAL, including the120-frame branding.
lineStarts/lineEnds and lines.startFrame/endFrame are SCENE-RELATIVE.
"""
from pathlib import Path
import argparse,hashlib,json,math

R=Path(__file__).resolve().parents[4]
P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6';V=O/'voice';FPS=60
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ceilf(t):return math.ceil(t*FPS-1e-8)
def floorf(t):return math.floor(t*FPS+1e-8)
def relative(p):return Path(p).as_posix()
def path_value(value):return value.get('path') if isinstance(value,dict) else value

def build():
 control=read(R/'shared/publishing/video-production-control.json')
 assert control['selectedVideo']==P.name
 ko_file=P/'script/revision-v6-article-flow/narration.ko.json'
 ko=read(ko_file);alignment=read(V/'voice-alignment.json')
 assert alignment['inputs']['koSha256']==sha(ko_file),'Stale measured alignment'
 current_file=V/'current-pcm.json';current_pcm=read(current_file)
 assert current_pcm['status']=='current41-ready-for-word-alignment'
 assert alignment['inputs']['currentPcmMappingSha256']==sha(current_file),'Measured alignment must use the currently selected41 PCM sources'
 assert alignment['inputs']['timingAliasesSha256']==sha(H/'voice-normalize.py'),'Stale word/character timing normalization'
 extra_file=H/'voice-extra-visuals.json';extra=read(extra_file)['visuals'] if extra_file.exists() else []
 assert alignment['inputs'].get('extraVisualsSha256')==(sha(extra_file) if extra_file.exists() else None)
 breathing_file=H/'voice-breathing-plan.json'
 assert alignment['inputs'].get('breathingPlanSha256')==(sha(breathing_file) if breathing_file.exists() else None)
 extra_by={x['id']:x for x in extra}
 assert len(ko['scenes'])==len(alignment['scenes'])==41
 assert not alignment['pendingSeams'],'Resolve actual word/PCM evidence; never invent a seam'
 spatial=read(H/'spatial-plan.json');screen=read(H/'screen-plan.json');footage=read(H/'footage-plan.json')
 assert screen['scriptSha256']==sha(ko_file),'Screen plan must match the current complete narration'
 spatial_by={b['id']:b for s in spatial['scenes'] for b in s['beats']}
 spatial_aux={b['id']:b for b in spatial.get('auxiliaryClips',[])}
 screen_by={b['id']:b for s in screen['scenes'] for b in s['beats']}
 screen_scene={s['id']:s for s in screen['scenes']}
 actual_by={c['beatId']:c for c in footage['clips']}
 native_file=O/'footage/finite-clips/finite-assets.json';native=read(native_file)
 native_by={c['id']:c for c in native['clips']}
 math_outputs=read(O/'math/outputs.json')
 math_by={c['id']:c for c in math_outputs['outputs']}
 assert len(math_by)==len(math_outputs['outputs'])==54,'One current finite receipt per mathematical beat'
 assert sum(b['renderer']=='Unity' for b in spatial_by.values())==48
 assert len(actual_by)==len(native_by)==4
 approved_ids={b['id'] for s in ko['scenes'] for b in s['teachingBeats']}
 assert approved_ids==set(spatial_by)==set(screen_by)
 assert set(math_by)=={k for k,b in spatial_by.items() if b['renderer']=='root-2D'}
 scenes=[];cuts=[];auxiliary_all=[];current=120;hold_total=0;motion_total=0;insert_total=0;auxiliary_hold_total=0;auxiliary_motion_total=0;breathing_total=0;breathing_count=0
 prior_picture=None
 for index,(scene,measured) in enumerate(zip(ko['scenes'],alignment['scenes'])):
  sid=scene['id'];assert sid==measured['id'];rate=measured['sampleRate'];n=measured['samples']
  assert rate==24000,'Sample-exact timeline currently requires approved24kHz PCM'
  assert sha(R/measured['wav'])==measured['wavSha256']
  events=[];beats=[];auxiliaries=[];seen_seams=set()
  # Sparse prerequisite/numeric breaths are loaded before visual placement so
  # every subsequent global beat accounts for them. Unverified candidates are
  # retained in the review report, never replaced with guessed sample offsets.
  for breath in measured.get('selectiveBreathing',[]):
   if breath['status']!='verified-selective-breathing-candidate' or breath['insertFrames']<=0:continue
   seam=breath['observedSeam'];sample=seam['sampleOffset'];low,high=breath['wordGap']
   assert low<=sample/rate<=high and sample not in seen_seams
   frames=int(breath['insertFrames']);assert 0<frames<=math.floor(breath['maximumInsertedSeconds']*FPS+1e-8)
   events.append(dict(beat=breath['id'],selectiveBreathing=True,line=breath['line'],sourceSample=sample,sourceSeconds=sample/rate,
    insertFrames=frames,insertSamples=frames*(rate//FPS),originalWordGap=[low,high],quietEvidence=seam,reason=breath['reason']))
   seen_seams.add(sample);insert_total+=frames;breathing_total+=frames;breathing_count+=1
  def mapped_seconds(raw,include_equal=True):
   sample=round(raw*rate)
   added=sum(x['insertFrames'] for x in events if x['sourceSample']<sample or (include_equal and x['sourceSample']==sample))
   return raw+added/FPS
  for scripted,observed in zip(scene['teachingBeats'],measured['beats']):
   bid=scripted['id'];assert bid==observed['id']
   seam=observed['observedSeam'];assert seam and observed['wordGap']
   seam_sample=seam['sampleOffset'];assert seam_sample not in seen_seams
   seen_seams.add(seam_sample);low,high=observed['wordGap']
   assert low<=seam_sample/rate<=high
   routing=spatial_by[bid];display=screen_by[bid]
   if bid in actual_by:
    kind='actual';clip=actual_by[bid];motion=clip['frames'];renderer='independent-gameplay'
    native_clip=native_by[clip['id']];assert native_clip['frames']==motion and native_clip['sourceFrameStart']==clip['sourceFrameStart']
    clip_file=native_clip['videoFile'];assert sha(R/clip_file)==native_clip['videoSha256']
    first=path_value(clip['firstFrame']);last=path_value(clip['lastFrame'])
    source_kind='independent-gameplay; verified source image-space editorial guidance'
    receipt=None
   elif routing['renderer']=='Unity':
    kind='explanation';clip=routing;motion=int(clip['durationFrames']);renderer='Unity'
    clip_file=clip['clipFile'];first=clip['firstFrame'];last=clip['lastFrame']
    source_kind=clip['measurementKind'];receipt=None
   else:
    kind='explanation';assert bid in math_by,f'Finite math receipt missing:{bid}'
    clip=math_by[bid];motion=int(clip['durationFrames']);renderer='Manim'
    clip_file=clip['clipFile'];first=clip['firstFrame'];last=clip['lastFrame']
    source_kind=clip['sourceKind'];receipt=sha(O/'math'/bid/'output.json')
    assert (R/clip_file).exists(),f'Math receipt media missing:{bid}'
   assert motion>0
   hold=round(scripted['hold']['plannedSeconds']*FPS);hold_total+=hold;motion_total+=motion
   # The motion begins after the full approved speech, before the existing
   # quiet gap. Account for earlier inserted pauses in this same scene.
   visual_start=ceilf(mapped_seconds(low));next_speech=floorf(mapped_seconds(high))
   needed=max(0,visual_start+motion+hold-next_speech)
   event=dict(beat=bid,sourceSample=seam_sample,sourceSeconds=seam_sample/rate,
    insertFrames=needed,insertSamples=needed*(rate//FPS),
    originalWordGap=[low,high],quietEvidence=seam)
   events.append(event);insert_total+=needed
   end=visual_start+motion;hold_end=end+hold
   assert floorf(mapped_seconds(high))>=hold_end
   global_start=current+visual_start
   beat=dict(id=bid,kind=kind,renderer=renderer,sourceKind=source_kind,
    speechLines=scripted['speech']['lineNumbers'],resultCheckLines=scripted['resultCheckAndConnection']['lineNumbers'],
    afterLine=scripted['visual']['afterLine'],visualStartFrame=global_start,
    visualEndFrame=current+end,holdEndFrame=current+hold_end,
    visualFrames=motion,holdFrames=hold,clipFile=clip_file,firstFrame=first,lastFrame=last,
    durationSource=('verified-native-gameplay-range' if kind=='actual' else 'finite-math-render-receipt' if renderer=='Manim' else 'finite-spatial-capture-budget'),
    motionReceiptSha256=receipt,observationPurpose=scripted['hold']['purpose'],
    existingQuietSeconds=high-low,insertedQuietFrames=needed,
    activeMotionLoop=False,sourceSpeed=1,answerRevealPendingConfirmation=bid in ['v6-41.B02','v6-41.B03'])
   if kind=='actual':
    cut=dict(id=clip['id'],scene=sid,beat=bid,sourceId=clip['sourceId'],sourceFile=clip['sourceFile'],
     sourceStart=clip['sourceIn'],sourceEndExclusive=clip['sourceOutExclusive'],sourceFrameStart=clip['sourceFrameStart'],
     frames=motion,startFrame=visual_start,globalStartFrame=global_start,sourceSpeed=1,
     annotation=clip['annotation'],audioSource=clip['audioSource'],firstFrame=first,lastFrame=last)
    cuts.append(cut);beat['cutId']=clip['id']
   for key in ['visualStart','visualEnd','holdEnd']:beat[key]=beat[key+'Frame']/FPS
   beats.append(beat)
  for observed in measured.get('auxiliaryVisuals',[]):
   aid=observed['id'];scripted=extra_by[aid];route=spatial_aux[aid]
   # Current explicit auxiliary is after all primary motions in scene41.
   # A future mid-scene auxiliary requires an intentionally interleaved plan.
   assert sid==scripted['sceneId']=='v6-41' and scripted['afterLine']==6
   seam=observed['observedSeam'];assert seam and observed['wordGap']
   sample=seam['sampleOffset'];assert sample>max(seen_seams);seen_seams.add(sample)
   low,high=observed['wordGap'];assert low<=sample/rate<=high
   motion=int(route['durationFrames']);hold=round(scripted['hold']['plannedSeconds']*FPS)
   assert motion==scripted['visual']['durationFrames']==180 and hold==240
   start=ceilf(mapped_seconds(low));next_speech=floorf(mapped_seconds(high));needed=max(0,start+motion+hold-next_speech)
   events.append(dict(beat=aid,auxiliary=True,sourceSample=sample,sourceSeconds=sample/rate,insertFrames=needed,insertSamples=needed*(rate//FPS),originalWordGap=[low,high],quietEvidence=seam))
   insert_total+=needed;auxiliary_hold_total+=hold;auxiliary_motion_total+=motion
   assert floorf(mapped_seconds(high))>=start+motion+hold
   auxiliary=dict(id=aid,sceneId=sid,afterLine=6,kind='explanation',renderer='Unity',sourceKind='authored auxiliary answer-confirmation motion; no new narration',
    speechLines=[6],resultCheckLines=[7,8],visualStartFrame=current+start,visualEndFrame=current+start+motion,holdEndFrame=current+start+motion+hold,
    visualFrames=motion,holdFrames=hold,clipFile=route['clipFile'],firstFrame=route['firstFrame'],lastFrame=route['lastFrame'],
    existingQuietSeconds=high-low,insertedQuietFrames=needed,sourceSpeed=1,activeMotionLoop=False)
   for key in ['visualStart','visualEnd','holdEnd']:auxiliary[key]=auxiliary[key+'Frame']/FPS
   auxiliaries.append(auxiliary)
  events.sort(key=lambda x:x['sourceSample'])
  assert all(a['sourceSample']<b['sourceSample'] for a,b in zip(events,events[1:]))
  lines=[]
  for line in measured['lines']:
   start=mapped_seconds(line['rawStart']);end=mapped_seconds(line['rawEnd'])
   assert end>=start
   lines.append(dict(line=line['line'],rawStart=line['rawStart'],rawEnd=line['rawEnd'],
    start=start,end=end,startFrame=floorf(start),endFrame=ceilf(end)))
  for b in beats:
   speech=[lines[i-1] for i in b['speechLines']]
   b.update(speechStart=current/FPS+speech[0]['start'],speechEnd=current/FPS+speech[-1]['end'],
    speechStartFrame=current+floorf(speech[0]['start']),speechEndFrame=current+ceilf(speech[-1]['end']))
   checks=b['resultCheckLines'];following=b['afterLine']+1
   confirmation=lines[checks[0]-1]['start'] if checks else (lines[following-1]['start'] if following<=len(lines) else None)
   b['confirmationStart']=None if confirmation is None else current/FPS+confirmation
   b['confirmationStartFrame']=None if confirmation is None else current+floorf(confirmation)
   if confirmation is not None:assert b['confirmationStartFrame']>=b['holdEndFrame']
  for b in auxiliaries:
   speech=lines[b['afterLine']-1];confirmation=lines[b['afterLine']]['start']
   b.update(speechStart=current/FPS+speech['start'],speechEnd=current/FPS+speech['end'],speechStartFrame=current+floorf(speech['start']),speechEndFrame=current+ceilf(speech['end']),
    confirmationStart=current/FPS+confirmation,confirmationStartFrame=current+floorf(confirmation))
   assert b['confirmationStartFrame']>=b['holdEndFrame'];auxiliary_all.append(b)
  inserted=sum(x['insertFrames'] for x in events)
  body_frames=ceilf(n/rate)+inserted
  # Scene boundaries receive only the missing part of the approved0.72s
  # total natural join; source head/tail samples are never trimmed.
  last_end=measured['lines'][-1]['rawEnd'];tail=max(0,n/rate-last_end)
  next_head=alignment['scenes'][index+1]['lines'][0]['rawStart'] if index+1<len(alignment['scenes']) else 0
  missing_join=max(0,.72-tail-next_head) if index+1<len(alignment['scenes']) else 0
  join_frames=ceilf(missing_join);frames=max(body_frames,max(b['holdEndFrame']-current for b in [*beats,*auxiliaries]))+join_frames
  segments=[];source=0;destination=0
  for event in events:
   end_sample=event['sourceSample'];assert end_sample>=source
   if end_sample>source:
    segments.append(dict(sourceSampleStart=source,sourceSampleEnd=end_sample,destinationSampleStart=destination,rate=rate))
   destination+=end_sample-source+event['insertSamples'];source=end_sample
  if source<n:segments.append(dict(sourceSampleStart=source,sourceSampleEnd=n,destinationSampleStart=destination,rate=rate))
  assert sum(x['sourceSampleEnd']-x['sourceSampleStart'] for x in segments)==n
  unity_first=next((b['firstFrame'] for b in beats if b['renderer']=='Unity'),None)
  base=unity_first or prior_picture
  assert base,'Every scene requires an inherited or own same-testbed first state'
  for b in beats:
   if b['renderer']=='Unity':prior_picture=b['lastFrame']
  info=screen_scene[sid]
  row=dict(id=sid,title=scene['title'],kind='mixed' if any(b['kind']=='actual' for b in beats) else 'explanation',
   sourceKind=info.get('pictureLabel','authored illustrative mathematical explanation'),
   firstFrame=base,pictureFirstState=base,startFrame=current,endFrame=current+frames,frames=frames,seconds=frames/FPS,
   rawVoiceFile=measured['wav'],rawVoiceSha256=measured['wavSha256'],rawVoiceSamples=n,sampleRate=rate,rawAsrFile=measured['asrFile'],rawAsrSha256=measured['asrSha256'],
   lineStarts=[x['start'] for x in lines],lineEnds=[x['end'] for x in lines],lines=lines,
   voiceSegments=segments,pauseInsertions=events,teachingBeats=beats,auxiliaryVisuals=auxiliaries,
   naturalTailSeconds=tail,nextNaturalHeadSeconds=next_head,addedSceneJoinFrames=join_frames,
   paddingFrames=frames-body_frames,selectiveBreathing=measured.get('selectiveBreathing',[]),humanPaceListening='pending')
  scenes.append(row);current+=frames
 assert len(scenes)==41 and sum(len(s['lines']) for s in scenes)==250
 assert sum(len(s['teachingBeats']) for s in scenes)==106
 assert hold_total==527*FPS,'Preserve all planned527s observation holds'
 assert len(auxiliary_all)==1 and auxiliary_hold_total==4*FPS,'Explicit answer-confirmation adds only4s observation'
 assert sum(c['frames'] for c in cuts)==1074
 for a,b in zip(cuts,cuts[1:]):assert a['globalStartFrame']+a['frames']<=b['globalStartFrame']
 return dict(schemaVersion=1,revision='article-flow-v6',slug=P.name,timing='measured-and-asr-aligned',status='measured-source-timing-finite-motion-ready; rendered/moving/audio/human review pending',
  fps=FPS,width=1920,height=1080,introFrames=120,outroFrames=600,bodyFrames=current-120,totalFrames=current+600,seconds=(current+600)/FPS,
  temporalContract=dict(beatTimes='global final-video seconds including2s branding',beatFrames='global final-video frames',lineStarts='scene-relative seconds',lineEnds='scene-relative seconds',lineFrames='scene-relative frames',voiceDestinationSamples='scene-relative at original sampleRate',outroStartFrame=current),
  inputs=dict(koSha256=sha(ko_file),alignmentSha256=sha(V/'voice-alignment.json'),currentPcmMappingSha256=sha(current_file),timingAliasesSha256=sha(H/'voice-normalize.py'),extraVisualsSha256=sha(extra_file),breathingPlanSha256=sha(breathing_file) if breathing_file.exists() else None,spatialPlanSha256=sha(H/'spatial-plan.json'),screenPlanSha256=sha(H/'screen-plan.json'),footagePlanSha256=sha(H/'footage-plan.json'),nativeGameAssetsSha256=sha(native_file),mathOutputsSha256=sha(O/'math/outputs.json'),implementationSha256=sha(Path(__file__))),
  scenes=scenes,cuts=cuts,sceneCount=41,lineCount=250,beatCount=106,
  plannedHoldFrames=hold_total,primaryHoldFrames=hold_total,auxiliaryHoldFrames=auxiliary_hold_total,totalHoldFrames=hold_total+auxiliary_hold_total,
  primaryFiniteMotionFrames=motion_total,auxiliaryFiniteMotionFrames=auxiliary_motion_total,finiteMotionFrames=motion_total+auxiliary_motion_total,auxiliaryVisuals=auxiliary_all,insertedPauseFrames=insert_total,
  selectiveBreathingFrames=breathing_total,selectiveBreathingCount=breathing_count,pendingBreathing=alignment.get('pendingBreathing',[]),
  actualFrames=sum(c['frames'] for c in cuts),explanationFrames=current-120-sum(c['frames'] for c in cuts),actualExplanationRatioEnforced=False,
  ratioPolicy='lecture-concept-sized-game-examples-v1; each observed game operation once, no padding quota',
  originalPcmPreserved=True,sourceSpeed=1,gameAudioPolicy='lecture-no-added-bgm-standard-game-audio-v3',humanWholeListening='pending')

def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=H/'timeline.json');args=a.parse_args()
 plan=build();save(args.output,plan)
 print('Measured timeline:',plan['sceneCount'],'scenes',plan['beatCount'],'beats',plan['totalFrames'],'frames;',plan['plannedHoldFrames']/60,'s observation retained')
if __name__=='__main__':main()
