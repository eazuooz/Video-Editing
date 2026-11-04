"""Record the final encoded images actually inspected, without inflating scope."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parents[1];Q=P/'production/local/render-v3/final-qa'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=read(Q/'report.json');assert len(report['samples'])==237
record=dict(id='final-v3-sampled-pixel-review',checkedAt=datetime.now(timezone.utc).isoformat(),status='sampled-pixel-pass-final-audio-repair-pending',captionedMasterSha256=report['files']['captioned']['sha256'],scope='All 79 scenes at opening 8%, middle 50%, closing 90%; 237 final captioned frames, 20 contact sheets with 375px-wide panels. Targeted original crops confirm no source clipping where scaled preview appeared truncated.',images=[dict(path=str((Q/f'contact-{i:02}.png').relative_to(P)),sha256=sha(Q/f'contact-{i:02}.png')) for i in range(20)],targetedOriginalCrops=dict(path=str((Q/'targeted-original-crops.png').relative_to(P)),sha256=sha(Q/'targeted-original-crops.png')),observations=['Fixed white captions remain below game content and explanation figures in the inspected frames.','Source labels, canonical names, worked formulas and real-engine versus illustrative outputs are distinguished.','Same-space material, light shape, shading-frequency, baked/mixed/probe and summary comparisons retain consistent spatial framing.','Original-crop checks resolve apparent missing titles/model and caption fragments in the tool contact-sheet display.'],remaining=['Continuous actual gameplay and annotation-target motion review','Every caption cue and chapter join in moving output','Corrected V4 audio technical/full ASR/local-level checks','Actual human listening and user final review'],humanListening=False,humanViewing=False,allCaptionCuesViewed=False,continuousPlaybackViewed=False,readyForUserReview=False)
(Q/'sampled-visual-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=P/'production/review-ledger.json';ledger=read(p);checks=ledger.get('checks',[])
if isinstance(checks,dict):checks[record['id']]=record
else:checks=[x for x in checks if x.get('id')!=record['id']]+[record]
ledger.update(checks=checks,updatedAt=record['checkedAt']);p.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('237 actually inspected final-frame samples recorded; continuous/audio/user review remains pending')
