"""Adopt only a fully directly read current ASS/input review."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,re,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;FINAL=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for n in range(40):
  try:os.replace(t,p);return
  except OSError:
   if n==39:raise
   time.sleep(.15)
reviewPath=BASE/'selected-inputs-direct-review-v1.json';review=read(reviewPath)
assert review['allBoardsDirectlyRead'] and review['all400CuePixelsDirectlyRead'] and review['all69CutEdgesDirectlyRead'] and review['all128WhiteMotionWithActualCaptionsDirectlyRead']
assert review['sourceAllocationApproved'] and not review['unresolvedDefects']
statePath=BASE/'selected-inputs-execution-v1.json';state=read(statePath)
assert state['exitCode']==0 and state['actualExitObserved'] and sha(statePath)==review['executionSha256']
candidatePath=BASE/'measured-allocation-v2/plan.json';candidate=read(candidatePath)
capPath=BASE/'caption-candidate-v2/captions.json';cap=read(capPath)
assert sha(candidatePath)==state['plan']['sha256'] and sha(capPath)==state['captionCandidate']['sha256']
assert sha(ROOT/state['silentVideo'])==state['silentSha256'] and sha(ROOT/state['captionAss'])==state['captionAssSha256']
assert not FINAL.exists(),'Preserve already adopted final plan'
for b in review['boards']:assert sha(ROOT/b['path'])==b['sha256'] and b['directlyRead']
reference=read(ROOT/'projects/player-customization/production/final-v1/plan.json')
for x in [reference['intro'],reference['membership']]:assert sha(ROOT/x['path'])==x['sha256']
assert candidate['finalFrames']==37098 and candidate['bodyFrames']==36378 and candidate['ratioErrorFrames']<=1
assert sum(x['sourceSamples']for x in candidate['scenes'])==14532962
FINAL.mkdir();timing=dict(schemaVersion=1,adoptedAt=now(),sampleRate=24000,wholePcmSamples=14532962,allCurrentPcmSamplesPreserved=True,rows=[])
for scene in candidate['scenes']:
 assert sha(ROOT/scene['voicePath'])==scene['voiceSha256']
 timing['rows'].append(dict(id=scene['id'],audioPath=scene['voicePath'],audioSha256=scene['voiceSha256'],samples=scene['sourceSamples'],frames=scene['frames'],startFrame=scene['startFrame'],endFrame=scene['endFrameExclusive'],paragraphStartSamples=[p['sourceInSample']for p in scene['paragraphs']],allSamplesPreserved=True))
save(FINAL/'voice-timing.json',timing)
plan=copy.deepcopy(candidate);plan.update(candidateOnly=False,adoptedAt=now(),finalTimingApproved=True,bodyRatioApproved=True,allInputSegmentCaptionPixelsReviewed=True,body60_40ErrorFrames=candidate['ratioErrorFrames'],selectedInputReview=rel(reviewPath),selectedInputReviewSha256=sha(reviewPath),bodySilentVideo=state['silentVideo'],bodySilentSha256=state['silentSha256'],voiceTiming=rel(FINAL/'voice-timing.json'),voiceTimingSha256=sha(FINAL/'voice-timing.json'),intro=reference['intro'],membership=reference['membership'],cuts=state['segments'],allFinalPixelsReviewed=False,finalMixedAsrApproved=False,render=False,qa=False,collected=False,uploaded=False,videoId=None)
for scene in plan['scenes']:
 for part in scene['parts']:part['captionPixelsReviewed']=True
for cut in plan['cuts']:cut['captionPixelsReviewed']=True
save(FINAL/'plan.json',plan)
def shift(m):
 h,mi,se=m.group().split(':');n=round((int(h)*3600+int(mi)*60+float(se)+2)*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
ass=(ROOT/state['captionAss']).read_text('utf-8');out=[]
for line in ass.splitlines():
 if line.startswith('Dialogue:'):line=re.sub(r'\d+:\d{2}:\d{2}\.\d{2}',shift,line,count=2)
 out.append(line)
(FINAL/'captions.ko.ass').write_text('\n'.join(out)+'\n','utf-8')
for lang in ['ko','en']:(FINAL/f'captions.{lang}.srt').write_bytes((BASE/f'caption-candidate-v2/candidate.{lang}.srt').read_bytes())
save(FINAL/'caption-clock-adoption.json',dict(adoptedAt=now(),planSha256=sha(FINAL/'plan.json'),sourceCaptionCandidate=rel(capPath),sourceCaptionSha256=sha(capPath),koCueCount=400,enCueCount=148,paragraphs=73,captionCenter=[960,970],style='boxed-white-forest-v1',bodyAssSha256=state['captionAssSha256'],finalAssSha256=sha(FINAL/'captions.ko.ass'),bodyToFinalSecondsOffset=2,koSrtByteIdentical=True,enSrtByteIdentical=True,allInputSegmentCaptionPixelsReviewed=True,allFinalPixelsReviewed=False))
manifestPath=BASE.parent/'project.json';manifest=read(manifestPath)
manifest['editing'].update(independentSceneCount=24,koParagraphCount=73,enParagraphCount=73,plannedSceneOrder=[s['id']for s in plan['scenes']],exampleSeconds=21827/60,measuredTotals=dict(actualFrames=21827,whiteFrames=14551,bodyFrames=36378,finalFrames=37098,fps=60,seconds=618.3,ratioErrorFrames=candidate['ratioErrorFrames']),finalTimingApproved=True,bodyRatioApproved=True,finalPlan=rel(FINAL/'plan.json'),allOriginalPcmPreserved=True)
manifest['audio'].update(ttsStarted=True,wholeVoiceAsrApproved=True,mixedAsrApproved=False,currentRawPcmSamples=14532962,currentRawPcmSeconds=14532962/24000,humanListeningPending=True)
manifest['paths'].update(finalPlan=rel(FINAL/'plan.json'),voiceTiming=rel(FINAL/'voice-timing.json'),captionKorean=rel(FINAL/'captions.ko.srt'),captionEnglish=rel(FINAL/'captions.en.srt'))
manifest['status']='reviewed-inputs-current-mix-pending';save(manifestPath,manifest)
cp=read(BASE/'latest-checkpoint.json');cp.update(stage='current24-73-reviewed-inputs-final-timing-adopted',finalPlan=rel(FINAL/'plan.json'),finalTimingApproved=True,bodyRatioApproved=True,allInputSegmentCaptionPixelsReviewed=True,finalMixedAsrApproved=False,render=False,qa=False,collected=False,uploaded=False,nextAction='Fresh resources; single CPU2 Nimbus mix preserving all24 PCM, then current24 whole+24 padded complete mixed-ASR contexts. Pair/final pixels/QA/collection/private/Git pending.',updatedAt=now());save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items']if x['slug']=='similar-game-design');item.update(stage=cp['stage'],finalPlan=cp['finalPlan'],finalTimingApproved=True,bodyRatioApproved=True,allInputSegmentCaptionPixelsReviewed=True,nextAction=cp['nextAction'],updatedAt=now());q['updatedAt']=now();save(qp,q)
print(json.dumps(dict(finalFrames=37098,seconds=618.3,koCues=400,enCues=148,finalTimingApproved=True,finalMixedAsrApproved=False,allFinalPixels=False)))
