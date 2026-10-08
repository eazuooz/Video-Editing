from pathlib import Path
import json,hashlib
R=Path('D:/Github/Video-Editing');slug='game-math-mesh-uv';W=R/'shared/output'/slug;Q=W/'qa';P=R/'projects'/slug/'production'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(W/'before-menu-boundary-repair/prior-direct-pixel-review.json');qa=read(P/'qa.json');beats=read(Q/'final-beats/generated-samples.json');ob=read(Q/'observation-samples.json')
assert qa['fullDecodePassed'] and qa['videos']['videoBurnedCaptions']['sha256']==beats['videoSha256']==ob['videoSha256']
assert beats['videoSha256']!=old['videoSha256']
images=sorted(Q.glob('caption-strips-*.jpg'))+sorted(Q.glob('composition-sheet-*.jpg'))+[R/x['path'] for x in beats['records']]+[R/x['path'] for x in ob['sheets']]
assert len(images)==len(old['images'])==47
same=[];changed=[]
for p in images:
 relative=p.relative_to(R).as_posix();previous=next(x for x in old['images'] if x['path']==relative)
 (same if sha(p)==previous['sha256'] else changed).append(relative)
value=dict(oldReview='shared/output/game-math-mesh-uv/before-menu-boundary-repair/prior-direct-pixel-review.json',currentVideoSha256=beats['videoSha256'],identicalPixelSheets=same,requiresFreshDirectView=changed,status='comparison-only-direct-view-pending')
(Q/'menu-repair-image-comparison.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(identical=len(same),changed=changed),ensure_ascii=False))
