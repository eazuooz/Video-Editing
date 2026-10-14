"""Save explicit direct observations; never infer review from files or playback events."""
from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
data=json.load(sys.stdin)
mode=data['mode']
assert mode in ['boards','motion']
if mode=='boards':
 sourcePath=P/'part1-final-pixel-review-execution-v294.json';source=read(sourcePath)
 assert source['status']=='complete' and source['exitCode']==0
 path=P/'part1-final-board-direct-progress-v297.json'
 record=read(path) if path.exists() else dict(startedAt=stamp(),sourceSha256=source['sourceSha256'],extractionSha256=sha(sourcePath),records=[],unresolvedIssues=[],allFinalPixelsReviewed=False,newGitImages=0)
 assert record['sourceSha256']==source['sourceSha256'] and record['extractionSha256']==sha(sourcePath)
 known={r['board']:r for r in record['records']};expected={r['board']:r for r in source['boards']}
 for observation in data['records']:
  number=observation['board'];assert number in expected and number not in known,'Preserve a prior observation'
  original=expected[number];assert sha(ROOT/original['path'])==original['sha256']
  assert observation['actualObservation'].strip() and observation['allConstituentFramesDirectlyRead'] is True
  row=dict(original,**{k:v for k,v in observation.items() if k!='board'},directlyRead=True,reviewedAt=stamp())
  known[number]=row
 record['records']=[known[n] for n in sorted(known)]
 record['unresolvedIssues']=[{'board':r['board'],'issue':issue} for r in record['records'] for issue in r.get('issues',[])]
 record['allFinalPixelsReviewed']=len(known)==len(expected) and not record['unresolvedIssues']
else:
 sourcePath=P/'part1-final-moving-review-request-v295.json';source=read(sourcePath)
 path=P/'part1-final-moving-direct-progress-v298.json'
 record=read(path) if path.exists() else dict(startedAt=stamp(),sourceSha256=source['sourceSha256'],requestSha256=sha(sourcePath),records=[],unresolvedIssues=[],allFinalMovingPixelsReviewed=False,newGitImages=0,humanWholeListening='pending')
 assert record['sourceSha256']==source['sourceSha256'] and record['requestSha256']==sha(sourcePath)
 known={r['id']:r for r in record['records']};expected={r['id']:r for r in source['rows']}
 for observation in data['records']:
  key=observation['id'];assert key in expected and key not in known,'Preserve a prior observation'
  assert observation['actualObservation'].strip() and observation['fullSelectedIntervalActuallyPlayed'] is True and observation['playbackRate']==1
  assert observation['rangeSeconds']==expected[key]['ranges'][0]
  known[key]=dict(observation,reviewedAt=stamp())
 record['records']=[known[r['id']] for r in source['rows'] if r['id'] in known]
 record['unresolvedIssues']=[{'id':r['id'],'issue':issue} for r in record['records'] for issue in r.get('issues',[])]
 record['allFinalMovingPixelsReviewed']=len(known)==len(expected) and not record['unresolvedIssues'] and all(r['normalSpeedPixelsApproved'] for r in known.values())
 for key in ['fourGameDifferencesAndCommonPrincipleDirectlyReviewed','originalIntroMembershipAndFixedCaptionStyleDirectlyReviewed']:
  if key in data:record[key]=data[key]
record['updatedAt']=stamp()
temporary=path.with_suffix('.writing.json');temporary.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');temporary.replace(path)
print(json.dumps({'mode':mode,'directlyReviewed':len(record['records']),'total':len(expected),'unresolved':len(record['unresolvedIssues']),'complete':record.get('allFinalPixelsReviewed',record.get('allFinalMovingPixelsReviewed'))}))
