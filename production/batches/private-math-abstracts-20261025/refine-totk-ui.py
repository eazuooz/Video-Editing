"""Protect the actual ability UI while pointing at the manipulated object."""
from render import *
import qa
for id in ['M03-original','M04','M05','M07']:
 pp=B/'plans'/f'{id}.json';p=read(pp);W=Path(p['work'])
 if (W/'ui-clearance-polish.json').exists():continue
 previous=read(W/'qa.json');save(W/'qa-before-ui-clearance.json',previous)
 if id=='M03-original':p['segments'][0]['guides'][0].update(xy=[.65,.59],radius=80)
 p['status']='sources-reviewed';p['uiClearance']='TOTK leader starts below ability HUD; sail arc remains above Attach prompt.';save(pp,p)
 receipt=W/'render-receipt.json';save(W/'render-receipt-before-ui-clearance.json',read(receipt));assert receipt.parent.resolve().is_relative_to(Path('C:/Users/1/.codex/video-render-cache/private-math-abstracts-20261025/work').resolve());receipt.unlink()
 run(id);qa.run(id,previous);save(W/'ui-clearance-polish.json',dict(id=id,status='visual-review-pending'))
