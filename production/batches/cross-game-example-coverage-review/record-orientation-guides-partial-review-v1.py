"""Preserve direct sample review progress without claiming all eight scenes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=O/'current34-guides-pixel-execution-v1.json';s=rd(sp)
assert s['actualOuterExitCode']==0 and s['workerDead']
out=O/'current34-guides-partial-direct-review-v1.json';assert not out.exists()
starts={'02':.195401,'05':.170538,'08':.175021,'11':.169445,'14':.183793,'17':.17525,'20':.1531,'23':.168416}
ends={'02':39.,'05':49.,'08':47.883333,'11':41.,'14':47.433333,'17':47.,'20':35.,'23':49.85}
notes={
 '02':'Cyan torso observation and red screen-displacement segment follow the visible subject; annotations are hidden after the observed bracket and do not claim a game-world axis. Upper labels and uncaptioned bottom region clear in selected samples.',
 '05':'Cyan torso screen point follows rotation. Gold image-up remains a screen reference, not a body/world axis; hidden after its short demonstration. Native source cut has no fake path interpolation.',
 '08':'Cyan point follows the torso through banking/inversion; it is hidden before subsequent source cuts. No angular rate or engine-axis measurement is claimed.',
 '11':'Cyan point follows the black wing-suit torso during clear intervals. It is hidden for uncertain small/occluded brackets, including1619–1681 and1739–1770; later cut frames have no false motion trail. Labels and source score UI remain readable in selected samples.'}
rows=[]
for r in s['results']:
 assert sha(ROOT/r['video'])==r['videoSha256'] and r['extractExitCode']==0
 done=r['id'] in notes
 if done:
  for x in r['samples']+r['boards']:assert sha(ROOT/x['path'])==x['sha256']
 rows.append(dict(scene=r['id'],video=r['video'],videoSha256=r['videoSha256'],allSamplesDirectlyRead=done,directlyReadSampleCount=len(r['samples']) if done else 0,directlyReadBoardCount=len(r['boards']) if done else 0,samples=r['samples'] if done else [],boards=r['boards'] if done else [],observation=notes.get(r['id'],'Encoded samples await direct reading.'),normalPlayback=dict(tabId='108',url='http://127.0.0.1:9250/orientation-current34-baseline-guides-v1-review.html',startTime=starts[r['id']],endTime=ends[r['id']],duration=ends[r['id']],rate=1,muted=True,runningAtStart=True,endedAtEnd=True,scope='Actual normal UI start/end; not all intervening frames or continuous listening.')))
assert sum(r['directlyReadSampleCount'] for r in rows)==274 and sum(r['directlyReadBoardCount'] for r in rows)==70
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),extraction=sp.relative_to(ROOT).as_posix(),extractionSha256=sha(sp),rows=rows,directlyReadScenes=['02','05','08','11'],pendingDirectScenes=['14','17','20','23'],directlyReadSamples=274,directlyReadBoards=70,pendingSamples=288,pendingBoards=74,normalPlaybackEndpointsReviewedAll8=True,all8EncodedScenesApproved=False,allInterveningFramesReviewed=False,final244CaptionPixelsApproved=False,newImageGit=0),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(directScenes=4,samples=274,boards=70,normalEndpoints=8,pendingBoards=74,finalPixels=False)))
