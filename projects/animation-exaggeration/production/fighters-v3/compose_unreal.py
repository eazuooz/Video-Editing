"""Native Unreal pixels plus speech-synchronized labels and pose-derived guides."""
from pathlib import Path
import math,json,sys,subprocess,hashlib
import numpy as np
import audio_pipeline as ap,video_pipeline as vp
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3'
def color(hex):return hex[4:6]+hex[2:4]+hex[:2]
def text(x,y,words,size=42,c='F0F0E9',an=5):return f'{{\\an{an}\\pos({x},{y})\\fs{size}\\b1\\bord0\\shad0\\1c&H{color(c)}&}}'+words
def shape(points,c,width=6):
 # Hollow strokes are filled quads, with round point markers added separately.
 out=[]
 for a,b in zip(points,points[1:]):
  a=np.array(a);b=np.array(b);v=b-a;length=np.linalg.norm(v)
  if length<.01:continue
  n=np.array([-v[1],v[0]])/length*width/2
  poly=[a+n,b+n,b-n,a-n];out.append('{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c&H'+color(c)+'&}'+vp.polygon([p.tolist() for p in poly]))
 return out
def ring(point,c,radius=12):
 x,y=point;p=[[x+radius*math.cos(t),y+radius*math.sin(t)] for t in np.linspace(0,2*math.pi,33)]
 return ['{\\an7\\pos(0,0)\\p1\\bord3\\shad0\\1a&HFF&\\3a&H00&\\3c&H'+color(c)+'&}'+vp.polygon(p)]
def projected(p,side):
 x,y,z=p;t=math.radians(-60);wx=math.cos(t)*x-math.sin(t)*y+(-125 if side=='left' else 125)
 return [960+wx*1920/550,540-(z-85)*1920/550]
def main():
 cid=sys.argv[1];data=ap.read(L/'unreal/poses'/f'{cid}.json');built=ap.read(L/'unreal'/f'{cid}-build.json');frames=data['frames'];duration=frames/60
 directory=L/'unreal/renders'/built.get('renderFolder',cid);assert len(list(directory.glob('*.png')))==frames
 raw=L/'unreal'/f'{cid}-raw.mp4';movie=L/'unreal'/f'{cid}.mp4';ass=L/'unreal'/f'{cid}.ass'
 script=vp.ass_header();ev=vp.event
 # Fixed black branding/caption bands; the selected series keeps its gray grid.
 for box in [[0,0,1920,135],[0,880,1920,1080]]:
  x0,y0,x1,y1=box;fill='{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c&H080908&}'+vp.polygon([[x0,y0],[x1,y0],[x1,y1],[x0,y1]])
  script+=ev(0,duration,fill,1)
 size=data['mode']=='size-amplitude'
 script+=ev(0,duration,text(65,48,'동작의 과장 · Exaggeration' if size else '회전과 이동 · 어깨의 자유도',46,'E8CF83',7),3)
 for cue in data['phases']:
  a,b,phase=cue['start'],cue['end'],cue['phase']
  if size:
   labels=('가까이 보기','같은 동작 · 작은 화면') if phase==0 else (('같은 크기 · 같은 동작','같은 크기 · 같은 동작') if phase==1 else ('기존 움직임','어깨·허리 움직임 확대'))
  else:
   labels=('어깨 위치 고정','어깨 이동 가능') if phase==3 else (('뼈대와 표면','뼈대와 표면') if phase==0 else (('어깨 기준점','Rotation · 회전') if phase==1 else ('기준 자세','Translation · 이동')))
  script+=ev(a,b,text(480,175,labels[0],40,'354C60'),3)+ev(a,b,text(1440,175,labels[1],40,'247B59'),3)
 if not size:
  for side in ['left','right']:
   rows=data['evidence'][side]
   for f in range(0,frames,2):
    a=f/60;b=min((f+2)/60,duration);row=rows[f];points=[projected(row[k],side) for k in ['shoulder','elbow','wrist']]
    c='315C86' if side=='left' else '267D57'
    for draw in shape(points,c,6):script+=ev(a,b,draw,2)
    for p in points:
     for draw in ring(p,c,10):script+=ev(a,b,draw,2)
    if row['phase']==3:
     target=projected(row['target'],side)
     for draw in ring(target,'B57612',18):script+=ev(a,b,draw,3)
  script+=ev(0,duration,text(960,850,'같은 손 목표 · 다른 어깨 위치' if any(c['phase']==3 for c in data['phases']) else 'Rig · 뼈대와 조절 장치',34,'313B35'),3)
 ass.write_text(script,encoding='utf-8')
 if not raw.exists():
  subprocess.run(['ffmpeg','-y','-v','error','-framerate','60','-i',str(directory/'%06d.png'),'-frames:v',str(frames),'-vf','format=yuv420p','-c:v','libx264','-threads','4','-preset','fast','-crf','16',str(raw)],check=True)
 args=['ffmpeg','-y','-v','error','-filter_complex_threads','2','-i',str(raw)]
 if size:
  closeEnd=next((c['end'] for c in data['phases'] if c['phase']==0),0)
  graph=f'[0:v]split=3[a][b][c];[a]crop=960:720:0:160[big];[b]crop=960:720:0:160,scale=624:468,pad=960:720:168:252:0xd1d2d1[small];[big][small]blend=all_expr=if(lt(T\\,{closeEnd})\\,A\\,B)[left];[c]crop=960:720:960:160,scale=624:468,pad=960:720:168:252:0xd1d2d1[right];[left][right]hstack,pad=1920:1080:0:160:black,ass='+vp.filter_path(ass)+'[v]'
  args+=['-filter_complex',graph,'-map','[v]']
 else:args+=['-vf','ass='+vp.filter_path(ass)]
 args+=['-an','-frames:v',str(frames),*vp.ENCODER,'-movflags','+faststart',str(movie)]
 subprocess.run(args,check=True);vp.assert_video(movie,frames)
 receipt={'status':'complete','episode':'A02','revision':'fighters-v3','frames':frames,'fps':60,'width':1920,'height':1080,'movie':ap.relative(movie),'movieSha256':ap.sha(movie),'sourceMesh':built['sourceMesh'],'sourceAnimation':built['sourceAnimation'],'level':built['level'],'sequence':built['sequence'],'build':ap.artifact(L/'unreal'/f'{cid}-build.json'),'poseData':ap.artifact(L/'unreal/poses'/f'{cid}.json'),'nativePixels':ap.artifact(raw),'labels':ap.artifact(ass),'humanReview':False,'sourceAssetsModified':False}
 ap.save(L/'unreal'/f'{cid}-capture.json',receipt);print(cid,'composed',frames)
if __name__=='__main__':main()
