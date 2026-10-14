"""Preserve all six v1 mocks, increase room for the destination feet below."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(R/'alyx-annotation-observation-plan-v2.json')
for x in plan['samples']:assert sha(ROOT/x['staticPath'])==x['staticSha256'] and sha(ROOT/x['path'])==x['sha256']
proof=dict(schemaVersion=1,reviewedAt=datetime.now(timezone.utc).isoformat(),planSha256=sha(R/'alyx-annotation-observation-plan-v2.json'),
    allSixStaticMocksDirectlyRead=True,samples=plan['samples'],
    findings=['All three post-arrival cyan leaders end on visible wall/window trim next to the door; no destination marker is carried across the jump.',
        'Before-arrival red small circle targets the gap between feet; make it a wider bracket around both yellow feet.',
        'Native3039 lower boot pixels overlap the caption top edge under shiftY-120. Raise source by180pixels before moving-pilot adoption.'],
    verdict='held-narrow-layout-repair',movingAnnotationApproved=False,narrationTimed=False,finalCueApproval=False,gitImagesAdded=0)
p=R/'alyx-annotation-static-direct-review-v1.json';assert not p.exists();p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
src=B/'prepare-motion-alyx-annotation-static-v1.py';dst=B/'prepare-motion-alyx-annotation-static-v2.py';assert not dst.exists()
code=src.read_text('utf-8-sig').replace("motion/alyx-annotation-static-v1'","motion/alyx-annotation-static-v2'")
code=code.replace('crop((0,120,1920,1080))','crop((0,180,1920,1080))').replace('crop((0,960,1920,1080))','crop((0,900,1920,1080))').replace('(0,960))','(0,900))').replace('*1.5-120','*1.5-180').replace('subtract120','subtract180')
code=code.replace('point[0]-42,point[1]-30,point[0]+42,point[1]+30','point[0]-115,point[1]-55,point[0]+115,point[1]+55')
code=code.replace("R/'alyx-annotation-observation-plan-v2.json'","R/'alyx-annotation-observation-plan-v3.json'")
compile(code,str(dst),'exec');dst.write_text(code,'utf-8')
print('All6v1 observed/held; v2mock prepared only. Native source/old mock preserved.')
