"""Draw short, manually keyed editorial focus marks over the inspected source frames."""
import subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
def render(shot,keys,destination,retro=False):
    source_start=shot['sourcePoint'];seconds=shot['frames']/60
    matching=[p for p in keys if p['source']==shot['key'] and p['points'][-1][0]>source_start and p['points'][0][0]<source_start+seconds]
    if not matching:return None
    # Transparent video is authored at half resolution and composited exactly into the 1080p picture.
    font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',25)
    with destination.with_suffix('.log').open('wb') as log:
        proc=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-y','-f','rawvideo','-pix_fmt','rgba','-s','960x540','-r','30','-i','pipe:0','-an','-c:v','qtrle','-pix_fmt','argb',str(destination)],stdin=subprocess.PIPE,stderr=log)
        for i in range((shot['frames']+1)//2):
            time=source_start+i/30;im=Image.new('RGBA',(960,540));d=ImageDraw.Draw(im)
            for item in matching:
                pts=item['points'];xs=[p[0] for p in pts]
                if not xs[0]<=time<=xs[-1]:continue
                x,y,w,h=[np.interp(time,xs,[p[f] for p in pts]) for f in range(1,5)]
                if retro:x=160+(x-160)*5/6;y*=5/6;w*=5/6;h*=5/6
                x,y,w,h=[round(v*3) for v in (x,y,w,h)];col=item.get('color','#FFB95F')
                frac=min(1,(time-xs[0])/.17);width=4
                if item.get('shape')=='oval':d.arc((x,y,x+w,y+h),-90,-90+int(360*frac),fill=col,width=width)
                else:
                    n=round(min(w*.31,h*.45)*frac)
                    for px,sx in ((x,1),(x+w,-1)):
                        for py,sy in ((y,1),(y+h,-1)):
                            d.line([(px+n*sx,py),(px,py),(px,py+n*sy)],fill=col,width=width)
                if item.get('label') and frac>.85:
                    label=item['label'];tx=max(12,min(x,934-d.textlength(label,font=font)));ty=max(85,min(372,y+h+3))
                    d.rounded_rectangle((tx-4,ty,tx+int(d.textlength(label,font=font))+6,ty+28),radius=4,fill=(20,36,29,234))
                    d.text((tx,ty-1),label,font=font,fill='#F5F5E8')
            proc.stdin.write(im.tobytes())
        proc.stdin.close();assert proc.wait()==0
    return destination
