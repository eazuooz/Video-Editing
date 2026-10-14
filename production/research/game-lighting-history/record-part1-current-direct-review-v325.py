"""Persist explicit observations against the current final source; preserve historical issues."""
from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=lambda:datetime.now(timezone.utc).isoformat()
data=json.load(sys.stdin);mode=data['mode'];assert mode in ['boards','motion']
if mode=='boards':
 sourcePath=P/'part1-current-pixel-qa-execution-v327.json'; source=read(sourcePath)
 assert source['status']=='complete' and source['exitCode']==0
 path=P/'part1-current-board-direct-progress-v325.json'
 record=read(path) if path.exists() else dict(startedAt=stamp(),sourceSha256=source['sourceSha256'],extractionSha256=sha(sourcePath),records=[],allNewCurrentBoardsDirectlyRead=False,newGitImages=0,historicalIssuesPreserved=True)
 assert record['sourceSha256']==source['sourceSha256'] and record['extractionSha256']==sha(sourcePath)
 known={r['board']:r for r in record['records']};expected={r['board']:r for r in source['boards']}
 for observation in data['records']:
  key=observation['board'];assert key in expected and key not in known
  original=expected[key];assert sha(ROOT/original['path'])==original['sha256']
  assert observation['actualObservation'].strip() and observation['allConstituentFramesDirectlyRead'] is True
  known[key]=dict(original,**{k:v for k,v in observation.items() if k!='board'},directlyRead=True,reviewedAt=stamp())
 record['records']=[known[k] for k in sorted(known)]
 record['unresolvedIssues']=[dict(board=r['board'],issue=x) for r in record['records'] for x in r.get('issues',[])]
 record['allNewCurrentBoardsDirectlyRead']=len(known)==len(expected) and not record['unresolvedIssues']
else:
 sourcePath=P/'part1-current-moving-review-request-v325.json';source=read(sourcePath)
 path=P/'part1-current-moving-direct-progress-v325.json'
 record=read(path) if path.exists() else dict(startedAt=stamp(),sourceSha256=source['sourceSha256'],requestSha256=sha(sourcePath),records=[],allFreshMovingPixelsReviewed=False,newGitImages=0,humanWholeListening='pending')
 assert record['sourceSha256']==source['sourceSha256'] and record['requestSha256']==sha(sourcePath)
 known={r['id']:r for r in record['records']}; expected={r['id']:r for r in source['rows'] if r['id']!='whole-current-captioned-final'}
 for observation in data['records']:
  key=observation['id'];assert key in expected and key not in known
  assert observation['actualObservation'].strip() and observation['fullSelectedIntervalActuallyPlayed'] is True and observation['playbackRate']==1
  assert observation['rangeSeconds']==expected[key]['ranges'][0]
  known[key]=dict(observation,reviewedAt=stamp())
 record['records']=[known[r['id']] for r in source['rows'] if r['id'] in known]
 record['unresolvedIssues']=[dict(id=r['id'],issue=x) for r in record['records'] for x in r.get('issues',[])]
 record['allFreshMovingPixelsReviewed']=len(known)==96 and not record['unresolvedIssues'] and all(r['normalSpeedPixelsApproved'] for r in known.values())
 for key in ['fourGameDifferencesAndCommonPrincipleDirectlyReviewed','originalIntroMembershipAndFixedCaptionStyleDirectlyReviewed']:
  if key in data:record[key]=data[key]
record['updatedAt']=stamp()
tmp=path.with_suffix('.writing.json');tmp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8');tmp.replace(path)
print(json.dumps(dict(mode=mode,directlyReviewed=len(record['records']),total=len(expected),unresolved=len(record['unresolvedIssues']))))
