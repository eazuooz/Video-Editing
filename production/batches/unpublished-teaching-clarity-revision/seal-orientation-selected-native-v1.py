"""Seal only the 379 listed pixels that were directly read, with observed failures."""
from pathlib import Path
import json, hashlib, datetime, subprocess

ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 return h.hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()

target=R/'selected-native-direct-review-v1.json'
assert not target.exists(), 'Preserve the existing review; write a follow-up version.'
m=read(R/'selected-native-v1/manifest.json')
ex=read(R/'selected-native-execution-v1.json')
baseline=read(R/'baseline-preservation-v1.json')
assert ex['workerExitCode']==0 and m['actualFfmpegExitCode']==0 and m['actualPtsMatch']
assert len(m['samples'])==379 and len(m['boards'])==68
assert all(sha(ROOT/x['path'])==x['sha256'] for x in m['samples']+m['boards'])
assert all(x['pts']==x['sourceFrame']*256 for x in m['samples'])
assert all(sha(ROOT/x['path'])==x['sha256'] for x in baseline['protectedFiles'])
live=subprocess.check_output(['powershell','-NoProfile','-Command',
 'Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(23788,75128) } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3'],text=True,encoding='utf8').strip()
assert not live, 'Check creation time and command before treating a reused PID as this worker.'
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
notes={
 ('02',0): ('Green world; clear banking at31–34 and45–49; dark/occluded at30 and51. Collision burst52, CRASHED/PLAY/MAPS/SETTINGS/QUIT menu53, restarted flight54. Whole original22–61 window is rejected.', 'hold-crash-menu-repair'),
 ('05',0): ('Pink world; arms/torso contrast sky at144–150,157–170 and174–179. Dark tunnel/occlusion155–156,172–173 requires hiding tracked guides or replacing the shot.', 'candidate-needs-tracking-and-continuity-review'),
 ('05',1): ('Different green/yellow world after the excluded portal. Clear body192–197; dark/hidden near190 and198–200. Announce a different flight segment; never infer one continuous transform.', 'candidate-needs-tracking-and-continuity-review'),
 ('08',0): ('Violet world; banking clear257–258,266–278. Near-wall silhouettes259,263–265 need a validity mask. Awesome+2000 UI260–261 remains clear; score is not evidence of matrix implementation.', 'candidate-needs-tracking-and-continuity-review'),
 ('08',1): ('Different gray world; body/edge comparison clear291–298 and300–305. Dark wall299; end305.867 lies in a narrow opening. No menu in the listed samples; no whole-window approval.', 'candidate-needs-tracking-and-continuity-review'),
 ('11',0): ('Pink/green world; visible banks353–356 and359–361. Dark wall364 and explicit CRASHED menu at364.983/f21899. Original351–365 is held.', 'hold-crash-menu-repair'),
 ('11',1): ('Same map restarted at370; pose clear373–376,380–384,388–390. Walls partly obscure body377–379 and393–395; body becomes visible396.983. Keep restart separate from preceding flight.', 'candidate-needs-tracking-and-continuity-review'),
 ('14',0): ('Bright green world; foreground perspective changes. Body silhouette clear510–513,522–524,529–537 and540–551. Red endpoint figures at517/526, spawn-like reset at517/527/539, and detached yellow cubes at538 suggest collision/restart intervals between samples. Hold the unsplit504–551.433 window and probe515–518,525–528,537–540 at exact native PTS.', 'hold-collision-restart-probe'),
 ('17',0): ('Orange/green world; pose clear609–620,625,630–639 and642–644. Dark corridor/body occlusion623–624,640–641,645–648. Smooth visible flight cannot establish internal orthonormality, controller inputs or drift.', 'candidate-needs-tracking-and-continuity-review'),
 ('20',0): ('Gold world/blue sky; pose strongly separated662–665,676–680 and688–693. Near wall670 and681–686 reduces contrast. Suitable body-versus-screen guide if it follows the visible body; not evidence of actual input mapping.', 'candidate-needs-tracking-and-continuity-review'),
 ('23',0): ('Gray/red world against bright white sky offers the strongest body contrast822–824,831–832,839–847 and854–861. New Highscore858–860 is unrelated UI to leave unobscured. Dark wall segments827–829 and848–853 need masking. Prefer part of this interval as the first body-pose observation, then reassign later retrieval to distinct reviewed frames rather than repeat it.', 'preferred-clear-first-observation-candidate-not-adopted'),
}
windows=[]
for w in m['windows']:
 key=(w['scene'],w['segment']); n,status=notes[key]
 boards=[x for x in m['boards'] if (x['scene'],x['segment'])==key]
 windows.append({**w,'allSamplesDirectlyRead':True,'boardCountRead':len(boards),'boards':boards,
                 'observation':n,'decision':status,'wholeFramesApproved':False,'finalCueApproved':False})
