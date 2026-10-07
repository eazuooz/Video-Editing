"""Only call after explicitly reading every indexed board for this exact encoded video."""
from pathlib import Path
import json,sys,hashlib,datetime,re

def has_rejection_marker(observation):
 # Preserve actual or ambiguous findings; ignore only explicit absence statements.
 without_absence=re.sub(r'\bno REJECT finding (?:was )?observed\b|새 REJECT 없음', '', observation, flags=re.IGNORECASE)
 return re.search(r'\bREJECT\b', without_absence, flags=re.IGNORECASE) is not None
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];count=int(sys.argv[2]);observations=sys.argv[3:]
folder=ROOT/'projects'/slug/'production/visual-depth-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=read(folder/'encoded-pixels-local/index.json');plan=read(folder/'encoded-pixel-plan.json');qa=read(folder/'pair-technical-qa.json')
progress=read(folder/'encoded-pixel-direct-progress.json')
if progress.get('videoSha256')!=index['videoSha256'] or not progress.get('allIndexedBoardsDirectlyRead') or progress.get('allFinalPixelsReviewed'):
 raise RuntimeError('Current exact-video complete direct-read progress required; unresolved pixel failures must remain unapproved')
if any(has_rejection_marker(o) for r in progress['ranges'] for o in r['observations']):
 resolution=read(ROOT/progress['findingResolution']) if progress.get('findingResolution') else {}
 if resolution.get('videoSha256')!=index['videoSha256'] or not resolution.get('allRecordedRejectionsResolved'):
  raise RuntimeError('Recorded final pixel rejection needs exact-video direct reinspection resolution')
 for f in resolution.get('directlyReadOriginalFrames',[]):
  if sha(ROOT/f['file'])!=f['sha256']:raise RuntimeError('Resolution frame changed')
if count!=len(index['boards']) or not observations:raise RuntimeError('Exact directly read board count and observations required')
current=next(o for o in qa['outputs'] if o['variant']=='captioned')
if current['sha256']!=index['videoSha256'] or sha(ROOT/current['path'])!=current['sha256']:raise RuntimeError('Encoded video identity changed')
if qa['status']!='passed-awaiting-every-final-pixel' or any(o['fullDecodeExitCode']!=0 for o in qa['outputs']):raise RuntimeError('Technical QA not passed')
for board in index['boards']:
 if sha(ROOT/board['path'])!=board['sha256']:raise RuntimeError('Directly read board changed')
 for f in board['frames']:
  if sha(ROOT/f['file'])!=f['sha256']:raise RuntimeError('Directly read indexed frame changed')
result=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),slug=slug,videoSha256=index['videoSha256'],srtSha256=index['srtSha256'],boardsRead=count,framesRead=index['uniqueFrames'],cuesRead=index['cueCount'],gameCutsRead=plan['cutCount'],boardHashes=[b['sha256'] for b in index['boards']],allFinalPixelsReviewed=True,captionPixelsApproved=True,gameUiPixelsApproved=True,depthMotionApproved=True,memberOuttroPixelsApproved=True,observations=observations,humanFullListening='pending',truncatedMemberHandles='pending',privateUploadCompleted=False)
target=folder/'encoded-pixel-direct-review.json'
if target.exists():raise RuntimeError('Preserve prior direct review')
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(dict(slug=slug,boards=count,frames=index['uniqueFrames'],cues=index['cueCount'],finalPixelsApproved=True,uploaded=False)))
