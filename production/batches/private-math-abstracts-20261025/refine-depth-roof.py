"""Align the depth example's mark with the pitched roof, not the wall below."""
from render import *
import qa
id='M18';pp=B/'plans'/f'{id}.json';p=read(pp);W=Path(p['work'])
if not (W/'roof-target-polish.json').exists():
 previous=read(W/'qa.json');save(W/'qa-before-roof-target.json',previous)
 p['segments'][1]['guides'][0].update(xy=[.59,.23],radius=70)
 p['status']='sources-reviewed';p['roofTargetCorrection']='Final frame shows the pitched central roof at normalized .59,.23; mark moved above the wall.';save(pp,p)
 receipt=W/'render-receipt.json';save(W/'render-receipt-before-roof-target.json',read(receipt));assert receipt.parent.resolve().is_relative_to(Path('C:/Users/1/.codex/video-render-cache/private-math-abstracts-20261025/work').resolve());receipt.unlink()
 run(id);qa.run(id,previous);save(W/'roof-target-polish.json',dict(id=id,status='visual-review-pending'))
