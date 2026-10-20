"""CPU raw line timing and safe106-beat+explicit auxiliary seams; never edit PCM.

Run after the one current source-ASR batch. Unmatched/unsafe seams stay pending;
the edit timeline must not invent a timing or cut a word to fit a planned hold.
"""
from pathlib import Path
import hashlib,json,math,runpy,sys
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v6/voice'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def quiet_seam(samples,rate,low,high):
 n=round(rate*.08);a=max(0,math.ceil(low*rate));b=min(len(samples),math.floor(high*rate))
 if b-a<n:return None
 reference=float(np.sqrt(np.mean(np.asarray(samples,dtype=np.float64)**2)))
 options=[]
 for start in range(a,b-n+1,max(1,round(rate*.005))):
  window=samples[start:start+n];rms=float(np.sqrt(np.mean(np.asarray(window,dtype=np.float64)**2)));peak=float(np.max(np.abs(window)))
  if rms<=min(.01,max(reference*.08,1e-6)) and peak<=min(.04,max(reference*.30,1e-5)):
   mid=start+n//2;left=max(start,mid-round(rate*.005));right=min(start+n,mid+round(rate*.005))
   crossing=left+int(np.argmin(np.abs(samples[left:right])))
   options.append((rms,abs(crossing/rate-(low+high)/2),crossing,peak,start))
 if not options:return None
 rms,_,sample,peak,start=min(options)
 return dict(sampleOffset=sample,rawSeconds=sample/rate,quietWindowSamples=[start,start+n],quietRms=rms,quietPeak=peak,minimumQuietSeconds=.08)
