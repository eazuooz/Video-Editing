"""Generate current, captioned full-size and mobile QA evidence (local only)."""
from PIL import Image,ImageDraw,ImageFont
import common as c
Q=c.O/'qa';Q.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)

def still(sid,t,name):
 s=c.SCENES[sid];src=c.O/'clips'/f'{sid}.mp4';dest=Q/f'{name}.jpg'
 if not src.exists():return None
 if not dest.exists():
  c.ff(['-ss',t,'-i',src,'-vf',f'setpts=PTS+{s["start"]+t:.9f}/TB,ass=captions.ko.ass,setpts=PTS-STARTPTS','-frames:v',1,dest],f'qa-{name}.log',c.O)
 im=Image.open(dest);im.resize((375,211),Image.Resampling.LANCZOS).save(Q/f'{name}-375.jpg')
 return dest

def board(paths,name,columns=3,width=640):
 rows=(len(paths)+columns-1)//columns;out=Image.new('RGB',(columns*width,rows*(width*9//16+35)),(38,38,38));d=ImageDraw.Draw(out)
 for i,p in enumerate(paths):
  x=i%columns*width;y=i//columns*(width*9//16+35);d.text((x+8,y+4),p.stem,font=font,fill='white')
  out.paste(Image.open(p).resize((width,width*9//16),Image.Resampling.LANCZOS),(x,y+35))
 out.save(Q/f'{name}.jpg')

def main():
 paths=[]
 for sid,s in c.SCENES.items():
  if s.get('cuts'):continue
  for i,t in enumerate(s['lineStarts']):
   result=still(sid,min(t+1.7,s['seconds']-.1),f'{sid}-cue-{i+1:02}')
   if result:paths.append(result)
 for j in range(0,len(paths),9):board(paths[j:j+9],f'board-{j//9+1:02}')
 c.save(Q/'manifest.json',{'frameFiles':[c.rel(p) for p in paths],'currentCaptionsBurned':True,
   'everyOriginalExplanationCue':True,'mobileVersionWidth':375})
 print('QA frames',len(paths),flush=True)

if __name__=='__main__':main()
