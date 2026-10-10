from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[4]; BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
prepared=ROOT/'projects/picking-sides/publishing/pinned-comment.ko.txt'
visible=(BASE/'comment-visible-text.txt').read_text('utf-8')
text=prepared.read_text('utf-8-sig').strip()
assert '@yamyamcoding님이 고정함' in visible and '1430b1ff-a61e-8040-a542-d672d5d25328' in visible
assert '직접 만들어본 코드와 막힌 지점을 바탕으로 공부 방향을 잡고 싶다면 얌얌코딩 프로그래밍 코칭·과외 안내를 확인해보세요.' in visible
dest=BASE/'youtube-pinned-comment-v1.json'; assert not dest.exists()
record=dict(schemaVersion=1,slug='picking-sides',videoId='xtUVcAHtQzg',commentId='UgynTM-MA24mW_yhUx14AaABAg',
 commentUrl='https://www.youtube.com/watch?v=xtUVcAHtQzg&lc=UgynTM-MA24mW_yhUx14AaABAg',
 observedAt=datetime.now(timezone.utc).isoformat(),publiclyAvailableDirectlyObserved=True,visibilityChangedByThisFollowup=False,
 scheduleSource='shared/publishing/schedule-20261009/result.json',preparedComment=rel(prepared),preparedCommentSha256=sha(prepared),exactSubmittedText=text,
 posted=True,postedOnce=True,pinned=True,pinnedReopenedVerified=True,pinBadge='@yamyamcoding님이 고정함',reloadedCommentIdMatched=True,
 evidence=[dict(path=rel(BASE/name),sha256=sha(BASE/name),localOnly=True)for name in ['pinned-comment-reopened.png','pinned-comment-reopened.ax.txt','comment-visible-text.txt']],
 preservesHistoricalPrivateReceipt=True,historicalReceipt='projects/picking-sides/publishing/youtube-upload-depth-v1.json',
 otherCommentsModified=False,otherVideosModified=False,newUploads=0,newMedia=0,researchControlChanges=0,
 humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,gitDelivery=False)
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(posted=True,pinnedReopenedVerified=True,commentId=record['commentId'],historicalPrivateReceiptPreserved=True)))
