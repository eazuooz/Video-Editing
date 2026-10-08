"""Record only explicitly supplied, actually read boards; never auto-approve."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--from-board',required=True,type=int);ap.add_argument('--to-board',required=True,type=int)
ap.add_argument('--note',required=True);ap.add_argument('--defect');a=ap.parse_args()
execution=read(BASE/'selected-pixels-execution-v1.json');assert execution['exitCode']==0
path=BASE/'selected-pixels-direct-review-v1.json';now=datetime.now(timezone.utc).isoformat()
record=read(path) if path.exists() else dict(schemaVersion=1,slug='player-customization',createdAt=now,
 execution='projects/player-customization/production/selected-pixels-execution-v1.json',allocationSha256=execution['allocationSha256'],
 captionSha256=execution['captionSha256'],encodedBodySha256=execution['sourceSha256'],totalBoards=execution['boardCount'],
 totalSamples=execution['sampleCount'],koCueCount=415,totalCuts=136,groups=[],boards=[],unresolvedDefects=[],
 allBoardsDirectlyRead=False,sourceAllocationApproved=False,finalTimingApproved=False,bodyRatioApproved=False,
 finalMixedAsrApproved=False,allFinalPixels=False,qaApproved=False,collected=False,uploaded=False,newGitImages=0,
 humanWholeListening='pending',humanPronunciation='pending')
assert record['encodedBodySha256']==execution['sourceSha256']
assert 1<=a.from_board<=a.to_board<=execution['boardCount']
already={b['index'] for b in record['boards']};rows=[]
for n in range(a.from_board,a.to_board+1):
 assert n not in already,'Preserve direct review history; do not repeat completed boards.'
 board=execution['boards'][n-1];assert board['index']==n and sha(ROOT/board['path'])==board['sha256']
 for sn in board['sampleIndices']:
  sample=execution['samples'][sn-1];assert sha(ROOT/sample['path'])==sample['sha256']
 rows.append({**board,'directlyRead':True,'reviewedAt':now})
record['boards']+=rows;record['boards'].sort(key=lambda b:b['index'])
record['groups'].append(dict(fromBoard=a.from_board,toBoard=a.to_board,reviewedAt=now,findings=a.note,defect=a.defect))
if a.defect:record['unresolvedDefects'].append(dict(fromBoard=a.from_board,toBoard=a.to_board,observation=a.defect))
record.update(observedAt=now,readBoardCount=len(record['boards']),readSampleCount=sum(len(b['sampleIndices']) for b in record['boards']),
 allBoardsDirectlyRead=len(record['boards'])==record['totalBoards'])
t=path.with_name(path.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
for n in range(60):
 try:os.replace(t,path);break
 except OSError:
  if n==59:raise
  time.sleep(.15)
print(json.dumps(dict(readBoards=record['readBoardCount'],totalBoards=record['totalBoards'],sourceAllocationApproved=False,
 unresolvedDefects=len(record['unresolvedDefects']))))
