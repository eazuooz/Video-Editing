from pathlib import Path
from datetime import datetime,timezone
import json,os,time
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent
receipt=BASE/'youtube-pinned-comment-v1.json';r=json.loads(receipt.read_text('utf-8'))
assert r['posted'] and r['pinnedReopenedVerified'] and r['videoId']=='xtUVcAHtQzg'
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json'
for retry in range(12):
 raw=qp.read_text('utf-8-sig');q=json.loads(raw);i=next(x for x in q['items']if x['slug']=='picking-sides')
 i['postPublicationFollowup']=dict(videoId=r['videoId'],commentId=r['commentId'],posted=True,pinnedReopenedVerified=True,receipt=receipt.relative_to(ROOT).as_posix(),historicalReceiptsPreserved=True,otherPendingHumanRightsReviewsPreserved=True,gitDelivered=False)
 q['updatedAt']=datetime.now(timezone.utc).isoformat();temporary=qp.with_name(qp.name+f'.pinned-{os.getpid()}.writing')
 temporary.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
 if qp.read_text('utf-8-sig')==raw:
  os.replace(temporary,qp);break
 temporary.unlink();time.sleep(.15)
else:raise RuntimeError('Concurrent queue writer preserved; retry actual follow-up recording only')
print(json.dumps(dict(posted=True,pinnedReopenedVerified=True,onlyPickingFollowupFieldUpdated=True)))