def main():
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 plan=read(H/'voice-plan.json');script=read(P/'script/revision-v6-article-flow/narration.ko.json');input_script=read(H/'voice-input.ko.json')
 extra_file=H/'voice-extra-visuals.json';extra=read(extra_file)['visuals'] if extra_file.exists() else []
 breathing_file=H/'voice-breathing-plan.json';breathing_plan=read(breathing_file) if breathing_file.exists() else {}
 if breathing_plan:assert breathing_plan['koSha256']==sha(P/'script/revision-v6-article-flow/narration.ko.json')
 assert sha(P/'script/revision-v6-article-flow/narration.ko.json')==plan['inputs']['koSha256'],'Current script changed; refresh CPU voice preparation without replacing PCM'
 # Install only existing math text normalization; the historical batch's main
 # never executes and no generic alignment/source/ASR script is modified.
 old_argv=sys.argv[:];sys.argv=[sys.argv[0],P.name]
 try:helpers=runpy.run_path(str(R/'production/batches/game-math-part2-full-series/align.py'),run_name='v6_math_alignment_helpers')
 finally:sys.argv=old_argv
 align=helpers['a'];normalize=helpers['normalized'];scenes=[];pending=[]
 for scene,spoken,planned in zip(script['scenes'],input_script['scenes'],plan['scenes']):
  sid=scene['id'];assert sid==spoken['id']==planned['id'];wav=O/'chunks'/f'{sid}-scene.wav';cached=read(O/'asr'/f'{sid}.json')
  assert sha(wav)==cached['audio_sha256'],'ASR is stale; no substitute timestamps'
  samples,rate=sf.read(wav,dtype='float32',always_2d=True);mono=samples.mean(axis=1);duration=len(mono)/rate
  assert hashlib.sha256(' '.join(spoken['lines']).encode('utf8')).hexdigest()==planned['speechTextSha256'],'Prepared spoken text changed'
  starts,ends,coverage=align.align_characters(' '.join(spoken['lines']),cached['words'],duration)
  cursor=0;lines=[]
  for number,line in enumerate(spoken['lines'],1):
   length=len(normalize(line));assert length
   lines.append(dict(line=number,rawStart=float(starts[cursor]),rawEnd=float(ends[cursor+length-1]),
    normalizedSpokenText=normalize(line),characterStarts=[float(x) for x in starts[cursor:cursor+length]],characterEnds=[float(x) for x in ends[cursor:cursor+length]]))
   cursor+=length
  assert cursor==len(starts)==len(ends),'Paragraph normalization must preserve the full continuous input'
  words=[];actual=''
  for w in cached['words']:
   text=normalize(w['text']);a,b=w['timestamp']
   if not text:continue
   begin=len(actual);actual+=text
   words.append(dict(beginChar=begin,endChar=len(actual),start=a,end=b,text=w['text']))
  beat_rows=[];auxiliary_rows=[]
  extra_for_scene=[b for b in extra if b['sceneId']==sid]
  for beat in [*planned['beats'],*extra_for_scene]:
   number=beat['seamAfterLine'];expected_end=normalize(spoken['lines'][number-1])[-12:]
   next_prefix=normalize(spoken['lines'][number])[:8] if number<len(lines) else ''
   candidates=[]
   for j,w in enumerate(words):
    if w['start'] is None or w['end'] is None or w['end']<=w['start']:continue
    if abs(float(w['end'])-lines[number-1]['rawEnd'])>.35:continue
    if not actual[:w['endChar']].endswith(expected_end):continue
    if next_prefix and not actual[w['endChar']:].startswith(next_prefix):continue
    following=words[j+1]['start'] if j+1<len(words) else duration
    if following is None or float(following)<=float(w['end']):continue
    seam=quiet_seam(mono,rate,float(w['end']),float(following))
    if seam:candidates.append((abs(float(w['end'])-lines[number-1]['rawEnd']),seam,float(w['end']),float(following)))
   row=dict(id=beat['id'],seamAfterLine=number,nextLine=beat['nextLine'],speechLines=beat['speechLines'],resultCheckLines=beat['resultCheckLines'],
    plannedMotionSeconds=beat['visual'].get('plannedMotionSeconds'),plannedHoldSeconds=beat['hold']['plannedSeconds'],
    observedSeam=None,status='pending-no-verified-complete-word-quiet-seam',humanListening='pending')
   if candidates:
    _,seam,low,high=min(candidates,key=lambda x:x[0]);row.update(observedSeam=seam,wordGap=[low,high],status='source-boundary-and-quiet-waveform-verified-edit-candidate')
    row['existingQuietSeconds']=high-low
    budget=beat['plannedObservationBudgetSeconds'];row['plannedAdditionalPauseSeconds']=None if budget is None else max(0,budget-(high-low))
   else:pending.append(dict(scene=sid,beat=beat['id'],afterLine=number,reason='Do not invent a gap or split a word. Inspect complete context/word timestamps/waveform.'))
   (auxiliary_rows if beat in extra_for_scene else beat_rows).append(row)
  breathing=[]
  occupied={x['observedSeam']['sampleOffset'] for x in [*beat_rows,*auxiliary_rows] if x['observedSeam']}
  for candidate in breathing_plan.get('candidates',[]):
   if candidate['sceneId']!=sid:continue
   number=candidate['line'];source=scene['lines'][number-1];spoken_line=spoken['lines'][number-1]
   assert hashlib.sha256(source.encode('utf8')).hexdigest()==candidate['sourceParagraphSha256']
   assert source==spoken_line,'A changed spoken alias needs an explicit original-to-spoken boundary map'
   offset=candidate['sourceBoundaryOffset'];left=normalize(spoken_line[:offset]);right=normalize(spoken_line[offset:])
   row=dict(id=candidate['id'],line=number,sourceBoundaryOffset=offset,reason=candidate['reason'],targetTotalQuietGapSeconds=candidate['targetTotalQuietGapSeconds'],maximumInsertedSeconds=candidate['maximumInsertedSeconds'],
    observedSeam=None,insertFrames=0,status='pending-no-verified-word-gap',humanPaceListening='pending')
   # Normalizing an isolated substring can change a numeral's meaning. Never
   # use that boundary unless its two normalized pieces retain the full line.
   if not left or not right or left+right!=lines[number-1]['normalizedSpokenText']:
    row['status']='pending-context-dependent-normalization';breathing.append(row);continue
   expected_time=lines[number-1]['characterEnds'][len(left)-1];options=[]
   for j,w in enumerate(words):
    if w['start'] is None or w['end'] is None or w['end']<=w['start']:continue
    if abs(float(w['end'])-expected_time)>.35:continue
    if not actual[:w['endChar']].endswith(left[-12:]) or not actual[w['endChar']:].startswith(right[:8]):continue
    following=words[j+1]['start'] if j+1<len(words) else duration
    if following is None or float(following)<=float(w['end']):continue
    low,high=float(w['end']),float(following);seam=quiet_seam(mono,rate,low,high)
    if seam:options.append((abs(float(w['end'])-expected_time),low,high,seam))
   if options:
    _,low,high,seam=min(options,key=lambda x:x[0]);gap=high-low
    missing=max(0.,candidate['targetTotalQuietGapSeconds']-gap)
    frames=min(math.floor(candidate['maximumInsertedSeconds']*60+1e-8),math.ceil(missing*60-1e-8))
    row.update(observedSeam=seam,wordGap=[low,high],existingQuietSeconds=gap,insertFrames=max(0,frames),
     status='already-at-target-without-edit' if frames<=0 else 'verified-selective-breathing-candidate')
    if seam['sampleOffset'] in occupied:
     row.update(insertFrames=0,status='existing-primary-observation-owns-this-boundary')
    else:occupied.add(seam['sampleOffset'])
   breathing.append(row)
  scenes.append(dict(id=sid,wav=wav.relative_to(R).as_posix(),wavSha256=cached['audio_sha256'],asrSha256=sha(O/'asr'/f'{sid}.json'),sampleRate=rate,samples=len(mono),seconds=duration,
   rawOrigin=0,lineStarts=[x['rawStart'] for x in lines],lines=lines,matchingCharacterCoverage=coverage,beats=beat_rows,auxiliaryVisuals=auxiliary_rows,selectiveBreathing=breathing))
 report=dict(schemaVersion=1,revision='article-flow-v6',scope='Raw source PCM line timing and word-safe quiet seam candidates only. No PCM or final timeline modification.',
  inputs=dict(voicePlanSha256=sha(H/'voice-plan.json'),koSha256=sha(P/'script/revision-v6-article-flow/narration.ko.json'),extraVisualsSha256=sha(extra_file) if extra_file.exists() else None,breathingPlanSha256=sha(breathing_file) if breathing_file.exists() else None,implementationSha256=sha(Path(__file__))),
  scenes=scenes,sceneCount=len(scenes),lineCount=sum(len(x['lines']) for x in scenes),beatCount=sum(len(x['beats']) for x in scenes),auxiliaryVisualCount=sum(len(x['auxiliaryVisuals']) for x in scenes),pendingSeams=pending,
  selectiveBreathingCandidateCount=sum(len(x['selectiveBreathing']) for x in scenes),
  selectiveBreathingVerifiedCount=sum(x['status']=='verified-selective-breathing-candidate' for s in scenes for x in s['selectiveBreathing']),
  pendingBreathing=[dict(scene=s['id'],id=x['id'],reason=x['status']) for s in scenes for x in s['selectiveBreathing'] if x['status'].startswith('pending')],
  status='pending-seam-review' if pending else 'measured-candidates-ready-for-edit-placement',humanWholeListening='pending')
 save(O/'voice-alignment.json',report);print('Raw timing prepared;',len(pending),'seams pending explicit contextual review; original PCM unchanged.')
if __name__=='__main__':main()