review={'observedAt':stamp,'manifest':rel(R/'selected-native-v1/manifest.json'),
 'actualOuterExitCode':0,'outerExitObservedChunk':'c257a0','processAbsenceObservedChunk':'9c81e9',
 'freshProcessAbsenceVerified':True,'actualSessionId':46706,'all379ListedSamplesDirectlyRead':True,
 'all68BoardsDirectlyRead':True,'allSampleAndBoardHashesMatched':True,'ptsContract':'nativeFrame*256 / 15360',
 'baselineProtectedFilesUnchanged':len(baseline['protectedFiles']),'windows':windows,
 'explicitMenusObserved':[{'nativeFrame':3180,'pts':814080,'seconds':53.0,'scene':'02'},
                          {'nativeFrame':21899,'pts':5606144,'seconds':364.98333333333335,'scene':'11'}],
 'limits':{'allIntermediateFramesRead':False,'fullContinuousListening':False,'newNativeInOutAdopted':False,
           'sourceGeometryTracked':False,'engineWorldAxesMeasured':False,'finalCueAndCreditReviewed':False,
           'dependentNarrationApproved':False,'newTtsStarted':False,'newFinalMediaApproved':False,
           'publicRightsApproved':False,'humanListeningApproved':False},
 'next':'Probe collision/reset edges and unused brighter intervals; choose distinct actual-action windows, then prepare narrated moving-body/reference guides and only necessary prerequisite bridges.'}
write(target,review)
ex.update({'actualOuterExitCode':0,'sessionId':46706,'outerExitObservedChunk':'c257a0',
           'processAbsenceObservedChunk':'9c81e9','status':'completed-listed-pixels-reviewed-source-repair-required',
           'allSelectedPixelsRead':True,'allIntermediateFramesRead':False,'directReview':rel(target)})
write(R/'selected-native-execution-v1.json',ex)
cp=read(R/'latest-checkpoint.json');cp.update({'observedAt':stamp,'stage':'listed-native-pixels-reviewed-crash-repair-required',
 'selectedNativeDirectReview':rel(target),'nativeSamplesRead':379,'nativeBoardsRead':68,
 'allSelectedNativeCutsApproved':False,'next':review['next']});write(R/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json';q=read(qp)
item=next(x for x in q['items'] if x['slug']=='game-math-orientation-matrices')
item['selectedNativeReview']=rel(target);item['review']['comparisonScope']='50 initial audit samples plus379 exact-PTS native samples/68 boards; two explicit menus and three suspected collision/reset ranges held; new final approval pending'
old=q['execution'];job=old.get('ownedJob')
if job: old.setdefault('completedOwnedJobs',[]).append({**job,'actualSessionId':46706,'actualOuterExitCode':0,'outerExitObservedChunk':'c257a0','directReview':rel(target)})
old.update({'ownedJob':None,'stage':cp['stage'],'next':cp['next'],'orientationSelectedNativeReview':rel(target)})
q['updatedAt']=stamp;write(qp,q)
print(json.dumps({'samplesRead':379,'boardsRead':68,'protectedUnchanged':len(baseline['protectedFiles']),'explicitMenuFailures':2,'nativeAdoption':False}))
