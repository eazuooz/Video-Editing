"""One bounded fix after final-frame review; retain previous decode evidence."""
from render import *
import qa
FIX={'M03-original':{0:([.61,.68],95)},'M05':{0:([.5,.21],95)},'M06':{1:([.60,.46],70)},'M09':{1:([.50,.46],80)},'M11':{1:([.50,.46],80)},'M13':{2:([.36,.56],85)}}
for id in sys.argv[1:]:
 pp=B/'plans'/f'{id}.json';p=read(pp);W=Path(p['work'])
 if (W/'guide-polish.json').exists():continue
 oldqa=read(W/'qa.json');save(W/'qa-initial.json',oldqa)
 oldreceipt=read(W/'render-receipt.json');save(W/'render-receipt-initial.json',oldreceipt)
 for i,(xy,r) in FIX.get(id,{}).items():p['segments'][i]['guides'][0].update(xy=xy,radius=r)
 if id=='M10':p['segments'][0]['guides'][0]['label']='둥근 물체'
 p['status']='sources-reviewed';p['guideCorrection']='Keep leader strokes open; refine anchors from final full-resolution frames.';save(pp,p)
 # Remove only our own resumability receipt, retaining its complete backup.
 receipt=W/'render-receipt.json';assert receipt.parent.resolve().is_relative_to(Path('C:/Users/1/.codex/video-render-cache/private-math-abstracts-20261025/work').resolve());receipt.unlink()
 run(id);qa.run(id,oldqa);save(W/'guide-polish.json',dict(id=id,change='Open leader strokes and inspected target anchors',status='visual-review-pending'))
