"""Refresh current-file QA sheets/URLs without assigning review approval."""
from pathlib import Path
import hashlib,json,re,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3'
O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3'
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
records=[]
for sid in ['QF00','QF11','QF21','QF31','QC00','QC11','QC21','QC31']:
 p=O/f'explanation-preview/videos/quaternion_four_game_v3/540p30/{sid}.mp4'
 c=cv2.VideoCapture(str(p));sheet=Image.new('RGB',(1280,784),'white');d=ImageDraw.Draw(sheet)
 for k,t in enumerate([1,8,12,16]):
  c.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,img=c.read();assert ok,(sid,t)
  x=k%2*640;y=k//2*392
  sheet.paste(Image.fromarray(cv2.cvtColor(cv2.resize(img,(640,360)),cv2.COLOR_BGR2RGB)),(x,y+32))
  d.text((x+4,y+4),f'{sid} CURRENT silent preview {t}s',font=font,fill='black')
 c.release();sheet.save(O/f'{sid}-explanation-preview.jpg',quality=95)
 records.append(dict(scene=sid,path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),silent=True,artificialPreviewSeconds=18,finalTimingAndNarrationApproval=False))
page=O/'combined-draft-review.html';html=page.read_text(encoding='utf8')
def version(m):
 relative=m.group(1).split('?')[0];p=O/relative
 return 'data-src="'+relative+'?sha='+hashlib.sha256(p.read_bytes()).hexdigest()[:16]+'"'
html=re.sub(r'data-src="([^"]+)"',version,html);page.write_text(html,encoding='utf8')
source=ROOT/'manim/projects/game-math-part2-teaching-revision/quaternion_four_game_v3.py'
(R/'silent-draft-current-files.json').write_text(json.dumps(dict(records=records,sceneSourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),movingPixelReview='pending',finalNarrationTimingAndCaptionReview='pending'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Refreshed eight CURRENT preview sheets and content-hashed browser URLs; no QA approval assigned.')
