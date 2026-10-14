"""Persist current final board and two motion observations; keep Rivalry opening unresolved."""
from pathlib import Path
import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=m.ROOT/'projects/game-lighting-history-04/production'
data=json.load(sys.stdin);exPath=P/'part1-road-final-pixel-qa-execution-v335.json';ex=m.read(exPath)
assert ex['status']=='complete' and ex['exitCode']==0 and len(ex['boards'])==17
pair=m.read(P/'part1-reviewed-pair-build-v333.json');assert ex['sourceSha256']==pair['captioned']['sha256']
target=P/'part1-road-final-direct-review-v337.json';assert not target.exists()
observed={x['board']:x for x in data['boards']};assert set(observed)==set(range(1,18));records=[]
for row in ex['boards']:
 o=observed[row['board']];assert o['allConstituentFramesDirectlyRead'] and o['actualObservation'].strip()
 assert m.sha(m.ROOT/row['path'])==row['sha256']
 records.append(dict(row,**{k:v for k,v in o.items() if k!='board'},reviewedAt=m.stamp()))
request=m.read(P/'part1-current-moving-review-request-v325.json')
rows={x['id']:x for x in request['rows']}
assert {x['id'] for x in data['motion']}=={'geometry-road-mask:native','geometry-barrier-views:native'}
for o in data['motion']:
 assert o['rangeSeconds']==rows[o['id']]['ranges'][0] and o['fullSelectedIntervalActuallyPlayed'] and o['playbackRate']==1
 assert o['normalSpeedPixelsApproved'] and o['actualObservation'].strip() and not o['issues']
 o['reviewedAt']=m.stamp()
proof=dict(reviewedAt=m.stamp(),sourceSha256=ex['sourceSha256'],extraction=dict(path=m.rel(exPath),sha256=m.sha(exPath)),boards=records,motion=data['motion'],all17BoardsDirectlyRead=True,allFinalPixelsReviewed=False,qaApproved=False,newGitImages=0,humanWholeListening='pending',unresolvedIssues=[dict(board=x['board'],issue=i) for x in records for i in x['issues']],historicalRoadFailurePreserved=True)
assert len(proof['unresolvedIssues'])==2
m.save(target,proof);print(json.dumps(dict(boards=17,approvedMovingIntervals=2,remainingOpeningIssue=True)))
