from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
FONT=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
def wrap(text,width=1570):
 words=text.split();lines=[];cur=''
 for word in words:
  test=(cur+' '+word).strip()
  if FONT.getlength(test)>width and cur:lines.append(cur);cur=word
  else:cur=test
 if cur:lines.append(cur)
 return lines
def image(text):
 lines=wrap(text);assert len(lines)<=2,(len(lines),text)
 w=round(max(FONT.getlength(x) for x in lines))+44;h=62*len(lines)+22;x=960-w//2;y=970-h//2
 im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
 d.rectangle((x+14,y+14,x+w+14,y+h+14),fill='#073c32')
 d.rectangle((x,y,x+w,y+h),fill='white',outline='#161b18',width=3)
 for i,line in enumerate(lines):d.text((960,y+11+i*62+31),line,font=FONT,fill='#080b09',anchor='mm')
 return im
if __name__=='__main__':
 p=Path(__file__).resolve().parent
 image('접기는 삭제가 아닙니다. 지금 보이는 범위만 바뀝니다.\n제목과 그 아래 설명은 한 묶음으로 옮깁니다.').save(p/'preflight-caption.png')
