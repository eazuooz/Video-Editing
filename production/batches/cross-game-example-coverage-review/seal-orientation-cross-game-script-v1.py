"""Seal directly compared19 paired paragraphs and exact protected originals."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=O/'cross-game-paired-script-direct-review-v1.json';assert not out.exists()
kp=O/'script/cross-game-repair-batch.ko.json';ep=O/'script/cross-game-repair-batch.en.json';k=read(kp);e=read(ep)
assert [s['id'] for s in k['scenes']]==[s['id'] for s in e['scenes']]==['01b','03b','07b','10b','21r']
assert [len(s['lines']) for s in k['scenes']]==[len(s['lines']) for s in e['scenes']]==[1,5,6,6,1]
tts=read(O/'narration-tts-execution-v2.json')
for r in tts['protectedInputs']+tts['results']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
assert k['scenes'][-1]['lines'][0]==next(s for s in read(O/'script/additions.ko.json')['scenes'] if s['id']=='21a')['lines'][0]
proofs=[kp,ep,O/'cross-game-causal-and-source-plan-v1.json',O/'cross-game-source-permissions-and-recent-use-v1.json',O/'space-enlarged-static-direct-review-v3.json',O/'cross-game-native-direct-review-v1.json']
data=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),actualWholePairedRead='682101 exit0',all19KoAndIndependentEnParagraphsDirectlyCompared=True,sceneCount=5,paragraphCount=19,
 fullPairs=[dict(id=a['id'],title=a['title'],ko=a['lines'],en=b['lines']) for a,b in zip(k['scenes'],e['scenes'])],
 findings=['01b preserves original20.16s overview and adds actual example order: Superflight/bicycle, assembled aircraft, componentplacement. No replaced original words or invented matching Sakurai mathematics lecture.',
 '03b supplies cycling prerequisites, separates position/lean, compares upright/inverted/upright bicycle action and motivates front/up axes. Guides must follow the rigid bicycle and not the articulated rider.',
 '07b supplies build-and-fly prerequisites, compares takeoff/bank and a separately announced viewpoint, uses redfront/bluewing observedrole guides.90degrees remains an explicit mathematicalmodel, not a measured game angle.',
 '10b distinguishes translucent green preview from placed solid part, says compare two shots rather than claiming uninterrupted rotation/placement. Size selection changes are separate. Shared reference-frame principle connects flight and building.',
 '21r is one exact original firstparagraph candidate, because both currentwhole/independentASR omit 시작. Candidate adoption and p2bytepreserving splice require currentASR and seam review.'],
 contentReadyForApprovedVoiceMeasurement=True,originalAllWordingAndOrderPreserved=True,original24PcmAnd6AdditivePcmUnchanged=True,overviewPromiseReviewed=True,
 newSourceClaimLimitsReviewed=True,sourcePlanningOnly=True,narrationMeasured=False,finalFourGameTeachingApproved=False,currentMixedApproved=False,allMovingPixelsApproved=False,humanListeningApproved=False,publicRightsApproved=False,
 evidence=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in proofs])
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
plan=read(O/'cross-game-causal-and-source-plan-v1.json');plan.update(wholePairedTextReviewed=True,pairedDirectReview=out.relative_to(ROOT).as_posix())
(O/'cross-game-causal-and-source-plan-v1.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf-8')
# Reviewhash is recorded before the plan changes its reviewedflag; preserve the
# directlyread wording and capture final plan hash in the request below.
request=O/'narration-cross-game-repair-request-v1.json';assert not request.exists()
mp=O/'tts-cross-game-repair-manifest-v1.json';m=read(mp)
protected=tts['protectedInputs']+tts['results']+[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [kp,ep,mp,out,O/'cross-game-causal-and-source-plan-v1.json',O/'cross-game-source-permissions-and-recent-use-v1.json',O/'space-enlarged-static-direct-review-v3.json',O/'cross-game-native-direct-review-v1.json']]
request.write_text(json.dumps(dict(schemaVersion=1,recordedAt=data['reviewedAt'],slug='game-math-orientation-matrices',manifest=mp.relative_to(ROOT).as_posix(),scriptReview=out.relative_to(ROOT).as_posix(),sourceReview='projects/game-math-orientation-matrices/revision-teaching-clarity-v1/cross-game-source-permissions-and-recent-use-v1.json',total=5,paragraphs=19,pairedWholeTextReview=True,overviewPromiseReview=True,baselineApprovedPcmRegeneration=0,existing6AdditivePcmRegeneration=0,protectedInputs=protected,
 scenes=[dict(id=s['id'],title=s['title'],text=' '.join(s['lines']),path=m['tts']['outputDir']+'/chunks/'+s['id']+'-scene.wav') for s in k['scenes']],
 preparedOnly=True,actualVoiceStarted=False,repairCandidateAdopted=False,measuredRatioApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
cp=read(O/'latest-checkpoint.json');cp.update(stage='cross-game-script-reviewed-currentduplicate-and-resource-pending',crossGamePairedScriptReview=out.relative_to(ROOT).as_posix(),crossGameVoiceRequest=request.relative_to(ROOT).as_posix(),next='Currentfull duplicate/content/Studio gate thenfreshGPU20s observer. Singlefiveitem voicebatch; preserve original24+6, scoped21firstparagraphcandidate requiresASR beforeadoption.')
(O/'latest-checkpoint.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(directPairs=19,voiceItems=5,original24And6Preserved=True,model=0)))
