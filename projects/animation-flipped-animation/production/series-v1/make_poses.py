"""Mirror an asymmetric guard, switch the grip socket and inspect travel from two cameras."""
from pathlib import Path
import sys,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/series-v1'
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
def sample(key,i,t):
    p=rig.pose_copy();v=ease((t-9)/26)*(1-ease((t-64)/35))
    reverse=key=='tool' or bool(i and key=='mirror')
    side='l' if reverse else 'r';rest='r' if reverse else 'l'
    sign=-1 if reverse else 1
    pitch_torso(p,sign*(14+17*v),-8*v)
    arm(p,side,[sign*(12+19*v),25,-9+26*v]);arm(p,rest,[-sign*13,12,-22])
    if key in ('direction','observer'):
        pos,q=p['root'];p['root']=(pos+np.array([0,38*v,0]),q)
    return p
def letters():
    font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',150)
    swatch=Image.new('RGBA',(250,540));draw=ImageDraw.Draw(swatch)
    for i,letter in enumerate('MAR'):
        draw.text((125,76+160*i),letter,font=font,anchor='mm',fill='#e9e6d7')
    mirror=ImageOps.mirror(swatch)
    with (L/'letters-render.log').open('wb') as log:
        proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0','-c:v','libx264','-threads','3','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',str(L/'letters.mp4')],stdin=subprocess.PIPE,stderr=log)
        for t in range(120):
            im=Image.new('RGB',(1920,1080),'#111b18');d=ImageDraw.Draw(im)
            for x in range(0,1920,96):d.line((x,230,x,760),fill='#2c3a34',width=2)
            d.line((960,237,960,765),fill='#e4b870',width=4)
            im.paste(swatch,(355,226),swatch)
            width=max(2,round(250*abs(np.cos(np.pi*ease((t-12)/34)))))
            glyph=(swatch if t<29 else mirror).resize((width,540),Image.Resampling.LANCZOS)
            im.paste(glyph,(1440-width//2,226),glyph)
            proc.stdin.write(im.tobytes())
        proc.stdin.close();assert proc.wait()==0
if __name__=='__main__':
    keys=('mirror','tool','direction','observer');settings={k:{'sideYaws':[-72,72],'cameraWidth':505} for k in ('mirror','tool')}
    settings['tool']['handSockets']=['hand_r','hand_l']
    settings['direction']={'yaw':-58,'cameraWidth':505}
    settings['observer']={'yaw':-58,'cameraWidth':505,'cameraView':'top'}
    export('A13',P,{k:lambda i,t,k=k:sample(k,i,t) for k in keys},settings)
    letters()
