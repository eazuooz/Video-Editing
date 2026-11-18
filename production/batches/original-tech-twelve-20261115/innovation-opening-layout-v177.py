"""The established Shorts layout with a concrete innovation thesis beside real footage."""
from pathlib import Path
import importlib.util
import av
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=module('innovation177_retained_layout',H/'shorts-layout-v6.py');core=old.previous.layout
class Composer(old.Composer):
 def __init__(self,row):
  super().__init__(row['slug']);self.row=row;self._opening_base=None;self._opening_caps={}
 def captioned(self,im,text):
  if not text:return im
  if text not in self._opening_caps:
   parts=[];line=''
   for word in text.split():
    assert self.caption.getlength(word)<=800
    trial=(line+' '+word).strip()
    if self.caption.getlength(trial)>800:parts.append(line);line=word
    else:line=trial
   if line:parts.append(line)
   assert 1<=len(parts)<=3,'Clause needs a further meaning split: '+text
   sample=Image.new('RGB',(1080,1920),'black');d=ImageDraw.Draw(sample);width=max(self.caption.getlength(x)for x in parts)+44;height=len(parts)*62+22;x=492-width/2;y=1600-height/2
   d.rectangle((round(x+14),round(y+14),round(x+width+14),round(y+height+14)),fill='#073c32');d.rectangle((round(x),round(y),round(x+width),round(y+height)),fill='white',outline='#161b18',width=3)
   for i,line in enumerate(parts):d.text((492,y+42+i*62),line,font=self.caption,fill='#080b09',anchor='mm')
   self._opening_caps[text]=sample.crop((0,1470,1080,1740))
  im.paste(self._opening_caps[text],(0,1470));return im
 def opening(self,pixels,caption=''):
  if self._opening_base is None:
   im=self.base('왜 혁신적이었을까?');d=ImageDraw.Draw(im)
   if self.row['order']==2:
    d.rectangle((0,0,1080,320),fill='black')
    for t,y,color in zip(['3D 게임의 판도를 바꾼','마리오64'],[145,240],[core.TOKENS['ink'],core.TOKENS['title']]):d.text((492,y),t,font=self.title,anchor='mm',fill=color)
   label=self.row['sourceLabel'];f=core.font(29,True);assert f.getlength(label)<=950;d.text((492,450),label,font=f,fill='#c3d8ce',anchor='mm')
   d.text((492,1210),'핵심 변화',font=core.font(32,True),fill=core.TOKENS['relation'],anchor='mm');tag=self.row['innovationTag'];f=core.font(42,True);assert f.getlength(tag)<=940
   d.text((492,1280),tag,font=f,fill=core.TOKENS['title'],anchor='mm');self._opening_base=im
  im=self._opening_base.copy();height=round(984*pixels.height/pixels.width);assert height<=984;im.paste(pixels.resize((984,height),Image.Resampling.LANCZOS),(0,396+(984-height)//2))
  if caption:self.captioned(im,caption)
  return im
class Reader:
 def __init__(self,path):
  self.c=av.open(str(path));self.s=self.c.streams.video[0];self.s.thread_count=2;assert self.s.width>=1920 and self.s.height>=1080;self.decoder=None;self.current=None;self.next=None;self.last=None
 def frame(self,seconds):
  if self.decoder is None or self.last is not None and(seconds<self.last or seconds-self.last>.25):
   self.c.seek(int(seconds/self.s.time_base),stream=self.s,backward=True);self.decoder=self.c.decode(self.s);self.current=None;self.next=None
  while self.next is None or self.next.time<=seconds:
   if self.next is not None:self.current=self.next
   self.next=next(self.decoder)
  if self.current is None:self.current=self.next
  assert self.current.time<=seconds+1/float(self.s.average_rate)+.0001;self.last=seconds;return self.current.to_image(),self.current.time
 def close(self):self.c.close()
