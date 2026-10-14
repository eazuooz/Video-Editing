"""Measure actual Windows font advances before timing; no final-pixel approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
source=R/'current17-caption-editorial-groups-v1.json';out=R/'current17-caption-phrase-measurement-v1.json';assert not out.exists()
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48);rows=[]
for cue in json.loads(source.read_text('utf-8-sig'))['groups']:
 limit=900 if cue['scene']=='08b' and cue['paragraph']==4 else 1570
 text=cue['ko'];measure=lambda v:float(font.getlength(v));lines=[text]
 if measure(text)>min(1050,limit):
  words=text.split();options=[]
  for i in range(1,len(words)):
   candidate=[' '.join(words[:i]),' '.join(words[i:])];widths=list(map(measure,candidate))
   if max(widths)<=limit:options.append((abs(widths[0]-widths[1]),candidate,widths))
  assert options,('Editorial split needed',cue['id'],text,limit)
  _,lines,widths=min(options,key=lambda v:v[0])
 else:widths=list(map(measure,lines))
 width=math.ceil(max(widths))+44;height=len(lines)*62+22;x=round(960-width/2);y=round(970-height/2)
 assert len(lines)<=2 and width<=1614 and x>=2 and x+width+14<1920 and y+height+14<1080
 if limit==900:assert x>475
 rows.append(dict(id=cue['id'],ko=text,lines=lines,actualGlyphAdvancePixels=widths,boxWidth=width,boxHeight=height,x=x,y=y,centerX=960,centerY=970,finalPixelsReviewed=False))
assert len(rows)==41
out.write_text(json.dumps(dict(schemaVersion=1,measuredAt=datetime.now(timezone.utc).isoformat(),font='C:/Windows/Fonts/malgun.ttf',fontSize=48,sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),cueCount=41,allPhrasesFitMaximumTwoLines=True,rows=rows,timingApproved=False,finalPixelsApproved=False),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(measuredPhrases=41,maxWidth=max(v['boxWidth'] for v in rows),allFitTwoLines=True,timingApproved=False,finalPixelsApproved=False)))
