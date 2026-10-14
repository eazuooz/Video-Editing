"""Prepare independent current-PCM explanation blocks; no final cut approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
B=ROOT/'production/batches/cross-game-example-coverage-review'
MC='motion-canvas/src/projects/motion-sickness-games/cross-game-four-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
plan_path=R/'narration-timed-comparisons-plan-v1.json'
assert not plan_path.exists()
specs=[
 ('07b-role','portal-role-comparison-narration-v1.tsx','07b',17.66,26.28,518,'Held cube and changed room cues versus earlier independent aim mode'),
 ('07b-limit','portal-connection-limit-narration-v1.tsx','07b',42.33,48.6975,383,'Manipulation/view relation; not portal traversal or comfort test'),
 ('08b-intro','alyx-prerequisite-narration-v1.tsx','08b',0,8.68,521,'VR prerequisite: choose destination, move, read arrival'),
 ('08b-arrival','alyx-destination-arrival-narration-v1.tsx','08b',8.68,17.32,519,'Yellow destination UI and blue door/wall arrival context'),
 ('08b-limit','alyx-separate-evaluation-narration-v1.tsx','08b',32.60,40.24,459,'Separate orientation understanding from individual response')]
sources=[]
for ident,name,pcm,start,end,frames,claim in specs:
 p=ROOT/MC/name
 sources.append(dict(id=ident,source=f'{MC}/{name}',sha256=sha(p),frames=frames,pcmScene=pcm,
  currentPcmInSeconds=start,currentPcmOutSeconds=end,claim=claim,explanation=True,
  gameplay=False,worldMeasurement=False,narrationTimedPixelApproval=False))
plan=dict(schemaVersion=1,preparedAt=datetime.now(timezone.utc).isoformat(),
 preparedOnly=True,status='independent-PCM-aligned-explanation-blocks-before-final-native-cut-allocation',
 sources=sources,wordTimingSources=['first-paragraph-spliced-whole-asr-v1.json','additions-whole-asr-v1/08b.json'],
 timingScope='Current PCM ASR word landmarks and quiet editorial boundaries; human timing/listening and final mixed cues pending.',
 preservedCurrentPcm=True,original14PcmRegenerated=0,allFinalPixelsApproved=False,
 explanationFrames=sum(x['frames'] for x in sources)+1997,
 preservedSummaryFrames=1997,
 previousNarrowProposalHeld='narration-led-cut-allocation-proposal-v1.json',
 reason='The held-cube comparison needs its full paragraph and unfamiliar VR prerequisite/arrival/individual-response explanation needs its full narrated blocks. Do not shorten explanations to fit the earlier 4915-frame source bank.',
 conditionalUniqueActualRequiredFrames=6596,existingCandidateBankCapacityFrames=4915,
 conditionalExtraUniqueActualRequiredFrames=1681,
 additionalActualMustBeRelevantAndNormalSpeed=True,sourceAndFinalRatioApproved=False,
 sourceSelectionNext='Compare fresh unused normal-speed task/view footage. Then align actual before/action/result cuts and observation pauses; no loops, slowdown or unrelated idle.')
assert plan['explanationFrames']==4397
plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
base=(B/'render-motion-narration-timed-summary-v1.cjs').read_text('utf-8')
base=base.replace('narration-timed-summary-v1','narration-timed-comparisons-v1')
base=base.replace('narration-timed-summary-plan-v1.json','narration-timed-comparisons-plan-v1.json')
base=base.replace('narration-timed-summary-render-execution-v1.json','narration-timed-comparisons-render-execution-v1.json')
base=base.replace('rendering-one-33.28s-narration-timed-summary','rendering-five-PCM-aligned-explanation-blocks')
base=base.replace('rendered-summary-awaiting-moving-label-caption-clearance-review','rendered-comparisons-awaiting-moving-label-caption-clearance-review')
base=base.replace('// This renders only two held visual targets; no audio, source gameplay or UI.','// Five independent explanation blocks only; no PCM, gameplay, final captions or publishing changed.')
worker=B/'render-motion-narration-timed-comparisons-v1.cjs'
assert not worker.exists()
worker.write_text(base,'utf-8')
print(json.dumps(dict(blocks=len(sources),frames=sum(x['frames'] for x in sources),extraActualRequiredFrames=1681)))
