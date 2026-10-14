"""Seal actual CUA normal endpoints and completed direct guide-board review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):
 assert not p.exists()
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
now=datetime.now(timezone.utc).isoformat()
samplep=O/'current34-detailed-explanations-sampled-direct-review-v1.json';sample=rd(samplep)
assert sample['all605SamplesDirectlyRead'] and sample['all109BoardsDirectlyRead']
normal=[('03',.200005,34.6),('04',.192047,33.25),('06',.189485,32.533333),('07',.184176,36.766667),('09',.184579,35.633333),('10',.1897,37.933333),('13',.189709,32.516667),('15',.191163,37.566667),('16',.175544,39.),('21',.190085,31.233333),('22',.194149,35.166667),('12',.185209,32.681706),('06a',.182804,12.633008),('09a',.189393,14.06569),('13a',.191686,14.866016),('16a',.192593,15.349023),('21a',.193522,14.266667)]
rows=[]
for sid,start,end in normal:
 r=next(x for x in sample['rows'] if x['scene']==sid)
 assert sha(ROOT/r['video'])==r['videoSha256']
 rows.append(dict(scene=sid,video=r['video'],videoSha256=r['videoSha256'],start=dict(time=start,duration=end,paused=False,rate=1,muted=True),end=dict(time=end,duration=end,paused=True,ended=True,rate=1,muted=True)))
np=O/'current34-detailed-explanations-normal-direct-review-v1.json'
write(np,dict(recordedAt=now,sampledReview=samplep.relative_to(ROOT).as_posix(),sampledReviewSha256=sha(samplep),tabId='110',url='http://127.0.0.1:9250/orientation-current34-detailed-review-v1.html',rows=rows,all17NormalStartEndObserved=True,normalPlaybackReviewed=True,allInterveningFramesReviewed=False,continuousListeningApproved=False,final244CaptionPixelsApproved=False,scope='Actual CUA UI play clicks and read-only DOM running/start plus ended endpoints; some videos overlapped. Selected moving samples separately directly inspected; not continuous whole-scene watching or listening.',newImageGit=0))
partialp=O/'current34-guides-partial-direct-review-v1.json';partial=rd(partialp)
sp=O/'current34-guides-pixel-execution-v1.json';s=rd(sp)
assert s['workerDead'] and s['actualOuterExitCode']==0
planp=O/'current34-baseline-guide-plan-v2.json';plan=rd(planp)
assert plan['currentNarrationGuideTimingDirectlyReviewed']
notes={
 '14':'Source cut at840 starts the cyan observation. Torso samples885–975 are clear; hidden in989–1065 terrain-overlap bracket, visible again1080–1199, and hidden from1200. Later native cuts1860/2340/2700 carry no interpolated path. Labels and score UI preserved in selected samples.',
 '17':'Cyan torso point appears at1500 and follows changing visible attitudes to1859; hidden at1860 and in later occluded samples. Label explicitly distinguishes visible posture from measured internal numerical error. No engine-error or world-axis inference.',
 '20':'Cyan torso point follows the selected1620–1745 samples and hides at1746; later1759 samples are unmarked. Earlier camera/terrain occlusion and the later fall are unmarked. The label identifies observable posture and states input method is unverified.',
 '23':'Cyan point follows clear torso samples600–675, is hidden by689 through780, follows795–959, and hides at960. Gold image-up appears1015–1504 and is explicitly a screen reference, not body/world axes. Cyan stays hidden for the small/occluded subject. Source cut1380 changes the world without path interpolation; all annotations end at1505. Later native cuts and score UI remain native.'}
grows=[]
for r in s['results']:
 old=next(x for x in partial['rows'] if x['scene']==r['id'])
 assert sha(ROOT/r['video'])==r['videoSha256'] and r['extractExitCode']==0
 for x in r['samples']+r['boards']:assert sha(ROOT/x['path'])==x['sha256']
 grows.append(dict(scene=r['id'],video=r['video'],videoSha256=r['videoSha256'],samples=r['samples'],boards=r['boards'],allSamplesDirectlyRead=True,observation=notes.get(r['id'],old['observation']),normalPlayback=old['normalPlayback'],priorDirectReviewReused=r['id'] not in notes))
assert sum(len(x['samples']) for x in grows)==562 and sum(len(x['boards']) for x in grows)==144
gp=O/'current34-baseline-guides-direct-review-v1.json'
write(gp,dict(recordedAt=now,extraction=sp.relative_to(ROOT).as_posix(),extractionSha256=sha(sp),priorPartialReview=partialp.relative_to(ROOT).as_posix(),priorPartialReviewSha256=sha(partialp),plan=planp.relative_to(ROOT).as_posix(),planSha256=sha(planp),rows=grows,allPlannedEncodedSamplesDirectlyRead=True,all562SamplesDirectlyRead=True,all144BoardsDirectlyRead=True,normalPlaybackReviewed=True,normalPlaybackEndpointsReviewedAll8=True,currentNarrationTimingReviewed=True,timingScope='Guide meaning/reveal brackets use the previously reviewed current AAC placement plan. Final combined244 caption pixels still pending.',all8EncodedScenesApproved=True,allInterveningFramesReviewed=False,final244CaptionPixelsApproved=False,physicalCentroidMeasured=False,gameWorldAxesMeasured=False,newImageGit=0))
proof=rd(O/'narration-07b-guide-repair-execution-v1.json')
for x in proof['protectedInputs']+proof['results']:assert sha(ROOT/x['path'])==x['sha256']
print(json.dumps(dict(detailNormalEndpoints=17,guideSamples=562,guideBoards=144,protected79=True,candidate=True,finalPixels=False)))
