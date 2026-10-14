"""Seal the 358 listed native pixels actually read; retain all adoption holds."""
from pathlib import Path
import datetime, hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def write(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def rel(p): return p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''): h.update(b)
    return h.hexdigest()

target = R / 'repair-candidate-direct-review-v1.json'
assert not target.exists(), 'Preserve the existing review and write a follow-up.'
m = read(R/'repair-candidate-native-v1/manifest.json')
ex = read(R/'repair-candidate-execution-v1.json')
baseline = read(R/'baseline-preservation-v1.json')
assert ex['workerExitCode'] == 0 and m['actualFfmpegExitCode'] == 0 and m['actualPtsMatch']
assert len(m['samples']) == 358 and len(m['boards']) == 66
assert all(sha(ROOT/x['path']) == x['sha256'] for x in m['samples']+m['boards'])
assert all(x['pts'] == x['sourceFrame']*256 for x in m['samples'])
assert all(sha(ROOT/x['path']) == x['sha256'] for x in baseline['protectedFiles'])
live = subprocess.check_output(['powershell', '-NoProfile', '-Command',
    'Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(79316,79228) } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'], text=True, encoding='utf8').strip()
assert not live, 'Compare creation and command before treating a reused PID as this job.'
notes = {
 'event02': '51.5–51.9 dark flight;52.0 collision burst;52.1–52.4 detached/dead body and red277. CRASHED menu directly visible52.5–53.1.53.2 transition;53.3 normal restarted flight. Sparse0.1s samples bound observations, not exact onset. Exclude51–54 conservatively.',
 'event11': '364.0–364.2 flight;364.3 impact;364.4–364.7 dead body/red15 72. CRASHED directly visible364.8–365.1;365.183 restarted body. Candidate350–364 and370–397 keeps41 seconds while excluding collision/menu, but requires final cue/continuity review.',
 'event14a': '515–516.4 mostly dark flight.516.5 impact;516.6–516.8 dead body/red13 91;516.9 reset;517–517.983 body at new flight start. No CRASHED menu in the listed14a samples; do not infer unseen frames.',
 'event14b': '525–525.5 near portal;525.6 impact/Awesome2000;525.7–526.0 dead body/red21 37. CRASHED menu526.1–526.3;526.4 reset.526.8–527.983 clear new flight. Hold the original unsplit scene14.',
 'event14c': '537–537.5 body over purple portal structure;537.6 approaching surface;537.7 impact;537.8–538.1 detached yellow cubes/dead state. CRASHED538.2;538.3 reset.538.8–539.983 restarted flight. Hold unsplit original scene14.',
 'unused83': '83–100 gray/green map: many wall occlusions, small body and score overlays;86–91 and98–99 offer isolated clearer silhouettes.101 Portal changes to cyan;104–105 obscured,106–110 silhouettes,111–116 wall occlusion;123–125 and137–140 clearer.131 Portal changes to pink. Reject the entire83–143 range as one continuous transform; not preferred for the first explanation.',
 'unused403': '403–409 flight against yellow sky;407–409 especially clear.411–416 dark edge but silhouette readable,417–426 alternating turns/occlusions.427–428 Portal changes green map.433–447 arms/body are clear against bright sky;448–450 reduce contrast,451–460 mixed occlusions,461–467 dark. CRASHED468;469 reset.477–479 clear portal approach,480–485 mostly dark. CRASHED486,492;499 dead body,500 reset. Only short individual clear candidate intervals are retained; never adopt403–504 whole.',
 'unused871': 'Gray/red/white map continues with strong silhouettes871–878.879–883 mixed wall contrast;884–886 Portal transition,887–889 tiny body.891–896 and901–908 offer clear turns against white background;899–900 and909–912 reduce contrast.914–916 Portal changes to green,917–921.983 green flight/dark edge. No menu in these listed samples, but whole continuity is not approved. Prefer871–878 as a distinct retrieval or observation; split any map transition.',
 'extend19': '19–19.5 body against pale sky,20–20.5 partly wall-adjacent,21–21.983 tiny body beside structure. Normal flight in listed samples but weaker first-time clarity than bright gray/red sequence.',
 'extend350': '350 and350.5 body partly blends into terrain;350.983 clearly silhouetted against pink sky. Suitable one-second extension before351 if continuous final playback/cue review passes.'
}
windows = []
for w in m['windows']:
    boards = [x for x in m['boards'] if x.get('window') == w['name']]
    if not boards: boards = [x for x in m['boards'] if Path(x['path']).name.startswith(w['name']+'-board-')]
    windows.append({**w, 'listedSamplesDirectlyRead': True, 'boardCountRead': len(boards), 'boards': boards,
                    'observation': notes[w['name']], 'footageAdopted': False, 'allFramesApproved': False,
                    'finalCreditCaptionUiApproved': False})
stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
review = {'observedAt': stamp, 'manifest': rel(R/'repair-candidate-native-v1/manifest.json'),
 'actualSessionId':39906, 'actualOuterExitCode':0, 'outerExitObservedChunk':'5adb6b',
 'workerPid':79316, 'workerCreateTime':1791673014.228864, 'workerGenerationNoLongerAlive':True,
 'pidReuseObservation':'At07:59:40KST PID79316 appeared with a later07:59:40.608785 creation and NULL command. It was a different generation, not this completed worker; no process was manipulated. Fresh query now contains neither worker PID.',
 'all358ListedSamplesDirectlyRead':True, 'all66BoardsDirectlyRead':True,
 'allSampleAndBoardHashesMatched':True, 'ptsContract':'nativeFrame*256 /15360',
 'baselineProtectedFilesUnchanged':len(baseline['protectedFiles']), 'windows':windows,
 'explicitMenusObserved':[{'seconds':52.5,'frame':3150,'pts':806400}, {'seconds':364.8,'frame':21888,'pts':5603328},
                         {'seconds':526.1,'frame':31566,'pts':8080896}, {'seconds':538.2,'frame':32292,'pts':8266752},
                         {'seconds':468,'frame':28080,'pts':7188480}, {'seconds':486,'frame':29160,'pts':7464960},
                         {'seconds':492,'frame':29520,'pts':7557120}],
 'limits':{'allIntermediateFramesRead':False,'exactEventBoundariesApproved':False,'fullContinuousListening':False,
           'sourceAdoptionApproved':False,'trackedAnnotationApproved':False,'dependentTtsStarted':False,
           'newFinalMediaApproved':False,'humanListeningApproved':False,'publicRightsApproved':False},
 'next':'Use distinct clear gray/white flight first. Prepare conservative split source plan excluding every observed collision/menu/portal, compare actual normal-speed proposed actions, then review a moving-body/reference annotation pilot. Preserve useful original narration and measure only necessary added bridges.'}
write(target, review)
ex.update({'sessionId':39906,'actualOuterExitCode':0,'outerExitObservedChunk':'5adb6b',
 'status':'completed-listed-pixels-reviewed-conservative-recut-required','directReview':rel(target),
 'allListedPixelsRead':True,'allIntermediateFramesRead':False,'workerGenerationNoLongerAlive':True})
write(R/'repair-candidate-execution-v1.json', ex)
cp=read(R/'latest-checkpoint.json');cp.update({'observedAt':stamp,'stage':'repair-candidate-pixels-reviewed-conservative-recut-required',
 'repairCandidateDirectReview':rel(target),'repairCandidateSamplesRead':358,'repairCandidateBoardsRead':66,
 'next':review['next']});write(R/'latest-checkpoint.json',cp)
plan=read(R/'causal-flow-and-annotation-plan-v1.json')
plan['bridgeFullKoEnDirectComparisonApproved']=True
plan['bridgeFullKoEnReviewAt']=stamp
plan['bridgeReviewScope']='All six paired prepared paragraphs directly compared: meanings/order match; retained original140KOEN/24claims and source conventions checked. This approves prepared wording only, not source adoption, timing or final mixed voice.'
plan['sourceHold']=['scene02 observed52.5–53.1 menu','scene11 observed364.8–365.1 menu','scene14 observed collisions/reset and526.1–526.3/538.2 menus; unsplit source rejected']
write(R/'causal-flow-and-annotation-plan-v1.json',plan)
qp=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qp)
item=next(x for x in q['items'] if x['slug']=='game-math-orientation-matrices')
item['repairCandidateReview']=rel(target)
item['review']['comparisonScope']='50 initial samples;379 selected-native samples/68 boards;358 repair samples/66 boards all directly read/hash sealed. Conservative recut and tracked annotation remain pending.'
execution=q['execution'];job=execution.get('ownedJob')
if job: execution.setdefault('completedOwnedJobs',[]).append({**job,'actualSessionId':39906,'actualOuterExitCode':0,'outerExitObservedChunk':'5adb6b','directReview':rel(target)})
execution.update({'ownedJob':None,'stage':cp['stage'],'next':cp['next'],'orientationRepairCandidateReview':rel(target)})
q['updatedAt']=stamp;write(qp,q)
print(json.dumps({'samplesRead':358,'boardsRead':66,'baselineProtectedUnchanged':38,'sourceAdoption':False,'bridgeWordingPreparedReview':True}))
