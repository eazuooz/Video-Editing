"""Mobile-sized simultaneous fixed/player camera panels using the approved style."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
previous=module('paired167_cached_style',H/'shorts-layout-v6.py');previous.previous.TITLES['shorts-mario64-lakitu-camera']=['3D 게임의 판도를 바꾼','마리오64']
NativeStreamReader=previous.NativeStreamReader
font=previous.previous.layout.font
class Composer(previous.Composer):
 def pair(self,left,right,label,leftLabel,rightLabel,condition='',leftState='',rightState='',credit=''):
  im=self.base(label);d=ImageDraw.Draw(im)
  for x,pixels,heading,color,state in [(0,left,leftLabel,'#e5b97a',leftState),(504,right,rightLabel,'#73c7c2',rightState)]:
   f=font(31,True);assert f.getlength(heading)<=450;d.text((x+240,460),heading,font=f,fill=color,anchor='mm')
   scale=min(480/pixels.width,480/pixels.height);w=round(pixels.width*scale);h=round(pixels.height*scale);im.paste(pixels.resize((w,h),Image.Resampling.LANCZOS),(x+(480-w)//2,510+(480-h)//2))
   d.rectangle((x+1,509,x+478,991),outline=color,width=3)
   if state:
    f=font(32,True);assert f.getlength(state)<=450;d.text((x+240,1042),state,font=f,fill=color,anchor='mm')
  if condition:
   f=font(32);assert f.getlength(condition)<=940;d.text((492,1120),condition,font=f,fill='white',anchor='mm')
  if credit:
   f=font(28);assert f.getlength(credit)<=940;d.text((492,1408),credit,font=f,fill='white',anchor='mm')
  return im
