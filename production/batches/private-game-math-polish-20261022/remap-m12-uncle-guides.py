"""Map already observed glyph pixels to the same source frames in M12.

Only editorial screen regions are reused; world positions/weights are unknown.
Current M12 composites still require direct inspection.
"""
import copy, math
from PIL import Image, ImageDraw, ImageFont
from polish_common import *

src=Episode('M11');e=Episode('M12');e.authorized()
clip=e.O/'clips/14.mp4';e.verify(clip,3449)
assert read(e.H/'uncle-source-cut-review.json')['status']=='passed-source-cut-inspection'
out=e.O/'uncle-guide-source';out.mkdir(exist_ok=True)
records=[];paths=[]
for name,shift in [('glyph-and-endpoint',-30),('glyph-observation',18)]:
 p=src.H/'cue-tracks'/('08-'+name+'.json');d=read(p)
 assert d['sourceSha256']==sha(src.O/'clips/08.mp4')
 new=copy.deepcopy(d)
 for k in new['keyframes']:k['t']=round(k['t']+shift,5)
 new.update(sourceFile=rel(clip),sourceSha256=sha(clip),sourceEvidence=rel(e.H/'uncle-source-cut-review.json'),sourceEvidenceSha256=sha(e.H/'uncle-source-cut-review.json'),
   reuse={'originalTrack':rel(p),'originalTrackSha256':sha(p),'timeOffsetSeconds':shift,'sameSourceId':'5u3sUKuncSU','reason':'Same source414–415.25 and367.25–368.75 frames appear at M12 local8–9.25 and31.25–32.75.'},movingPixelApproval=False)
 dst=e.H/'cue-tracks'/('14-'+name+'.json');save(dst,new);paths.append(rel(dst))
 for k in new['keyframes']:
  t=k['t'];img=out/f'14-{t:.3f}.png'
  e.ff(['-ss',t,'-i',clip,'-vf','scale=640:360','-frames:v','1','-threads','1',img],'m12-uncle-guide-source.log')
  records.append({'localSeconds':t,'image':rel(img),'sha256':sha(img)})
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
for i in range(0,len(records),4):
 sheet=Image.new('RGB',(1280,780),'#222222')
 for j,r in enumerate(records[i:i+4]):
  x=(j%2)*640;y=(j//2)*390
  sheet.paste(Image.open(R/r['image']),(x,y+30));ImageDraw.Draw(sheet).text((x+5,y+3),str(r['localSeconds']),font=font,fill='white')
 sheet.save(out/f'sheet-{i//4+1:02d}.jpg',quality=94)
save(e.H/'uncle-guide-source.json',{'sourceSha256':sha(clip),'samples':records,'sheets':math.ceil(len(records)/4),'status':'await-direct-current-source-inspection'})
p=e.H/'cue-guide-additions.json';d=read(p)
d['scenes']['14']={'landmarkSources':paths,'useReviewedLocalClip':True,'hideMathNote':True,
 'redLabel':'빨강: 표식 · 메시 아님','blueLabel':'파랑: 보이는 연결점',
 'mathNote':'화면 표식 ≠ 삼차원 가중치','mathNotePosition':[390,155],
 'revealAtLine':0,'redAtLine':0,'blueAtLine':0,'redKeyword':'표식','blueKeyword':'표식','mathNoteAtLine':0}
d['status']='additional-source-guide-await-composited-review';save(p,d)
print('M12 glyph guides mapped;13 current source frames await inspection',flush=True)
