"""Annotate the existing Unity captures using their own orthographic projection and sampled-frame clock."""
import math,subprocess
from bisect import bisect_right
import numpy as np
from PIL import Image,ImageDraw
from common import WORK,BASE,read,write,sha
from guides import stroke,dot,unit,NCLR,LCLR,RCLR,VCLR,PCLR,BG
from layout import font
from symbol_pages import text
NATIVE={35,36,77}
ORIGIN_Y=174
def render(s):
    job=read(WORK.parent/'render-v5/native-jobs'/f'{s:03}.json')
    cue=read(WORK.parent/'render-v5/native-jobs'/f'{s:03}-cue.json')
    sample=job['sampleFrames'];count=job['frames'];out=WORK/'native-guides';out.mkdir(exist_ok=True)
    dest=out/f'{s:03}.mov';marker=dest.with_suffix('.json');stamp=[sha(BASE/'unity_guides.py'),job['expectedFingerprint'],count]
    if marker.exists() and read(marker)['stamp']==stamp and dest.exists():return
    eye=np.array(cue.get('cameraPosition',[6,4,-8]),dtype=float)
    forward=unit(np.array([0,1.35,0])-eye)
    right=unit(np.cross([0,1,0],forward));up=np.cross(forward,right)
    origin=eye+right*3.5
    def projection(w):
        q=np.asarray(w)-origin
        return np.array([960+540/4.6*np.dot(q,right),540-ORIGIN_Y-540/4.6*np.dot(q,up)])
    def paint(frame):
        im=Image.new('RGBA',(968,736));d=ImageDraw.Draw(im)
        sec=frame/60;n=np.array([0.,1.,0.]);pos=np.array([-.7,1.42+1.36+({35:.06,36:.065,77:.08}[s]),0]);p=projection(pos)
        def lab(x,word,col,offset):
            at=x+np.array(offset);at[0]=np.clip(at[0],8,830);at[1]=np.clip(at[1],22,710)
            text(d,at,word,col,30)
        def direction(v,name,col,length,offset):
            q=projection(pos+v*length);delta=q-p
            if np.linalg.norm(delta)<6:
                x,y=p;d.ellipse((x-9,y-9,x+9,y+9),outline=col,width=3);dot(d,p,3,col)
            else:
                dv=unit(delta);t=np.array([-dv[1],dv[0]])
                stroke(d,p,q-dv*10,col,5);d.polygon([tuple(q),tuple(q-dv*17+t*7),tuple(q-dv*17-t*7)],fill=col)
            lab(q,name,col,offset)
        if s==35:
            later=sec>=cue['stepTimes'][1]
            a=math.radians(10+70*min(1,sec/cue['stepTimes'][1]))
            l=np.array([-math.sin(a),math.cos(a),0])
            source=projection(pos+l*1.9)
            direction(n,'N',NCLR,1.2,(9,-12))
            if not later:
                direction(2*np.dot(l,n)*n-l,'R',RCLR,1.8,(9,-9))
                lab(source,'입사 −L',LCLR,(-33,-22))
            else:direction(l,'광원 쪽',RCLR,1.9,(-42,-23))
        elif s==36:
            grain=math.pi*.5*min(1,sec/cue['duration']);t=np.array([math.cos(grain),0,math.sin(grain)])
            direction(t,'T · 결 방향',LCLR,1.55,(9,-10))
        else:
            phase=0 if sec<cue['stepTimes'][1] else 1;v=-forward;r=2*np.dot(v,n)*n-v
            direction(n,'N',NCLR,1.4,(8,-9))
            if phase:direction(r,'R',RCLR,1.55,(9,-12))
            # In this Unity camera the orthographic view vector points out of the screen.
            direction(v,'V · 화면 앞',VCLR,1.2,(-137,39))
        dot(d,p,6,PCLR);lab(p,'P',PCLR,(11,18));return im.tobytes()
    cmd=['ffmpeg','-nostdin','-y','-v','error','-f','rawvideo','-r','60','-pix_fmt','rgba','-s','968x736','-i','pipe:0','-frames:v',str(count),'-an','-threads','1','-c:v','qtrle','-pix_fmt','argb',str(dest)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        cache=None;old=-1
        for i in range(count):
            k=sample[max(0,bisect_right(sample,i)-1)]
            if k!=old:cache=paint(k);old=k
            proc.stdin.write(cache)
    finally:proc.stdin.close()
    assert proc.wait()==0
    write(marker,dict(stamp=stamp,frames=count,source='Unity compiled scene positions, orthographic projection and actual capture sample times',point=projection([-.7,2.84,0]).tolist()))
if __name__=='__main__':
    for s in NATIVE:render(s);print('Native vectors',s,flush=True)
