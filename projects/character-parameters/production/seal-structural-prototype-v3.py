"""Seal all directly read current prototype pixels, never final video gates."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,x):
 t=p.with_name(p.name+'.seal.writing');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p)
qa1=read(BASE/'black-structural-qa-v1.json');qa2=read(BASE/'black-structural-qa-v2.json');qa3=read(BASE/'black-structural-qa-v3.json')
assert len(qa3['samples'])==26 and len(qa3['boards'])==5 and qa3['decodeExitCode']==qa3['extractionExitCode']==0
for q in [qa1,qa2,qa3]:
 assert sha(ROOT/q['videoPath'])==q['videoSha256']
 for x in q['samples']+q['boards']:assert sha(ROOT/x['path'])==x['sha256']
four={'05-useful-strength','06-role-and-limitation','07-state-not-base','11-cost-and-summary'}
unchanged=[s for s in qa1['samples'] if s['scene'] not in four|{'09-condition-and-time'}]
repaired=[s for s in qa2['samples'] if s['scene'] in four]
selected=unchanged+repaired+qa3['samples']
assert len(unchanged)==42 and len(repaired)==26 and len(selected)==94 and len({s['scene'] for s in selected})==12
assert all(s['captionReservePixelsAboveThreshold']==0 for s in selected)
boards=[b for b in qa1['boards'] if b['scene'] not in four|{'09-condition-and-time'}]+[b for b in qa2['boards'] if b['scene'] in four]+qa3['boards']
assert len(boards)==17
review=dict(schemaVersion=1,reviewedAt=now(),scope='Twelve independent silent prototype scenes/37 paragraph states: 74 core pixels plus 20 transition pixels, 94 current selected pixels on 17 selected boards. Not measured narration, final fixed-caption pixels or whole continuous animation.',allCurrentSelectedBoardsDirectlyRead=True,allV3BoardsDirectlyRead=True,coreSamples=74,additionalTransitionSamples=20,currentSelectedSamples=94,selectedBoards=boards,selectedPixels=selected,v3Samples=qa3['samples'],v3Boards=qa3['boards'],historicalReviews=[rel(BASE/'black-structural-direct-review-v1.json'),rel(BASE/'black-structural-direct-review-v2.json')],v3VideoPath=qa3['videoPath'],v3VideoSha256=qa3['videoSha256'],v3Frames=721,v3Seconds=12.016667,decodeExitCode=0,extractionExitCode=0,actualQaOuterExitObserved=True,actualQaOuterExitCode=0,actualFfmpegExitObserved=False,actualFfmpegExitCode=None,observations=[
 'The outgoing current-effect label is fully gone at f267 before the separate STRIKE label begins after f273. All 21 planned transition times f240..300 were directly read; no simultaneous label overlap remains.',
 'STA dice remain distinct from the next-turn platform and turn labels. The current/next-turn relationship and separate STRIKE action are retained.',
 'The other four targeted scenes retain the v2 resolved label heights, two visible corridor enemies and legible comparison/test paths.',
 'Unchanged seven-scene v1 prototype pixels remain directly reviewed; all selected frames retain projected top/front/side faces, spatial occlusion and meaningful state/route comparisons.',
 'The lower y910..1079 caption-reserve region has zero above-threshold pixels in each current selected sample. Final voice/cue composition still needs actual measured review.'
 ],unresolvedStructuralSampleIssues=[],prototypeStructuralPixelReviewApproved=True,source=rel(ROOT/'motion-canvas/src/projects/character-parameters/spatial-character-explanation.tsx'),sourceSha256=sha(ROOT/'motion-canvas/src/projects/character-parameters/spatial-character-explanation.tsx'),narrationTimingMeasured=False,continuousWholeAnimationReviewed=False,finalCaptionCuePixelsApproved=False,finalTimingApproved=False,finalMediaApproved=False,humanListening='pending',imagesGitAdded=0,localOnly=True)
save(BASE/'black-structural-direct-review-v3.json',review)
execution=read(BASE/'black-structural-qa-execution-v3.json');execution.update(actualOuterExitObserved=True,actualOuterExitCode=0,sessionId=None,outerExecution='exec_command completed directly with exit_code 0');save(BASE/'black-structural-qa-execution-v3.json',execution)
save(BASE/'black-structural-render-completion-v3.json',dict(observedAt=now(),cuaTab=150,uiObserved='RENDER/PAUSED with single 720-frame/12-second scene after actual ABORT rendering',viteSession=35447,ffmpegProcessIdentityObserved=False,actualFfmpegExitObserved=False,actualFfmpegExitCode=None,probe=qa3['probe'],videoPath=qa3['videoPath'],videoSha256=qa3['videoSha256'],wholeDecodeExitCode=0,qaExtractionExitCode=0,actualQaOuterExitObserved=True,actualQaOuterExitCode=0,measuredNarration=False,finalMediaApproved=False))
for x in read(BASE/'narration-tts-request-v1.json')['protectedInputs']:assert sha(ROOT/x['path'])==x['sha256']
for path,is_queue in [(BASE/'latest-checkpoint.json',False),(ROOT/'production/batches/sakurai-planning-game-design/queue.json',True)]:
 for _ in range(10):
  raw=path.read_text('utf-8-sig');doc=json.loads(raw);item=next(x for x in doc['items'] if x['slug']=='character-parameters') if is_queue else doc
  item.update(motionCanvasCreated=True,measuredMotionCanvasCreated=False,prototypeStructuralPixelReviewApproved=True,structuralPrototype=dict(status='current-selected-structural-pixels-reviewed',directReview=rel(BASE/'black-structural-direct-review-v3.json'),currentSamples=94,coreSamples=74,scenes=12,paragraphs=37,scope='Silent prototype only; voice/final cues/whole continuous animation not approved.',finalApproval=False))
  if is_queue:doc['updatedAt']=now()
  else:doc['recordedAt']=now()
  if path.read_text('utf-8-sig')==raw:save(path,doc);break
  time.sleep(.1)
 else:raise RuntimeError('Concurrent checkpoint writer; preserve it')
print('Selected 94 current structural pixels/17 boards sealed; twelve-scene prototype approved only within recorded sample scope. Protected narration unchanged; final gates remain false.')
