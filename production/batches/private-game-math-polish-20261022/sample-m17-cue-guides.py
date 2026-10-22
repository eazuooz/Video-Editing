"""Dense current candidate pixels for manual anchors; no inferred tracking."""
from PIL import Image, ImageDraw
from polish_common import *
e=Episode('M17'); e.authorized()
review=read(e.H/'camera-cue-review-v2.json'); src=R/review['rawClip']
assert sha(src)==review['rawClipSha256']
out=e.O/'camera-cue-guide-source'; out.mkdir(exist_ok=True)
times=[12+i*.25 for i in range(11)]+[26+i*.25 for i in range(7)]+[81.75+i*.25 for i in range(15)]
records=[]
for t in times:
 p=out/f'{t:.2f}.png'
 e.ff(['-ss',t,'-i',src,'-frames:v','1','-vf','scale=480:270','-threads','1',p],'camera-cue-guide-source.log')
 records.append(dict(localTime=t,path=rel(p),sha256=sha(p)))
for start in range(0,len(records),9):
 sheet=Image.new('RGB',(1440,900),'#171717'); d=ImageDraw.Draw(sheet)
 for i,r in enumerate(records[start:start+9]):
  x=i%3*480;y=i//3*300;sheet.paste(Image.open(R/r['path']),(x,y+30));d.text((x+5,y+5),str(r['localTime'])+'s',fill='white')
 sheet.save(out/f'sheet-{start//9+1:02}.jpg',quality=94)
save(e.H/'camera-cue-guide-source.json',dict(status='await-manual-source-observation',raw=review['rawClip'],rawSha256=review['rawClipSha256'],samples=records,coordinates=[480,270]))
print(len(records),'manual-anchor source states generated')
