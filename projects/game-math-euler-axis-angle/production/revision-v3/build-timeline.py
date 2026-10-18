"""Replace gameplay/overview only; retain reviewed explanation timing, PCM and clips."""
from pathlib import Path
import json, copy, math, importlib.util
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';HERE=Path(__file__).parent;O=P/'production/local/revision-v3'
spec=importlib.util.spec_from_file_location('v2_timing',P/'production/revision-v2/build-timeline.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read=h.read;save=h.save;sha=h.sha;rel=h.relative
CHANGED={'01','02','05','08','11','14','17','20','23'}
def build():
 h.require_selected();old=read(P/'production/revision-v2/timeline.json');m=read(HERE/'tts-manifest.json');lesson=read(HERE/'lesson.json')
 voice=R/m['tts']['outputDir'];timing_file=voice/(m['tts']['filenameStem']+'.timing.json');timing=read(timing_file)
 assert timing.get('alignment'),'Current word-aligned narration required'
 designs={s['id']:s for s in lesson['scenes']};cutplan=read(P/'sources/cut-plan-v3.json');media=read(P/'sources/media-revision-v3.json')
 source_info={s['id']:s for s in media['sources']};sources={}
 for sid,s in cutplan['sources'].items():
  src=R/s['file'];digest=sha(src);assert digest==source_info[sid]['downloadedSha256']
  sources[sid]={**s,'id':sid,'sha256':digest,'url':source_info[sid]['url'],'classification':'independent-gameplay'}
 raw={};rows=[]
 for prev in old['scenes']:
  sid=prev['id'];s=copy.deepcopy(prev)
  if sid not in CHANGED:
   for key in ['voice','placedVoice','asr']:assert sha(R/s[key])==s[key+'Sha256']
   folder='spatial' if sid in ['03','04','06','07','09','10','12','16','18','19','21','22'] else 'flat'
   f=P/f'production/local/revision-v2/{folder}/{sid}.mp4';assert f.exists();s['retainedRender']={'file':rel(f),'sha256':sha(f),'frames':s['frames'],'evidence':'v2 final review; decoded content retained'}
  else:
   d=designs[sid];entries=[e for e in timing['entries'] if e['scene_id']==sid];assert [e['text'] for e in entries]==d['ko']
   f=voice/'chunks'/f'{sid}-scene.wav';a=voice/'asr'/f'{sid}.json';pcm,sr=sf.read(f,dtype='float32');assert sr==24000 and pcm.ndim==1
   asr=read(a);assert asr['audio_sha256']==sha(f)
   origin=entries[0]['start'];s.update(title=d['title'],voice=rel(f),voiceSha256=sha(f),voiceSeconds=len(pcm)/sr,asr=rel(a),asrSha256=sha(a),rawOrigin=origin,paragraphs=entries,rawLineStarts=[e['voice_start']-origin for e in entries])
   if sid=='01':
    minimum=math.ceil((len(pcm)/sr+.6)*60)
    fixed_explanation=sum(v['frames'] for v in old['scenes'] if v['kind']=='explanation' and v['id']!='01')
    s['frames']=minimum+(-(fixed_explanation+minimum))%3
   else:
    # Pause only between complete aligned paragraphs. Never split a caption's sentence.
    h.INTERNAL_OBSERVATION_PURPOSES[sid]={};h.PARAGRAPH_OBSERVATION_PURPOSES[sid]=d['beats'][:-1]
   raw[sid]=(pcm,asr)
  rows.append(s)
 explanation=sum(s['frames'] for s in rows if s['kind']=='explanation');assert explanation%3==0
 actual=explanation*2//3;delta=actual-old['actualFrames'];next(s for s in rows if s['id']=='23')['frames']+=delta
 cursor=120;cuts=[];usage=[];obs=h.observations()
 for s in rows:
  sid=s['id'];s.update(startFrame=cursor,endFrame=cursor+s['frames'],start=cursor/60,seconds=s['frames']/60,voiceStart=cursor/60,voiceStartFrame=cursor)
  if sid in CHANGED:
   pcm,asr=raw[sid];assert len(pcm)/24000+.2<=s['seconds'],('Narration exceeds selected slot',sid,len(pcm)/24000,s['seconds'])
   if s['kind']=='actual':
    seams,review=h.sentence_observation_seams(pcm,24000,designs[sid]['ko'],asr,sid)
    placed,pauses,evidence=h.place_verified_observation_pauses(pcm,24000,seams,s['seconds'],review)
   else:placed,pauses,evidence=pcm,[],{'status':'new-overview-current-PCM','rawSamplesPreserved':True}
   s.update(observationPauses=pauses,observationReview=evidence,lineStarts=[obs.mapped_time(x,pauses) for x in s['rawLineStarts']],voicePlacedSamples=len(placed),voicePlacementSeconds=len(placed)/24000)
   f=O/'placed-voice'/f'{sid}.wav';f.parent.mkdir(parents=True,exist_ok=True);sf.write(f,placed,24000,subtype='FLOAT');s.update(placedVoice=rel(f),placedVoiceSha256=sha(f))
  if s['kind']=='actual':
   s.pop('annotationWindow',None);s.pop('sourceAllocationReview',None);cplan=cutplan['scenes'][sid];source=sources[cplan['sourceId']];local=0
   ranges=[[round(a*60),round(b*60)] for a,b in cplan['ranges']]
   if sid=='23':ranges[-1][1]+=delta;assert ranges[-1][1]<=round(cplan['lastRangeMaximumOut']*60)
   assert sum(b-a for a,b in ranges)==s['frames'],sid
   for i,(a,b) in enumerate(ranges,1):
    assert b-a>=120
    c=dict(id=f'{sid}-cut-{i:02}',scene=sid,sourceId=source['id'],sourceFile=source['file'],sourceSha256=source['sha256'],sourceStart=a/60,sourceEnd=b/60,frames=b-a,seconds=(b-a)/60,startFrame=local,globalStartFrame=cursor+local,sourceSpeed=1,kind='actual',classification='actual-existing-gameplay',sourceAudioUsed=True,purpose=cplan['purpose'],credit=source['credit'],sourceUrl=source['url'],movingReview='pending current composite')
    cuts.append(c);usage.append((source['id'],a,b));local+=b-a
   s['cuts']=[c for c in cuts if c['scene']==sid]
  cursor+=s['frames']
 for sid in sources:
  intervals=sorted((a,b) for src,a,b in usage if src==sid);assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:])),'Source reuse forbidden'
 # Retained explanation captions keep exact local text and timing. Changed scenes
 # use current ASR-aligned bilingual cues, not character-count timing.
 caps={};changed_rows={}
 origins=sorted((s['rawOrigin'],s['id']) for s in rows if s['id'] in CHANGED)
 all_origins={sid:next(e['start'] for e in timing['entries'] if e['scene_id']==sid) for sid in designs}
 for lang in ['ko','en']:
  result=[];new=[]
  for n,c in enumerate(h.read_srt(R/m['paths']['captions'+lang.title()]),1):
   sid=max((sid for sid,o in all_origins.items() if c['start']>=o-.004),key=lambda k:all_origins[k])
   if sid not in CHANGED:continue
   s=next(s for s in rows if s['id']==sid);a=c['start']-s['rawOrigin'];b=c['end']-s['rawOrigin'];assert b<=s['voiceSeconds']+.05
   # Reject a subtitle spanning an inserted observation pause; split with real
   # word alignment before this stage rather than revealing future speech.
   assert not any(a+.025<p['rawAt']<b-.025 for p in s['observationPauses']),('Caption crosses an observation seam',sid,n)
   new.append({**c,'scene':sid,'sourceCue':n,'sourceStart':c['start'],'sourceEnd':c['end'],'start':s['start']+obs.mapped_time(a,s['observationPauses']),'end':s['start']+obs.mapped_time(b,s['observationPauses'])})
  changed_rows[lang]=new
  for s in rows:
   if s['id'] in CHANGED:result.extend(c for c in new if c['scene']==s['id'])
   else:
    previous=next(v for v in old['scenes'] if v['id']==s['id']);shift=s['start']-previous['start']
    result.extend({**c,'start':c['start']+shift,'end':c['end']+shift,'retainedLocalTiming':True} for c in old[lang+'Captions'] if c['scene']==s['id'])
  result.sort(key=lambda c:c['start']);assert all(a['end']<=b['start']+.002 for a,b in zip(result,result[1:]));caps[lang]=result
 assert [(c['start'],c['end']) for c in caps['ko']]==[(c['start'],c['end']) for c in caps['en']]
 # The unchanged explanations retain their reviewed canonical spellings. Only
 # a game title pronunciation alias changes in new captions.
 for c in caps['ko']:
  if c['scene'] in CHANGED:c['text']=c['text'].replace('마리오 카트 에이트 디럭스','마리오 카트 8 디럭스')
 for lang in caps:
  for n,c in enumerate(caps[lang],1):c['finalCue']=n
  h.write_srt(O/f'captions.{lang}.srt',caps[lang])
 inputs=[HERE/'tts-manifest.json',HERE/'lesson.json',timing_file,P/'sources/cut-plan-v3.json',P/'sources/media-revision-v3.json',P/'sources/annotation-plan-v3.json',Path(__file__),P/'production/revision-v2/timeline.json',R/m['paths']['script'],R/m['paths']['scriptEn'],R/m['paths']['captionsKo'],R/m['paths']['captionsEn']]
 result={**old,'revision':'nintendo-annotated-no-bgm-v3','frames':cursor+600,'totalFrames':cursor+600,'seconds':(cursor+600)/60,'bodyFrames':actual+explanation,'actualFrames':actual,'explanationFrames':explanation,'scenes':rows,'cuts':cuts,'sources':sources,'captions':{lang:rel(O/f'captions.{lang}.srt') for lang in caps},'captionCount':len(caps['ko']),'koCaptions':caps['ko'],'enCaptions':caps['en'],'inputHashes':{rel(f):sha(f) for f in inputs},'captionDisplayReview':{'retainedExplanationCanonicalDisplay':'identical local text/time, only global shift','newGameplay':'current bilingual word alignment; canonical game title display'},'speechAndAnnotationsMovingReview':'pending','humanWholeListening':'pending','annotationWindowsLocked':False,'actualCutValidation':{'status':'passed','minimumSelectedFrames':min(c['frames'] for c in cuts),'selectedCutCount':len(cuts),'sourceIntervalsUnique':True},'retainedExplanationCount':17,'newVoiceScenes':sorted(CHANGED)}
 save(HERE/'timeline.json',result);print(json.dumps({'frames':cursor+600,'seconds':result['seconds'],'ratio':[actual,explanation],'deltaFrames':delta,'captions':len(caps['ko'])}))
if __name__=='__main__':build()
