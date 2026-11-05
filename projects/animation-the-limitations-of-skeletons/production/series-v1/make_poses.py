"""Compare forward controls, inverse targets, elbow hints and two/four-link chains."""
from pathlib import Path
import sys,subprocess,math
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/series-v1'
sys.path.insert(0,str(R/'production/batches/animation-18-20261031/native'))
from pose_tools import *
def pose(key,i,t):
    p=rig.pose_copy();v=ease((t-9)/31)*(1-ease((t-69)/32))
    a=rig.WORLD['upperarm_r'][0];el=rig.WORLD['lowerarm_r'][0];hand=rig.WORLD['hand_r'][0]
    if key=='fkik':
        if not i:
            local_rotation(p,'upperarm_r','xz',[46*v,19*v]);local_rotation(p,'lowerarm_r','y',-27*v)
        else:rig.ik(p,'r',a+np.array([4+15*v,22,(-24+41*v)]))
    else:
        target=a+np.array([-4.,38.,-15.]);direction=(target-a)/np.linalg.norm(target-a)
        up=np.array([0.,0.,1.]);up-=up.dot(direction)*direction;up/=np.linalg.norm(up)
        across=np.cross(direction,up);phi=np.pi*(.2+(v*.82 if i else 0))
        n=up*np.cos(phi)+across*np.sin(phi)
        len1=np.linalg.norm(el-a);len2=np.linalg.norm(hand-el);d=np.linalg.norm(target-a)
        s=(len1**2-len2**2+d*d)/(2*d);mid=a+s*direction+np.sqrt(len1**2-s*s)*n
        rig.aim(p,'upperarm_r','lowerarm_r',mid-a)
        rig.aim(p,'lowerarm_r','hand_r',target-rig.fk(p)['lowerarm_r'][0])
    return p
def chains():
    with (L/'curve-render.log').open('wb') as log:
        pipe=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','60','-i','pipe:0','-c:v','libx264','-threads','3','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',str(L/'curve.mp4')],stdin=subprocess.PIPE,stderr=log)
        for t in range(120):
            weight=ease((t-9)/32)*(1-ease((t-67)/32))
            im=Image.new('RGB',(1920,1080),'#101b18');pen=ImageDraw.Draw(im)
            for x in range(0,1920,80):pen.line((x,231,x,770),fill='#29382e',width=2)
            for y in range(280,770,80):pen.line((0,y,1920,y),fill='#29382e',width=2)
            for side,joints in enumerate((2,4)):
                points=[]
                for k in range(joints+1):
                    u=k/joints;x=140+side*960+660*u;y=586-233*weight*np.sin(np.pi*u)
                    points.append((x,y))
                pen.line(points,fill='#d8a978' if not side else '#78c8ad',width=39,joint='curve')
                for x,y in points:pen.ellipse((x-13,y-13,x+13,y+13),fill='#26362e',outline='#e9eddf',width=4)
                x,y=points[-1];pen.ellipse((x-26,y-26,x+26,y+26),outline='#f3d477',width=5)
            pipe.stdin.write(im.tobytes())
        pipe.stdin.close();assert pipe.wait()==0
if __name__=='__main__':
    keys=('fkik','hint')
    export('A17',P,{k:lambda i,t,k=k:pose(k,i,t) for k in keys},{k:dict(yaw=-16,cameraWidth=370,cameraHeight=105,actorSpacing=79) for k in keys})
    chains()
