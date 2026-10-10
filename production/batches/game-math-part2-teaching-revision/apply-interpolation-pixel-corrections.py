"""Apply only defects directly observed in final moving pixels; no approval."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'interpolation-annotation-tracks.json';x=read(p)
x['scenes']['IG10']['blueHideSourceIntervals']=[[105,107.5]]
x['scenes']['IG10']['directPixelCorrection']='Final local18.35/source107.35 detector line follows shin while board is held; suppress ambiguous tail after completed landing.'
x['scenes']['14']['mathNotePosition']=[407,70]
x['scenes']['14']['directPixelCorrection']='Local8 final frame showed reminder near wing/body; raise panel above observed body path. Local56 and69.85 manual red anchors drift off skier; suppress these rapid intervals.'
write(p,x)
p=B/'interpolation-tracks/original-14-flight.json';x=read(p)
for interval in [[55,57],[68.2,70]]:
 if interval not in x['hideIntervals']:x['hideIntervals'].append(interval)
x['directFinalPixelCorrection']='Hide rapid55–57 ski turn and68.2–70 launch where sparse interpolation is not reliable. Do not substitute guessed screen anchors.'
write(p,x)
for slug in ['game-math-interpolation-paths-v2','game-math-rotation-conversions-v2']:
 p=ROOT/'projects'/slug/'publishing/thumbnail-v2.json';x=read(p);x['mobilePixelReview']=True;x['mobileReviewPixels']=[480,270];x['reviewReason']='Exact Korean brand/headline and episode pill readable; one subject/concept, integrated illustrated cat, no video inset.';write(p,x)
print('Applied observed IG10/14 corrections; final render/native review remains required.')
