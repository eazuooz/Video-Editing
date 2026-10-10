"""Record prepared followups and completed additional review accurately."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
FOLDER=BASE/'voice-clarity-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
paths=[BASE/'review-voice-clarity-v2.py',BASE/'display-clarity-asr-v2.py',BASE/'record-clarity-asr-session-v2.py',
       BASE/'capture-current-resource-v5.ps1',BASE/'verify-voice-clarity-research-resume-v2.py',
       ROOT/'production/batches/sakurai-planning-game-design/proof-character-parameters/adopt-additional-action-bank-v2.py']
request=read(FOLDER/'request.json')
for r in request['protectedInputs']: assert sha(ROOT/r['path'])==r['sha256'],r['path']
proof=dict(preparedAt=datetime.now(timezone.utc).isoformat(),
           ownedLiveTtsSession=33582,ownedLeaseToken='c64e812a-0796-43ea-8142-0d95423a930f',
           preparedFiles=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths],
           pythonCompilationAndAsrDryRunExitCode=0,
           requiredBeforeRuntime=['Actual session33582 exit0','Own lease/history closed and exact original research command/cwd queue/job resume verified','Fresh CIM/GPU/resource observation','Current duplicate --check pass','All25 protected inputs unchanged'],
           candidateAssembly='Preserve original08 prefix476640 and09 prefix460560 exact24kHz16bitmono samples; add2400 zero samples and the whole corresponding new paragraph. Other10 original scene PCM hashes are reused.',
           plannedWholeRecognitions=2,plannedIndependentCompleteParagraphRecognitions=2,
           independentPaddingSamplesEachSide=6000,expectedTextUsedAsRecognizerPrompt=False,
           actualCandidateAssemblyStarted=False,actualFreshAsrStarted=False,
           preparedCodeIsCompletion=False,currentVoiceApproved=False,
           currentSourceBank='production/batches/sakurai-planning-game-design/proof-character-parameters/source-action-bank-v1.json',
           currentSourceBankSha256='dbccd0c66b0d5f80ac74a2cf7a185b14d825d221dbd09cc2a28f4b63343dff6f',
           additionalSourceSparseReview='production/batches/sakurai-planning-game-design/proof-character-parameters/additional-role-action-direct-review-v2.json',
           additionalSourcePlayback='production/batches/sakurai-planning-game-design/proof-character-parameters/additional-role-playback-observation-v2.json',
           additionalSourceReviewCompleteForCandidateScope=True,additionalSourceAdopted=False,
           finalTimingApproved=False,finalMixedAsrApproved=False,allFinalPixelsApproved=False,qa=False,collected=False,uploaded=False,actualId=None,
           humanListening='pending',humanPronunciation='pending',finalPublicRights='pending',
           originalMainInputsAndTwelvePcmUnchanged=True,rasterGitAdditions=0,mediaGitAdditions=0)
target=FOLDER/'prepared-followups.json';assert not target.exists()
target.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedFiles=len(paths),protectedInputs=25,actualAssemblyOrAsrStarted=False,newSourceAdopted=False)))
