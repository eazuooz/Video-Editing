"""Preserve all80 scene frames/PCM; retime only measured additions at exact40:60."""
from pathlib import Path
import argparse,copy,hashlib,json,math,sys
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
sys.path.insert(0,str(ROOT/'production/batches/game-math-part2-full-series'))
from observations import observation_capacity_seconds,place_observation_pauses,mapped_time
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def stamp(t):
 h,r=divmod(round(t*1000),3600000);mi,r=divmod(r,60000);s,ms=divmod(r,1000)
 return f'{h:02}:{mi:02}:{s:02},{ms:03}'
def srt(cues):return '\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(cues,1))+'\n'
baseline=read(R/'baseline.json');timing=read(R/'combined-addition-timing.json');summary=[]
parser=argparse.ArgumentParser();parser.add_argument('--only',choices=[e['newSlug'] for e in baseline['episodes']]);parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
for e in baseline['episodes']:
 if args.only and e['newSlug']!=args.only:continue
 slug=e['newSlug'];P=ROOT/'projects'/slug;m=read(P/'project.json');lesson=read(P/'production/lesson.json')
 original=read(R/'baseline'/e['slug']/'production/lesson.json')['scenes'];oldids={s['id'] for s in original}
 assert [s for s in lesson['scenes'] if s['id'] in oldids]==original
 old=read(R/'baseline'/e['slug']/'production/timeline.json');oldslots={s['id']:s for s in old['scenes']}
 clips={s['id']:s for s in e['sceneClips']};record=next(x for x in e['media'] if x['kind']=='narration')
 original_wav=ROOT/record['path'];assert sha(original_wav)==record['sha256']
 original_audio,sr=sf.read(original_wav,dtype='float32');assert sr==24000 and original_audio.ndim==1
 rows=[];raw={};minimum={};maximum={};groups={'actual':[],'explanation':[]}
 for scene in lesson['scenes']:
  ident=scene['id'];kind=scene['kind'];groups[kind].append(ident)
  if ident in oldslots:
   base=oldslots[ident];a=original_audio[round(base['start']*sr):round((base['start']+base['seconds'])*sr)]
   assert len(a)==round(base['seconds']*sr)
   assert sha(ROOT/clips[ident]['clip'])==clips[ident]['clipSha256']
   slot=copy.deepcopy(base);slot.update(preservedOriginal=True,baselineStart=base['start'],baselineClip=clips[ident]['clip'],baselineClipSha256=clips[ident]['clipSha256'],baselineAudioSha256=record['sha256'],preservedSamplesSha256=hashlib.sha256(a.tobytes()).hexdigest())
   slot['captions']={lang:[{**c,'start':c['start']-base['start'],'end':c['end']-base['start']} for c in old[lang+'Captions'] if c['scene']==ident] for lang in ['ko','en']}
   minimum[ident]=maximum[ident]=base['frames']
  else:
   t=copy.deepcopy(timing[ident]);wav=ROOT/t['voice'];assert sha(wav)==t['voiceSha256']
   a,rate=sf.read(wav,dtype='float32');assert rate==sr and a.ndim==1
   minimum[ident]=math.ceil((len(a)/sr+.6)*60);maximum[ident]=minimum[ident]
   slot={**t,'title':scene['title'],'classification':kind,'preservedOriginal':False,'cues':[dict(start=x,end=y,line=i,text=scene['ko'][i]) for i,(x,y) in enumerate(zip(t['lineStarts'],t['lineEnds']))]}
   if kind=='actual':
    segments=copy.deepcopy(scene['sourceSegments']);assert len(segments)==len(scene['intervals'])
    for seg,(start,end) in zip(segments,scene['intervals']):
     assert seg['in']==start and abs(seg['maxSeconds']-(end-start))<1e-8
     assert sha(ROOT/seg['sourceFile'])==seg['sourceSha256']
    # In the Besiege shot, first let viewers identify the highlighted subset
    # before narration names it. This is a bounded real-time before-state
    # observation; the source keeps playing and speech samples stay exact.
    lead_limit=3 if ident in {'QF30','QC30','QC20'} else 0
    result_limit=2 if ident=='QC20' else 0
    slot['leadingObservationMaximumSeconds']=lead_limit
    slot['resultObservationMaximumSeconds']=result_limit
    if lead_limit:slot['leadingObservationReason']=('Identify the current component preview before its sideways/upright manipulation; normal source playback.' if ident=='QC20' else 'Identify the orange selected cannon subset and unchanged adjacent parts before the rotation manipulator changes their directions; normal source playback.')
    if result_limit:slot['resultObservationReason']='Inspect the actually placed upright component and its other faces at the end of the current normal-speed shot; upright does not prove identical full orientation.'
    capacity=observation_capacity_seconds(a,sr,slot['sentenceCues'])+lead_limit+result_limit
    # Ceil the minimum voice slot, allowing at most one frame of neutral tail
    # rounding when no internal observation seam exists.
    maximum[ident]=min(round(scene['maximumSeconds']*60),max(minimum[ident],math.floor(capacity*60)))
    assert minimum[ident]<=maximum[ident],f'{ident}: acquire clearer source/useful narration; preserve speech speed and old scenes'
    slot['cut']=dict(sourceId=scene['sourceId'],sourceFile=scene['sourceFile'],sourceSegments=segments,maximumSeconds=scene['maximumSeconds'],sourceAudioUsed=False,sourceSpeed=1,annotationPlan=scene['annotation'])
  rows.append(slot);raw[ident]=a
 min_actual=sum(minimum[i] for i in groups['actual']);min_explanation=sum(minimum[i] for i in groups['explanation'])
 body=math.ceil(min_explanation/3)*5;targets=dict(actual=body//5*2,explanation=body//5*3)
 maximum_actual=sum(maximum[i] for i in groups['actual'])
 print(json.dumps(dict(slug=slug,actualMinimumSeconds=min_actual/60,actualMaximumSeconds=maximum_actual/60,actualTargetSeconds=targets['actual']/60,newActualSlots=[dict(id=i,min=minimum[i]/60,max=maximum[i]/60) for i in groups['actual'] if i not in oldids])),flush=True)
 assert min_actual<=targets['actual'],'Gameplay speech needs useful explanation, never remove approved material'
 assert maximum_actual>=targets['actual'],'Secure additional clear actions/useful narration before final plan; never loop, freeze or slow source'
 frames=minimum.copy()
 for kind in groups:
  for _ in range(targets[kind]-sum(frames[i] for i in groups[kind])):
   available=[i for i in groups[kind] if i not in oldids and (kind=='explanation' or frames[i]<maximum[i])]
   assert available,'Preserve old frame/sample counts'
   ident=min(available,key=lambda i:frames[i]/minimum[i]);frames[ident]+=1
 assert sum(frames.values())==body
 if args.dry_run:continue
 voice=np.zeros(round((body/60+12)*sr),dtype='float32')
 voice[:round(2*sr)]=original_audio[:round(2*sr)]
 voice[-round(10*sr):]=original_audio[-round(10*sr):]
 start=2;captions={'ko':[],'en':[]}
 for slot in rows:
  ident=slot['id'];slot.update(start=start,frames=frames[ident],seconds=frames[ident]/60);a=raw[ident];pauses=[]
  if not slot['preservedOriginal'] and slot['classification']=='actual':
   raw_digest=hashlib.sha256(a.tobytes()).hexdigest()
   internal_capacity=observation_capacity_seconds(a,sr,slot['sentenceCues'])
   boundary_extra=max(0.,slot['seconds']-internal_capacity)
   leading=min(boundary_extra,slot.get('leadingObservationMaximumSeconds',0))
   result_observation=boundary_extra-leading
   assert leading<=slot.get('leadingObservationMaximumSeconds',0)+1/60
   assert result_observation<=slot.get('resultObservationMaximumSeconds',0)+1/60
   a,pauses,review=place_observation_pauses(a,sr,slot['sentenceCues'],slot['seconds']-leading-result_observation)
   if leading:
    count=round(leading*sr);leading=count/sr
    a=np.concatenate([np.zeros(count,dtype='float32'),a])
    pauses=[dict(rawAt=0,rawSample=0,seconds=leading,silenceSamples=count,leadingObservation=True,reason=slot['leadingObservationReason']),*pauses]
    review.update(status='leading-selected-subset-observation-plus-quiet-seams',leadingObservationSeconds=leading,rawSampleSha256=raw_digest,restoredSampleSha256=raw_digest,sourceSpeed=1,gameplayFreezeOrLoop=False)
   if result_observation:review.update(resultObservationSeconds=result_observation,resultObservationReason=slot['resultObservationReason'])
   slot['observationPauses']=pauses;slot['observationReview']=review
   slot['lineStarts']=[mapped_time(x,pauses) for x in slot['lineStarts']]
   slot['lineEnds']=[mapped_time(x,pauses) for x in slot['lineEnds']]
   slot['annotationReveal']={k:mapped_time(v,pauses) for k,v in slot['annotationReveal'].items()}
   slot['fragmentCues']={k:mapped_time(v,pauses) for k,v in slot['fragmentCues'].items()}
   slot['cues']=[{**c,'start':mapped_time(c['start'],pauses),'end':mapped_time(c['end'],pauses)} for c in slot['cues']]
   slot['sentenceCues']=[{**c,'start':mapped_time(c['start'],pauses),'end':mapped_time(c['end'],pauses)} for c in slot['sentenceCues']]
   parts=[];remaining=slot['frames']
   for seg in slot['cut']['sourceSegments']:
    count=min(remaining,round(seg['maxSeconds']*60));remaining-=count
    if count:parts.append({**seg,'frames':count,'seconds':count/60})
   assert remaining==0;slot['cut']['segments']=parts
  at=round(start*sr);assert len(a)<=round(slot['seconds']*sr);voice[at:at+len(a)]=a
  for lang in captions:
   for c in slot['captions'][lang]:captions[lang].append({**c,'start':start+mapped_time(c['start'],pauses),'end':start+mapped_time(c['end'],pauses),'scene':ident})
  start+=slot['seconds']
 assert abs(start+10-(body/60+12))<1e-8
 for lang in captions:
  assert all(a['end']<=b['start']+.004 for a,b in zip(captions[lang],captions[lang][1:]))
  (P/f'script/final.{lang}.srt').write_text(srt(captions[lang]),encoding='utf8')
 assert [(c['start'],c['end']) for c in captions['ko']]==[(c['start'],c['end']) for c in captions['en']]
 narration=ROOT/m['paths']['narration'];narration.parent.mkdir(parents=True,exist_ok=True);sf.write(narration,voice,sr)
 timeline=dict(fps=60,frames=body+720,seconds=body/60+12,bodyFrames=body,bodySeconds=body/60,actualFrames=targets['actual'],explanationFrames=targets['explanation'],actualShare=.4,explanationShare=.6,ratioErrorFrames=0,introSeconds=2,outroSeconds=10,backgroundMusic=False,sourceAudioUsed=False,scenes=rows,koCaptions=captions['ko'],enCaptions=captions['en'],baselineAudioSha256=record['sha256'],newSourcePixelAndListeningApproval=False)
 write(P/'production/timeline.json',timeline);m['video']['durationSeconds']=timeline['seconds']
 m['editing'].update(timingStatus='Measured original PCM + current-hash new speech; final pixels pending',actualGameplaySeconds=targets['actual']/60,actualExplanationSeconds=targets['explanation']/60,actualGameplayShare=.4,finalBodyFrames=dict(total=body,actual=targets['actual'],explanation=targets['explanation'],ratioErrorFrames=0))
 write(P/'project.json',m);assert sha(original_wav)==record['sha256']
 summary.append(dict(slug=slug,seconds=timeline['seconds'],originalScenesExact=len(oldids),originalPCMAndFrameCountsRetained=True,captionCount=len(captions['ko'])))
if not args.dry_run:write(R/'measured-episode-plan.json',dict(episodes=summary,finalPixelsListeningPublishing='pending'))
