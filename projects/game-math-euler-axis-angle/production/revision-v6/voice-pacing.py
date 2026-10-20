"""CPU raw line timing and safe106-beat+explicit auxiliary seams; never edit PCM.

Run after the one current source-ASR batch. Unmatched/unsafe seams stay pending;
the edit timeline must not invent a timing or cut a word to fit a planned hold.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,runpy,sys
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
 n=round(rate*.08);a=max(0,math.ceil(low*rate-1e-6));b=min(len(samples),math.floor(high*rate+1e-6))
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
def calibrated_word_boundaries(sid,cached,source_hash,mono,rate,spoken,normalize,review):
 # A zero ASR gap can be a stretched terminal-word timestamp. Independently
 # reviewed physical quiet may tighten that silent word tail in a NEW timing
 # copy; the original ASR cache and every source sample remain unchanged.
 words=[dict(w,timestamp=list(w['timestamp'])) for w in cached['words']];physical={};adjustments=[]
 for item in review.get('results',[]):
  if item['scene']!=sid or item.get('preferredSlotForOwnerReview')=='sourceEOF':continue
  q=item.get('quietWindow');boundary=item.get('selectedBoundary')
  if not q or not boundary or not item['paragraphEndsInCompleteSentencePunctuation']:continue
  assert item['source']['wavSha256']==source_hash
  if q.get('overlapsNonterminalAsrWords'):continue
  number=item['afterLine'];terminal=boundary['terminalWord'];following=boundary.get('nextWord')
  if following is None:continue
  matches=[j for j,w in enumerate(words) if w['text']==terminal['text'] and w['timestamp']==terminal['timestamp']]
  if len(matches)!=1:continue
  j=matches[0]
  if j+1>=len(words) or words[j+1]['text']!=following['text'] or words[j+1]['timestamp']!=following['timestamp']:continue
  whole=normalize(' '.join(w['text'] for w in words));end=len(normalize(' '.join(w['text'] for w in words[:j+1])))
  if not whole[:end].endswith(normalize(spoken[number-1])[-12:]):continue
  if not whole[end:].startswith(normalize(spoken[number])[:8]):continue
  low=q['startSample']/rate;high=q['endSample']/rate
  assert high-low>=.08-1e-8 and words[j]['timestamp'][0]<low<high<words[j+1]['timestamp'][1]
  assert abs((low+high)/2-item['searchAnchorSeconds'])<=.201
  checked=quiet_seam(mono,rate,low,high)
  if not checked:continue
  before=[list(words[j]['timestamp']),list(words[j+1]['timestamp'])]
  words[j]['timestamp'][1]=min(words[j]['timestamp'][1],low)
  words[j+1]['timestamp'][0]=max(words[j+1]['timestamp'][0],high)
  physical[item['beat']]=dict(seam=checked,wordGap=[low,high],reviewedBoundary=dict(terminal=terminal,following=following),
   method='independent80ms-physical-quiet-at-complete-paragraph;ASR-silent-tail-tightening-only')
  adjustments.append(dict(beat=item['beat'],afterLine=number,originalTerminalAndNextTimestamps=before,
   timingTerminalAndNextTimestamps=[words[j]['timestamp'],words[j+1]['timestamp']],quietWindowSamples=checked['quietWindowSamples'],
   sourceSamplesChanged=False,originalAsrChanged=False,humanPhoneticListening='pending'))
 return words,physical,adjustments
def calibrated_breathing_words(sid,words,source_hash,mono,rate,spoken,normalize,review):
 # Only the already planned internal boundaries with independent lexical AND
 # waveform evidence are accepted. Uncertain homophones/numbers are not newly
 # legalized to manufacture a pause. This changes timing estimates, not audio.
 adjustments=[]
 for item in review.get('results',[]):
  if item['scene']!=sid or not item.get('wordSafeEditCandidateForOwnerReview'):continue
  assert item['source']['wavSha256']==source_hash
  boundary=item['selectedBoundary'];terminal,following=boundary['terminalWord'],boundary['nextWord']
  matches=[i for i,w in enumerate(words) if w['text']==terminal['text'] and w['timestamp']==terminal['timestamp']]
  if len(matches)!=1:continue
  j=matches[0]
  assert words[j+1]['text']==following['text'] and words[j+1]['timestamp']==following['timestamp']
  number=item['line'];offset=item['sourceBoundaryOffset'];line=spoken[number-1]
  assert line[:offset]==item['leftApprovedClause'] and line[offset:]==item['rightApprovedClause']
  whole=normalize(' '.join(w['text'] for w in words));end=len(normalize(' '.join(w['text'] for w in words[:j+1])))
  assert whole[:end].endswith(normalize(line[:offset])[-12:]) and whole[end:].startswith(normalize(line[offset:])[:8])
  quiet=item['quietWindow'];assert not quiet['overlapsNonterminalAsrWords']
  low,high=quiet['startSample']/rate,quiet['endSample']/rate
  assert words[j]['timestamp'][0]<low<high<words[j+1]['timestamp'][1]
  assert abs((low+high)/2-item['searchAnchorSeconds'])<=.201
  checked=quiet_seam(mono,rate,low,high);assert checked
  before=[list(words[j]['timestamp']),list(words[j+1]['timestamp'])]
  words[j]['timestamp'][1]=min(words[j]['timestamp'][1],low);words[j+1]['timestamp'][0]=max(words[j+1]['timestamp'][0],high)
  adjustments.append(dict(breath=item['id'],line=number,originalTerminalAndNextTimestamps=before,
   timingTerminalAndNextTimestamps=[words[j]['timestamp'],words[j+1]['timestamp']],quietWindowSamples=checked['quietWindowSamples'],
   sourceSamplesChanged=False,originalAsrChanged=False,method='independently-reviewed80ms-quiet-at-existing-semantic-breath-candidate',humanPhoneticListening='pending'))
 return words,adjustments
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--audit-original39',action='store_true');args=parser.parse_args()
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 plan=read(H/'voice-plan.json');script=read(P/'script/revision-v6-article-flow/narration.ko.json');input_script=read(H/'voice-input.ko.json')
 current_file=O/('baseline-pcm-mapping.json' if args.audit_original39 else 'current-pcm.json');current=read(current_file)
 if not args.audit_original39:assert current['status']=='current41-ready-for-word-alignment'
 assert current['inputs']['koSha256']==sha(P/'script/revision-v6-article-flow/narration.ko.json')
 current_by={s['id']:s for s in current['scenes']};assert len(current_by)==41
 extra_file=H/'voice-extra-visuals.json';extra=read(extra_file)['visuals'] if extra_file.exists() else []
 breathing_file=H/'voice-breathing-plan.json';breathing_plan=read(breathing_file) if breathing_file.exists() else {}
 review_file=O/'seam-pending-review.json';boundary_review=read(review_file) if review_file.exists() else {}
 breathing_review_file=O/'breathing-pending-review.json';breathing_review=read(breathing_review_file) if breathing_review_file.exists() else {}
 if breathing_plan:assert breathing_plan['koSha256']==sha(P/'script/revision-v6-article-flow/narration.ko.json')
 assert sha(P/'script/revision-v6-article-flow/narration.ko.json')==plan['inputs']['koSha256'],'Current script changed; refresh CPU voice preparation without replacing PCM'
 # Install only existing math text normalization; the historical batch's main
 # never executes and no generic alignment/source/ASR script is modified.
 old_argv=sys.argv[:];sys.argv=[sys.argv[0],P.name]
 try:helpers=runpy.run_path(str(R/'production/batches/game-math-part2-full-series/align.py'),run_name='v6_math_alignment_helpers')
 finally:sys.argv=old_argv
 spec=importlib.util.spec_from_file_location('v6_timing_aliases',H/'voice-normalize.py');aliases=importlib.util.module_from_spec(spec);spec.loader.exec_module(aliases)
 align=helpers['a'];normalize=aliases.install(helpers);scenes=[];pending=[]
 for scene,spoken,planned in zip(script['scenes'],input_script['scenes'],plan['scenes']):
  if args.audit_original39 and scene['id'] in ['v6-10','v6-32']:continue
  sid=scene['id'];assert sid==spoken['id']==planned['id'];item=current_by[sid];wav=R/item['file'];asr_file=R/item['asrFile'];cached=read(asr_file)
  assert sha(wav)==item['sha256']==cached['audio_sha256'] and sha(asr_file)==item['asrSha256'],'ASR is stale; no substitute timestamps'
  samples,rate=sf.read(wav,dtype='float32',always_2d=True);mono=samples.mean(axis=1);duration=len(mono)/rate
  assert hashlib.sha256(' '.join(spoken['lines']).encode('utf8')).hexdigest()==planned['speechTextSha256'],'Prepared spoken text changed'
  timing_words,physical,word_adjustments=calibrated_word_boundaries(sid,cached,cached['audio_sha256'],mono,rate,spoken['lines'],normalize,boundary_review)
  timing_words,breath_adjustments=calibrated_breathing_words(sid,timing_words,cached['audio_sha256'],mono,rate,spoken['lines'],normalize,breathing_review)
  word_adjustments.extend(breath_adjustments)
  starts,ends,coverage=align.align_characters(' '.join(spoken['lines']),timing_words,duration)
  cursor=0;lines=[]
  for number,line in enumerate(spoken['lines'],1):
   length=len(normalize(line));assert length
   lines.append(dict(line=number,rawStart=float(starts[cursor]),rawEnd=float(ends[cursor+length-1]),
    normalizedSpokenText=normalize(line),characterStarts=[float(x) for x in starts[cursor:cursor+length]],characterEnds=[float(x) for x in ends[cursor:cursor+length]]))
   cursor+=length
  assert cursor==len(starts)==len(ends),'Paragraph normalization must preserve the full continuous input'
  words=[];raw_words=[]
  for w in timing_words:
   if normalize(w['text']):raw_words.append(w)
  # Whole-context normalization retains phrases such as 세 성분→3성분.
  # Standalone 세 plus standalone 성분 would otherwise disagree despite the
  # same actual spoken word boundary. Prefix lengths identify complete-word
  # endpoints only; no ASR timestamp or source sample is modified.
  actual=normalize(' '.join(w['text'] for w in raw_words));prefix=''
  for w in raw_words:
   a,b=w['timestamp'];begin=len(normalize(prefix));prefix+=' '+w['text'];end=len(normalize(prefix))
   assert 0<=begin<=end<=len(actual)
   words.append(dict(beginChar=begin,endChar=end,start=a,end=b,text=w['text']))
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
   if number==len(lines) and candidates==[] and normalize(actual).endswith(expected_end):
    # Exact EOF append never cuts an original word/sample. It is explicitly
    # different from claiming an80ms interior silence that does not exist.
    tail=mono[-max(1,round(rate*.02)):]
    seam=dict(sampleOffset=len(mono),rawSeconds=duration,slotType='sourceEOF',noInteriorSampleCut=True,
     tail20msRms=float(np.sqrt(np.mean(tail.astype(np.float64)**2))),tail20msPeak=float(np.max(np.abs(tail))),lastSample=float(mono[-1]),minimumQuietSeconds=0)
    row.update(observedSeam=seam,wordGap=[duration,duration],existingQuietSeconds=0,status='complete-sourceEOF-append;no-original-sample-cut',plannedAdditionalPauseSeconds=beat['plannedObservationBudgetSeconds'])
   elif beat['id'] in physical:
    evidence=physical[beat['id']];low,high=evidence['wordGap'];row.update(observedSeam=evidence['seam'],wordGap=[low,high],existingQuietSeconds=high-low,
     status='reviewed-physical80ms-complete-paragraph-boundary',boundaryMethod=evidence['method'],reviewedBoundary=evidence['reviewedBoundary'])
    budget=beat['plannedObservationBudgetSeconds'];row['plannedAdditionalPauseSeconds']=None if budget is None else max(0,budget-(high-low))
   elif candidates:
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
   if row['status'].startswith('pending') and any(x['id']==row['id'] for x in breathing_review.get('results',[])):
    evidence=next(x for x in breathing_review['results'] if x['id']==row['id'])
    row.update(status='intentionally-retain-current-natural-speech;human-listening-pending',
     retainedNaturalSpeechReason=evidence['classification'],independentBoundaryReviewFile=breathing_review_file.relative_to(R).as_posix())
   breathing.append(row)
  scenes.append(dict(id=sid,wav=wav.relative_to(R).as_posix(),wavSha256=cached['audio_sha256'],asrFile=asr_file.relative_to(R).as_posix(),asrSha256=sha(asr_file),sampleRate=rate,samples=len(mono),seconds=duration,
   rawOrigin=0,lineStarts=[x['rawStart'] for x in lines],lines=lines,matchingCharacterCoverage=coverage,beats=beat_rows,auxiliaryVisuals=auxiliary_rows,selectiveBreathing=breathing,wordBoundaryTimingAdjustments=word_adjustments))
 report=dict(schemaVersion=1,revision='article-flow-v6',scope='Raw source PCM line timing and word-safe quiet seam candidates only. No PCM or final timeline modification.',
  inputs=dict(voicePlanSha256=sha(H/'voice-plan.json'),koSha256=sha(P/'script/revision-v6-article-flow/narration.ko.json'),currentPcmMappingSha256=sha(current_file),extraVisualsSha256=sha(extra_file) if extra_file.exists() else None,breathingPlanSha256=sha(breathing_file) if breathing_file.exists() else None,timingAliasesSha256=sha(H/'voice-normalize.py'),boundaryReviewSha256=sha(review_file) if review_file.exists() else None,breathingBoundaryReviewSha256=sha(breathing_review_file) if breathing_review_file.exists() else None,implementationSha256=sha(Path(__file__))),
  scenes=scenes,sceneCount=len(scenes),lineCount=sum(len(x['lines']) for x in scenes),beatCount=sum(len(x['beats']) for x in scenes),auxiliaryVisualCount=sum(len(x['auxiliaryVisuals']) for x in scenes),pendingSeams=pending,
  selectiveBreathingCandidateCount=sum(len(x['selectiveBreathing']) for x in scenes),
  selectiveBreathingVerifiedCount=sum(x['status']=='verified-selective-breathing-candidate' for s in scenes for x in s['selectiveBreathing']),
  pendingBreathing=[dict(scene=s['id'],id=x['id'],reason=x['status']) for s in scenes for x in s['selectiveBreathing'] if x['status'].startswith('pending')],
  status='pending-seam-review' if pending else 'measured-candidates-ready-for-edit-placement',humanWholeListening='pending')
 if args.audit_original39:report.update(status='partial-original39-seam-audit;not-final-timing',excludedRetakeScenes=['v6-10','v6-32'])
 save(O/('voice-alignment-original39-audit.json' if args.audit_original39 else 'voice-alignment.json'),report);print('Raw timing prepared;',len(pending),'seams pending explicit contextual review; original PCM unchanged.')
if __name__=='__main__':main()
