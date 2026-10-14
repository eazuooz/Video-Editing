"""Move only the late aircraft15px down to separate its top wing from subtitle."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw
from orientation_detailed_projected_subjects_v1 import frame_07b
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-mixed-detailed-preparation-v3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
oldp=O/'current34-mixed-detailed-subject-replacement-plan-v2.json'
old=json.loads(oldp.read_text('utf-8-sig'));assert not LOCAL.exists();LOCAL.mkdir(parents=True)
samples=[];board=Image.new('RGB',(1920,1140),'#f5f5f5');d=ImageDraw.Draw(board)
for i,f in enumerate([1891,1960,2079]):
 fp=LOCAL/f'07b-f{f:04d}.png';im=frame_07b(f);im.save(fp);samples.append(dict(scene='07b',frame=f,path=rel(fp),sha256=sha(fp)))
 im.thumbnail((960,540));x=i%2*960;y=i//2*570;board.paste(im,(x,y));d.text((x+10,y+542),f'07b frame {f}',fill='black')
bp=LOCAL/'07b-board-01.png';board.save(bp)
out=O/'current34-mixed-detailed-subject-replacement-plan-v3.json';assert not out.exists()
old.update(recordedAt=datetime.now(timezone.utc).isoformat(),previousPlan=rel(oldp),previousPlanSha256=sha(oldp),editableModuleSha256=sha(B/'orientation_detailed_projected_subjects_v1.py'),additionalHeldStaticHistory='V2 late aircraft top wing was too close to the header subtitle. Center525 separates header and footer simultaneously. V2 remains historical.',preparedSamples=[x for x in old['preparedSamples'] if not (x['scene']=='07b' and x['frame']>=1891)]+samples,preparedBoards=[x for x in old['preparedBoards'] if '03b-' in x['path']]+[dict(path=rel(bp),sha256=sha(bp))],allStaticPreviewsDirectlyRead=False,clearanceRepair='03b continuous centerY600→480; up-arrow1.40. 07b late centerY525/wing endpoints±1.55. Direction, rotation, math and original narration reveal timing retained. Static clearance needs direct review, final captions pending.')
out.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(repairedSamples=3,boards=1,newPlan=rel(out))))
