"""Measure additive PCM capacity after actual exit/resume; no cut or QA approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OLD=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'measured-additions-feasibility-v1.json';assert not out.exists()
tts=read(R/'narration-tts-execution-v7.json');resume=read(R/'research-handoff-verification-v7.json')
assert tts['generationComplete'] and tts['actualExitObserved'] and tts['actualOuterExitCode']==0
assert resume['restorationVerified'] and resume['ttsLeaseToken']==tts['leaseToken']
assert len(tts['results'])==3 and {x['id'] for x in tts['results']}=={'07b','08b','11b'}
for row in tts['protectedInputs']+tts['results']:assert sha(ROOT/row['path'])==row['sha256']
plan=read(OLD/'measured-additive-plan-v1.json')
pair=read(OLD/'final-pair-execution-v2.json')
assert len(plan['scenes'])==14 and len(pair['pieces'])==20
assert sum(x['frames'] for x in pair['pieces'])==40193
bank=read(R/'sources/source-action-bank-v1.json')
capacity=[dict(id=a['id'],sourceKey=a['sourceKey'],firstPts=a['sourceFirstPts'],endExclusivePts=a['sourceEndExclusivePts'],
    nativeTimeBase=a['nativeTimeBase'],sourceFrames=a['frames'],maximumNormalSpeed60FpsFrames=math.floor(a['seconds']*60+1e-7)) for a in bank['actions']]
scenes=[dict(**x,minimumBodyFrames=math.ceil(x['samples']/400)) for x in tts['results']]
minimumBody=sum(x['minimumBodyFrames'] for x in scenes)
newBody=plan['bodyFrames']+minimumBody
targetActual=round(newBody*.6)
newActual=targetActual-plan['actualFrames']
maxActual=sum(x['maximumNormalSpeed60FpsFrames'] for x in capacity)
summaryFrames=next(x['minimumBodyFrames'] for x in scenes if x['id']=='11b')
proof=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),
    scope='Current measured PCM lower-bound timing and unique source capacity only; no editorial cut, voice, ratio or final pixels approval',
    actualOuterSession=tts['actualOuterSession'],voiceStateSha256=sha(R/'narration-tts-execution-v7.json'),
    restorationProofSha256=sha(R/'research-handoff-verification-v7.json'),scenes=scenes,
    baselineBodyFrames=plan['bodyFrames'],baselineActualFrames=plan['actualFrames'],baselineExplanationFrames=plan['explanationFrames'],
    minimumAdditionalBodyFrames=minimumBody,additionalActualForMinimumBodyFrames=newActual,
    additionalExplanationForMinimumBodyFrames=minimumBody-newActual,summaryMinimumExplanationFrames=summaryFrames,
    availableUniqueNormalSpeedActualFrames=maxActual,sourceCapacity=capacity,
    bankFitsMinimumMeasuredVoice=newActual<=maxActual,
    minimumExplanationCanContainSummary=minimumBody-newActual>=summaryFrames,
    retainedOriginalScenes=[dict(id=s['id'],voice=s['voice'],audioSha256=s['audioSha256'],frames=s['frames']) for s in plan['scenes']],
    retainedSilentPieces=pair['pieces'],original14PcmRegenerated=0,baseline20SilentPiecesRegenerated=0,
    insertions=[dict(id='07b',after='07',before='08'),dict(id='08b',after='08',before='09'),dict(id='11b',after='11',before='12')],
    actualPlaybackSpeed=1,loops=0,slowdowns=0,sourceAudio=False,
    measuredNarrationContentApproved=False,selectedSourceCutsApproved=False,finalRatioApproved=False,
    finalMovingAnnotationApproved=False,finalMixedAudioApproved=False,finalPixelApproved=False)
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:proof[k] for k in ['minimumAdditionalBodyFrames','additionalActualForMinimumBodyFrames','availableUniqueNormalSpeedActualFrames','bankFitsMinimumMeasuredVoice','minimumExplanationCanContainSummary']}))
