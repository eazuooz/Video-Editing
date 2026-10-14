"""Preserve V1 static history and prepare only eight affected clearance samples."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw
from orientation_detailed_projected_subjects_v1 import frame_03b,frame_07b
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-mixed-detailed-preparation-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
oldp=O/'current34-mixed-detailed-subject-replacement-plan-v1.json'
old=json.loads(oldp.read_text('utf-8-sig'));assert not LOCAL.exists();LOCAL.mkdir(parents=True)
samples=[];boards=[]
for sid,fn,frames in [('03b',frame_03b,[1270,1336,1402,1480,1600]),('07b',frame_07b,[1891,1960,2079])]:
 for f in frames:
  fp=LOCAL/f'{sid}-f{f:04d}.png';fn(f).save(fp);samples.append(dict(scene=sid,frame=f,path=rel(fp),sha256=sha(fp)))
 for n in range(0,len(frames),3):
  board=Image.new('RGB',(1920,1140),'#f5f5f5');d=ImageDraw.Draw(board)
  for i,f in enumerate(frames[n:n+3]):
   im=Image.open(LOCAL/f'{sid}-f{f:04d}.png');im.thumbnail((960,540));x=i%2*960;y=i//2*570
   board.paste(im,(x,y));d.text((x+10,y+542),f'{sid} frame {f}',fill='black')
  bp=LOCAL/f'{sid}-board-{n//3+1:02d}.png';board.save(bp);boards.append(dict(path=rel(bp),sha256=sha(bp)))
out=O/'current34-mixed-detailed-subject-replacement-plan-v2.json';assert not out.exists()
old.update(recordedAt=datetime.now(timezone.utc).isoformat(),previousPlan=rel(oldp),previousPlanSha256=sha(oldp),editableModuleSha256=sha(B/'orientation_detailed_projected_subjects_v1.py'),heldStaticHistory='V1 detailed subjects read; late03b teal arrow and late07b blue wing line crossed the explanatory footer/reserved margin. Geometry retained; camera framing and arrow graphic lengths corrected. V1 preview files preserved. V1 preparedBoards recorded only the final scene due to a preparation-list bug; all seven existing V1 boards were directly read.',preparedSamples=[x for x in old['preparedSamples'] if not ((x['scene']=='03b' and x['frame']>=1270) or (x['scene']=='07b' and x['frame']>=1891))]+samples,preparedBoards=boards,allStaticPreviewsDirectlyRead=False,clearanceRepair='03b smoothly reframes centerY600→480 during the same flip; up-arrow endpoint1.40. 07b late centerY510 and wing-line endpoints±1.55 align the detailed span. Direction, rotation, numerical math and reveal timing retained; graphic lengths are not measurements.')
out.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(repairedSamples=len(samples),boards=len(boards),newPlan=rel(out))))
