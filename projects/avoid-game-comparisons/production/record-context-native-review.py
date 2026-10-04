"""Record direct review decisions after reading all independent ASR and native sheets."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / 'projects/avoid-game-comparisons/production'
PROOF = ROOT / 'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons'
now = datetime.now(timezone.utc).isoformat()

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

request = read(PROD / 'independent-context-readback-request.json')
for item in request['protectedInputs']:
    assert sha(ROOT / item['path']) == item['sha256'], item['path']
state = read(PROD / 'independent-context-asr-execution.json')
assert state['exitCode'] == 0 and len(state['results']) == 10
decisions = {
    '01-name': ('retain-current-PCM', 'Independent complete sentence recognizes 플러키 스콰이어 correctly; full-scene 스쿼이어 variant remains historical ASR uncertainty. No listening or pronunciation approval claimed.'),
    '02-final': ('retain-current-PCM', 'Independent complete final paragraph matches all intended words and contains no added credit. Whole-scene near-zero-time appended credit is preserved as recognition discrepancy; not approval by ending heuristic.'),
    '04-name': ('retain-with-human-pronunciation-pending', 'Independent paragraph is complete; 플럭키 versus 플러키 consonant spelling remains uncertain. No extra paragraph or omitted action.'),
    '04-ending': ('retain-with-particle-note', 'Both sentences and virtual-game-desk limitation present; 의 recognized 에. Full-scene end-timestamp warning preserved.'),
    '06-first': ('targeted-clarity-repair-required', 'Independent full paragraph again recognizes 용암 위기를 rather than 용암 위 길을. Clarify only this action paragraph while preserving all explanation PCM and all unaffected action samples.'),
    '09-two-paragraphs': ('retain-white-explanation-PCM', '세/새 homophone remains an orthographic ASR ambiguity. First, second and third ordered steps are present. Third-sentence particle differs; content and order preserved, human pronunciation pending.'),
    '10-divided-cuts': ('targeted-clarity-repair-required', 'Independent complete paragraph again recognizes 컷이 아닙니다 rather than 컷이 나뉩니다, changing the claim. Clarify only this action paragraph before technical approval.'),
    '11-question': ('retain-white-explanation-PCM-with-word-note', '맞히는 recognized 맞추는 independently; intended request to check listener understanding and action rather than identify a title remains present. Pronunciation approval pending.'),
    '11-restatement': ('retain-white-explanation-PCM-with-particle-note', 'Independent paragraph recognizes 되말하기 correctly, resolving whole-scene 대말하기 discrepancy. Quoted 들어간다라면 recognized 들어간다면; preserve note and current explanation PCM.'),
    '11-same-action': ('retain-white-explanation-PCM', 'Independent complete paragraph recognizes 같게 correctly and all remaining goals, unknown conditions and supplement-only-needed-sentences content; no omission/repetition/extra greeting.'),
}
results = []
for item in state['results']:
    assert sha(ROOT / item['audioPath']) == item['audioSha256']
    assert sha(ROOT / item['contextAudioPath']) == item['contextAudioSha256']
    decision, note = decisions[item['id']]
    item['directReview'] = True
    item['decision'] = decision
    item['reviewNote'] = note
    results.append({k: item[k] for k in ['id','scene','audioPath','audioSha256','fromSeconds','toSeconds','expected','text','contextAudioSha256','decision','reviewNote']})
review = dict(schemaVersion=1, reviewedAt=now, method='All10 independent unprompted current-PCM context results directly compared with complete corresponding script paragraphs and prior full-scene ASR; no human listening claim.', requestSha256=sha(PROD/'independent-context-readback-request.json'), allContextsDirectlyReviewed=True, results=results, targetedRepairScenes=['06','10'], unchangedWhiteExplanationScenes=['01','03','05','07','09','11'], protectedInputsUnchanged=True, narrationApproved=False, finalMixAsrReviewed=False, humanWholeListening='pending', humanPronunciation='pending', newGitImages=0)
save(PROD/'independent-context-direct-review.json', review)
state.update(directContextReview=True, directReviewFile='projects/avoid-game-comparisons/production/independent-context-direct-review.json', status='direct-review-complete-targeted-06-10-clarity-repair-pending', updatedAt=now, actualWorkerClosed=True, cpuJobs=0, gpuJobs=0, narrationApproved=False)
save(PROD/'independent-context-asr-execution.json',state)
full = read(PROD/'narration-full-script-direct-review.json')
full['independentContextReview'] = {'path':'projects/avoid-game-comparisons/production/independent-context-direct-review.json','directlyReviewed':True,'targetedRepairScenes':['06','10'],'narrationApproved':False}
full['updatedAt'] = now
save(PROD/'narration-full-script-direct-review.json',full)

native_path = PROOF/'source-research/native-review-additional-measured-actions.json'
native = read(native_path)
sheets = []
for source in native['sources']:
    for key in ['actionSheets','boundarySheets']:
        for item in source[key]:
            assert sha(ROOT/item['path']) == item['sha256']
            sheets.append({**item,'videoId':source['videoId'],'type':key,'directlyRead':True})
    source['status'] = 'all-native-sheets-directly-read-cross-source-duplicate-review-pending'
assert len(sheets) == 19
native.update(status='all-native-sheets-directly-read-cross-source-duplicate-review-pending', sessionId=27040, exitCode=0, actualWorkerClosed=True, updatedAt=now, directReviewFile='production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research/direct-native-additional-measured-actions.json')
observations = {
 'KWDk-csu460': {
  'safeCandidateRangesSeconds':[[10,434/30],[434/30,18.5],[26.5,28],[42,43.5],[51,52.5],[55,57.2]],
  'boundaries':'n434 hard cut at14.466667. Alpha/prototype/wipe at9/9.5 excluded; final cave starts10. Level-prototype wipe by18.966667, conservative end18.5. Boss wipe26/28.5 excluded. Mechanical test41/41.5 excluded; final action42+. Test→water n1512/50.4 directly observed. n1719/57.3 white flash and n1725–1728 logo transition excluded by57.2 end.',
  'duplicateHold':'Final water attack, cauldron and green mech may overlap z4/DRILL; do not count until direct comparison. Cave and column also require comparison to prior cave/columns.',
  'captionHold':'Final-gameplay label along bottom may overlap fixed narration box; trim/composition and every final cue must be reviewed.',
 },
 'MJSMqtG0Kcs': {
  'hardEditFrames':[1037,1133,1242,1432,1941,2090,2179,2292,2380,2555,2656,2722,2835,2884,2940,3067,3157,3229,3294,3377,3529],
  'boundaries':'17.283 bomb-page action starts;18.883 industrial lift cut;20.7 boss-name introduction excluded.23.866667 tree-root action,25–28 city and portal to virtual3D desk.32.35 wide tree desk cut,34.833333 pencils,36.316667 dark desk,38.2 flat mug,39.666667 printed shelf→miniroom,42.583333 printed castle,44.266667 combat/explosion montage held,45.366667 book ruins exit,47.25 caterpillar edit and48.066667 wider cut,49 beach minigame,51.116667 topdown combat,52.616667 accordion stairs,53.816667 repeated tree shot,54.9 rocket,56.283333 flags,58.816667 title.',
  'duplicateHold':'Compare industrial combat/city portal/printed castle/mug/accordion stairs/rocket/flags with original Jd,WFI,Rocket.53.816667 tree is same source shot as23.866667 and cannot count again.',
  'claimLimits':'No arbitrary wall entry, puzzle unlock condition, stealth/light-carrying rule or actual player causality inferred from edited cuts. Old2023 release promise/title excluded. Desk is game virtual environment; no real-hands footage.',
  'captionHold':'Desk avatar near bottom and beach health/UI conflict require final composition/cue review; beach can be excluded rather than hiding UI. No captions moved.',
 }
}
save(PROOF/'source-research/direct-native-additional-measured-actions.json',dict(schemaVersion=1, reviewedAt=now, nativeState=native_path.relative_to(ROOT).as_posix(), actionSamples=123, boundaryCandidates=49, sheets=19, allSheetsDirectlyRead=True, sheetsEvidence=sheets, observations=observations, approvedIntervals=[], approvedActualSeconds=0, finalCutAndCaptionApproval=False, bodyRatioApproved=False, sourceAudioUsed=False, newGitImages=0))
save(native_path,native)
queue_path = ROOT/'production/batches/sakurai-planning-game-design/queue.json'
queue=read(queue_path)
task=next(x for x in queue['items'] if x['slug']=='avoid-game-comparisons')
task.update(stage='targeted-narration-clarity-and-unique-source-expansion',updatedAt=now,nextAction='Preserve all6 white explanation PCM and10 unaffected scene PCM. Prepare targeted06-first/10-paragraph2 clarity repair; verify current duplicate gate and actual GPU availability. Directly compare new sources with old bank before approving new action intervals; obtain additional unique official actions if required. No final ratio/render/upload yet.')
task['independentContextReadback']={'state':'projects/avoid-game-comparisons/production/independent-context-asr-execution.json','status':state['status'],'results':10,'directReview':True,'review':state['directReviewFile'],'narrationApproved':False}
task['sourceExpansionNativeReview']={'state':native_path.relative_to(ROOT).as_posix(),'status':native['status'],'all19SheetsRead':True,'approvedActualSeconds':0,'finalCutApproval':False}
task['execution'].update(observedAt=now,status='closed-context-and-native-workers-independent-review-complete',alive=False,activeTasks=[],gpuSynthesisJobs=0,cpuProductionJobs=0,renderJobs=0,uploads=0)
task['execution']['sourceNativeJobs']=0
task['narrationReadback']['independentContextsDirectReview']=True
queue.update(updatedAt=now,lastProgressAt=now)
save(queue_path,queue)
for path in [PROD/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    cp=read(path)
    for key in ['stage','updatedAt','nextAction','execution','independentContextReadback','sourceExpansionNativeReview']:
        cp[key]=task[key]
    save(path,cp)
print(json.dumps({'contextsReviewed':10,'nativeSheetsReviewed':19,'targetedRepairsPending':['06','10'],'newActualSecondsApproved':0,'allProtectedInputsUnchanged':True,'newGitImages':0}))
