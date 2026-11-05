"""Overlay wrist trails computed from each baked rig on the matching native frame."""
from pathlib import Path
import json, subprocess, sys, math, hashlib, shutil
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[4];L=H.parents[1]/'local/fighters-v4-kula-lili/unreal'
sys.path.insert(0,str(H.parents[1]/'fighters-v3'))
import video_pipeline as vp
V3=H.parents[1]/'fighters-v3'
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def to_bgr(rgb):return rgb[4:]+rgb[2:4]+rgb[:2]
def label(x,y,s,size,color='EEEEEA',align=5):
    return f'{{\\an{align}\\pos({x},{y})\\fs{size}\\b1\\bord0\\shad0\\1c&H{to_bgr(color)}&}}'+s
def proj(p,side):
    x,y,z=p;angle=math.radians(-60)
    return np.array([960+1920/500*(math.cos(angle)*x-math.sin(angle)*y+(-125 if side=='left' else 125)),540-1920/500*(z-85)])
def stroke(a,b,rgb,width):
    a=np.array(a);b=np.array(b);v=b-a;ll=np.linalg.norm(v)
    if ll<.15:return ''
    dx=np.array([-v[1],v[0]])*width/(2*ll)
    return '{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c&H'+to_bgr(rgb)+'&}'+vp.polygon([list(x) for x in [a+dx,b+dx,b-dx,a-dx]])
def ring(a,r,rgb):
    pts=[(a+np.array([math.cos(t),math.sin(t)])*r).tolist() for t in np.linspace(0,2*math.pi,24,endpoint=False)]
    return '{\\an7\\pos(0,0)\\p1\\bord3\\shad0\\1a&HFF&\\3c&H'+to_bgr(rgb)+'&}'+vp.polygon(pts)
def rect(x,y,w,h,color):
    return '{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c&H'+to_bgr(color)+'&}'+vp.polygon([[x,y],[x+w,y],[x+w,y+h],[x,y+h]])
def artifact(p):return {'path':p.relative_to(R).as_posix(),'sha256':digest(p)}
def main(cid):
    d=json.loads((L/'poses'/f'{cid}.json').read_text(encoding='utf-8'));built=json.loads((L/f'{cid}-build.json').read_text(encoding='utf-8'))
    frames=d['frames'];duration=frames/60;capture=L/'renders'/cid
    assert len(list(capture.glob('*.png')))==frames
    assert built['camera']['widthCm']==500
    script=[vp.ass_header()]
    def ev(start,end,draw,layer=1):
        if draw:script.append(vp.event(start,end,draw,layer))
    ev(0,duration,rect(0,0,1920,135,'080A09'))
    ev(0,duration,rect(0,883,1920,197,'080A09'))
    ev(0,duration,label(62,37,'동작의 과장',48,'E8CF83',7),3)
    ev(0,duration,label(1854,28,'손목 이동 거리  /  같은 재생 속도',33,'D7DAD4',9),3)
    ev(0,duration,label(1854,82,'+ 어깨 중심     ○ 손목     ━ 손목 궤적',29,'C4D1C7',9),3)
    ev(0,duration,label(480,168,'기준 동작  1.0×  ·  30 cm',41,'284969'),3)
    ev(0,duration,label(1440,168,'과장 동작  1.8×  ·  54 cm',41,'12573B'),3)
    for cue in d['phases']:
        phase=cue['phase']
        if d['mode']=='shoulder-control':
            note={0:'뼈대와 표면',1:'회전  ·  어깨의 중심은 고정',2:'이동  ·  왼쪽 어깨 고정   /   오른쪽 어깨 이동',3:'같은 손 목표   /   왼쪽 어깨 고정   ·   오른쪽 어깨 이동'}[phase]
        else:note='같은 크기의 캐릭터  ·  시작점에서 손목까지의 궤적'
        ev(cue['start'],cue['end'],label(960,846,note,33,'24322B'),3)
    # Clear editorial marks across discontinuous cue resets. MRQ samples
    # compressed poses and may interpolate one frame across that boundary.
    changes=[round(c['start']*60) for c in d['phases'][1:]]
    for side,rgb in [('left','2E5E97'),('right','146C4A')]:
        for f in range(frames):
            if any(abs(f-boundary)<=2 for boundary in changes):
                continue
            # libass time resolution is 0.01s. Round down both boundaries so
            # an exact 60Hz frame never displays the previous frame's pose.
            row=d['evidence'][side][f];t=(f*100//60)/100;end=((f+1)*100//60)/100
            start=proj(row['origin'],side);wrist=proj(row['wrist'],side);shoulder=proj(row['shoulder'],side);peak=proj(row['peak'],side)
            ev(t,end,stroke(start,wrist,rgb,6),2);ev(t,end,ring(start,7,rgb),2);ev(t,end,ring(wrist,13,rgb),2)
            ev(t,end,stroke(shoulder+[-12,0],shoulder+[12,0],rgb,4),2)
            ev(t,end,stroke(shoulder+[0,-12],shoulder+[0,12],rgb,4),2)
            if d['mode']=='shoulder-control' and row['phase']==3:ev(t,end,ring(peak,18,'80520B'),2)
    ass=L/f'{cid}.ass';ass.write_text(''.join(script),encoding='utf-8')
    raw=L/f'{cid}-raw.mp4';movie=L/f'{cid}.mp4'
    if not raw.exists():
        subprocess.run(['ffmpeg','-y','-v','error','-framerate','60','-i',str(capture/'%06d.png'),'-frames:v',str(frames),'-c:v','libx264','-threads','4','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',str(raw)],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-filter_threads','2','-i',str(raw),'-vf','ass='+vp.filter_path(ass),'-frames:v',str(frames),*vp.ENCODER,'-an','-movflags','+faststart',str(movie)],check=True)
    vp.assert_video(movie,frames)
    rec={'status':'complete','episode':'A02','revision':'fighters-v4-kula-lili','frames':frames,'fps':60,'width':1920,'height':1080,'movie':movie.relative_to(R).as_posix(),'movieSha256':digest(movie),'sourceMesh':built['sourceMesh'],'sourceAnimation':built['sourceAnimation'],'level':built['level'],'sequence':built['sequence'],'build':artifact(L/f'{cid}-build.json'),'poseData':artifact(L/'poses'/f'{cid}.json'),'nativePixels':artifact(raw),'labels':artifact(ass),'measurement':d['trials'],'humanReview':False,'sourceAssetsModified':False}
    (L/f'{cid}-capture.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');print('Completed',cid,frames,flush=True)
if __name__=='__main__':main(sys.argv[1])
