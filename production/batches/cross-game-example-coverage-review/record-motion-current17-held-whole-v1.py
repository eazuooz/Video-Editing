"""Preserve all17 whole-text comparisons and the independently evidenced placement hold."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'current17-mixed-whole-direct-review-v1-held.json';assert not out.exists()
closure=read(R/'current17-mixed-whole-asr-execution-v1.session.json');state=read(R/'current17-mixed-whole-asr-execution-v1.json')
assert closure['actualOuterExitCode']==state['exitCode']==0 and not closure['workerCurrentlyAlive'] and state['completed']==17
prior=read(R/'current17-mixed-whole-partial-direct-review-v1.json');notes={v['scene']:v['observations'] for v in prior['results']}
notes.update({
 '07':'All six complete paragraphs directly compared. Whole alternatives 컷임으로/컷이므로, 잊지는/읽지는, 앞에/앞의 and title2 spelling need independent current paragraphs. Separate-cut warning sequence is present; human pronunciation unconfirmed.',
 '07b':'All six full paragraph sequences compared. Extra initial 스 before 퍼즐 and 방해 단서 versus 방의 단서 remain recognition alternatives. Separately measured PCM placement8.32 interrupted a voiced onset across an observation pause; that physical defect holds this mix regardless of recognizable whole text.',
 '08':'All four full paragraphs recovered; no whole omission/repetition observed. Movement duration and arrival orientation remain separate questions.',
 '08b':'All five full paragraphs recovered; destination selection, door/wall orientation, hand manipulation and tool/cube comparison remain connected. Whole punctuation/spacing alternatives only.',
 '09':'All six full paragraphs recovered; visible tool/surface/view positions and limited evidentiary claims preserved.',
 '10':'All four full paragraphs compared. 다름으로 versus 다르므로 is an ending/particle recognition alternative; independent paragraph remains pending.',
 '11':'All six full paragraphs compared. aim mode English transcription is equivalent title spelling; 뒤에/뒤의 is a particle recognition alternative.',
 '11b':'All four full paragraphs compared. 네, 게임 versus 네 게임 punctuation and 화면에/화면의 recognition alternative; all four named game/object comparisons and conclusion connection present.',
 '12':'All four full conclusion paragraphs compared. 마지막에/마지막의 particle alternative; body choices and coaching ending connection present.'})
assert len(notes)==17
rows=[]
for result in state['results']:
 sid=result['id'];path=R/f'current17-mixed-whole-asr-v1/{sid}.json';row=read(path)
 assert row['expectedKo'] and row['text'] and row['exactSourceStereoPcmBytesMatched']
 rows.append(dict(scene=sid,resultPath=path.relative_to(ROOT).as_posix(),sha256=sha(path),wholeExpectedAndRecognizedTextsDirectlyCompared=True,findings=notes[sid],currentMixedAudioApproved=False))
out.write_text(json.dumps(dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),actualSession=55087,actualOuterExitCode=0,actualCompletion=closure['actualCompletion'],workerCurrentlyAlive=False,all17WholeTextsDirectlyCompared=True,results=rows,mixAacSha256=state['mixAacSha256'],decodedAacSha256=state['decodedAacSha256'],heldPhysicalPlacementAudit='current17-first-onset-placement-audit-v1.json',all81IndependentContextsDirectlyCompared=False,independentContextsExecuted=False,wholeRecognizerChunkingWarningPreserved=True,wholeRecognizerEndingWarningIsNotAnAcousticFailureDiagnosis=True,currentMixedContentReviewPassed=False,currentMixedAudioApproved=False,humanListeningApproved=False,humanPronunciationApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
old=read(R/'measured-current17-plan-v1.json');new=read(R/'measured-current17-plan-v2.json')
a=[v for v in old['voicePlacements'] if v['sceneId']=='07b'][1];b=[v for v in new['voicePlacements'] if v['sceneId']=='07b'][1]
delta=((b['destinationStartSample']-b['sourceStartSample'])-(a['destinationStartSample']-a['sourceStartSample']))/24000
assert abs(delta+1/150)<1e-9
clarification=R/'current17-placement-prose-clarification-v1.json';assert not clarification.exists()
clarification.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),plan=new['supersedesPlan'],activePlan='measured-current17-plan-v2.json',activePlanSha256=sha(R/'measured-current17-plan-v2.json'),preserveActiveInputBytes=True,clarification='The V2 purpose prose says33ms earlier. Exact measured placement delta for all retained p2 samples at or after originalcut8.32 is6.666667ms earlier (0.4 video frame);33ms is inaccurate prose. The early voiced onset formerly before the pause moves intact into p2. Final narrated pixels remain pending.',retainedP2TimingDeltaSeconds=delta,retainedP2TimingDeltaVideoFrames=delta*60),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(whole17DirectlyCompared=True,oldMixHeld=True,contextsExecuted=False,retainedP2DeltaSeconds=delta,finalAudioApproved=False)))
