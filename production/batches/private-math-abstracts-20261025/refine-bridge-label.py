"""Name the marked boat as the passing object, not the bridge surface."""
from render import *
import qa
id='M11';pp=B/'plans'/f'{id}.json';p=read(pp);W=Path(p['work'])
if not (W/'boat-label-polish.json').exists():
 previous=read(W/'qa.json');save(W/'qa-before-boat-label.json',previous)
 p['segments'][0]['guides'][0]['label']='통과할 대상'
 p['status']='sources-reviewed';p['boatLabelCorrection']='Mark names the passing boat during the candidate-bounds recap; later deck mark identifies the surface.';save(pp,p)
 receipt=W/'render-receipt.json';save(W/'render-receipt-before-boat-label.json',read(receipt));assert receipt.parent.resolve().is_relative_to(Path('C:/Users/1/.codex/video-render-cache/private-math-abstracts-20261025/work').resolve());receipt.unlink()
 run(id);qa.run(id,previous);save(W/'boat-label-polish.json',dict(id=id,status='visual-review-pending'))
