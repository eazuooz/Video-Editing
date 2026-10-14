"""Editable screen-space annotations on reviewed, action-led official footage.
Track visible image features, never infer world coordinates or renderer internals.
"""
import importlib.util,math,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import ConvexHull
p=Path(__file__).with_name('review-media-common-v15.py');s=importlib.util.spec_from_file_location('review_media',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
plan_path=m.PROD/'current-input-plan-v19.json';plan=m.read(plan_path)
out=m.ROOT/'production/research/game-lighting-history/local/native-annotations-v19b'
state_path=m.PROD/'native-annotation-preparation-execution-v19b.json'
assert not out.exists() and not state_path.exists(),'Preserve existing annotation preparation'
resources=m.resources();out.mkdir(parents=True)
state=dict(startedAt=m.stamp(),status='running',worker=m.worker(),resourceObservation=resources,active=None,cpuThreads=2,gpuJobs=0,allMovingPixelsReviewed=False,allFinalPixelsReviewed=False)
m.save(state_path,state)
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Malgun Gothic,30,&H00FFFFFF,&H00FFFFFF,&H00101010,&H00101010,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def at(f):
 cs=round(f*100/60);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
def event(a,b,text,layer=0):return f'Dialogue: {layer},{at(a)},{at(b)},Label,,0,0,0,,{text}\n'
def vector(points,color,width=4):
 path='m '+str(round(points[0][0]))+' '+str(round(points[0][1]))+' l '+' '.join(f'{round(x)} {round(y)}' for x,y in points[1:])
 return r'{\an7\pos(0,0)\p1\shad0\1a&HFF&\bord'+str(width)+r'\3c&H'+color+'&}'+path
def ring(x,y,r,color):return vector([(x+r*math.cos(t),y+r*math.sin(t)) for t in np.linspace(0,2*math.pi,33)],color,4)
def label(x,y,text,color='FFFFFF'):
 return r'{\an7\pos('+str(round(x))+','+str(round(y))+r')\1c&H'+color+'&}'+text
records=[]
try:
 c=next(x for x in plan['inputs'] if x['id']=='03-ray-shadow-02-repair-e5')
 proof=m.read(m.ROOT/c['verification']);assert proof['wholeDecode']['exitCode']==0 and m.sha(m.ROOT/c['output'])==proof['outputSha256']
 cmd=[str(m.FF),'-v','error','-threads','2','-i',str(m.ROOT/c['output']),'-frames:v',str(c['frames']),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
 log=out/'ray-shadow-feature-read.log'
 with log.open('wb') as lf:
  decoder=subprocess.Popen(cmd,cwd=m.ROOT,stdout=subprocess.PIPE,stderr=lf,creationflags=subprocess.CREATE_NO_WINDOW)
  state['active']=dict(pid=decoder.pid,createTime=m.psutil.Process(decoder.pid).create_time(),commandLine=cmd,log=m.rel(log),startedAt=m.stamp());m.save(state_path,state)
  tracks=[];ass=head;prev=np.array([218,77],float)
  for f in range(c['frames']):
   raw=decoder.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3,'Unexpected native decode end'
   hsv=np.asarray(Image.frombytes('RGB',(1920,1080),raw).resize((480,270),Image.Resampling.BILINEAR).convert('HSV'))
   blue=(hsv[:,:,0]>130)&(hsv[:,:,0]<180)&(hsv[:,:,1]>90)&(hsv[:,:,2]>55)
   blue[:,:125]=False;blue[222:,:]=False
   ids,count=ndimage.label(ndimage.binary_closing(blue,iterations=2));sizes=np.bincount(ids.ravel());sizes[0]=0;region=ids==sizes.argmax()
   assert region.sum()>1500,'Cube not visibly trackable'
   boundary=region&~ndimage.binary_erosion(region);yy,xx=np.where(boundary);points=np.stack([xx,yy],axis=1);hull=points[ConvexHull(points).vertices]*4;hull=np.vstack([hull,hull[0]])
   yellow=(hsv[:,:,0]>18)&(hsv[:,:,0]<49)&(hsv[:,:,1]>40)&(hsv[:,:,2]>145)
   yy0,xx0=np.indices(yellow.shape);yellow&=(xx0>130)&(xx0<250)&(yy0>45)&(yy0<221)
   ids,n=ndimage.label(ndimage.binary_closing(yellow,iterations=1));options=[]
   for i in range(1,n+1):
    py,px=np.where(ids==i)
    if 100<len(px)<1800:
     center=np.array([px.mean(),py.mean()]);options.append((float(np.linalg.norm(center-prev)),center,max(px.max()-px.min(),py.max()-py.min())/2))
   assert options,'Visible bulb feature unavailable'
   _,center,radius=min(options,key=lambda x:x[0])
   if np.linalg.norm(center-prev)>=45:
    diagnostic=out/('bulb-camera-jump-'+str(f)+'.png');Image.frombytes('RGB',(1920,1080),raw).save(diagnostic)
    m.save(out/('bulb-camera-jump-'+str(f)+'.json'),dict(frame=f,previous=prev.tolist(),current=center.tolist(),options=[dict(distance=x[0],center=x[1].tolist(),radius=x[2]) for x in options],cubeHull=hull.tolist(),diagnostic=m.rel(diagnostic),requiresDirectReview=True))
   prev=center;bx,by=center*4
   tracks.append(dict(localFrame=f,globalFrame=c['fromFrame']+f,bulbCenter=[round(bx,2),round(by,2)],bulbRadius=round(radius*4,2),visibleCubeHull=hull.tolist(),screenSpaceOnly=True))
   # Current guide speaks about the light/object and then their shadow. Source continues moving.
   if 50<=f<321:
    ass+=event(f,f+1,vector(hull.tolist(),'C8C850',3))
    ass+=event(f,f+1,ring(bx,by,min(80,max(42,radius*4+10)),'5265FF'))
    ass+=event(f,f+1,label(max(500,bx-230),max(125,by-85),'광원 위치','80D4FF'),2)
    ass+=event(f,f+1,label(min(1500,hull[:,0].min()+28),max(145,hull[:,1].min()+25),'가리는 상자','C8C850'),2)
   if f==50:ass+=event(50,321,label(34,775,'화면 투영 위치 비교 · 게임 월드 거리 측정 아님'),2)
  code=decoder.wait();assert code==0;state['lastCommand']={**state['active'], 'exitCode':code,'completedAt':m.stamp()};state['active']=None
 ass_path=out/(c['id']+'.annotations.ass');ass_path.write_text(ass,'utf-8')
 track_path=out/(c['id']+'.tracking.json');m.save(track_path,dict(method='Visible blue connected-region hull and yellow bulb feature, every decoded frame',source=dict(path=c['output'],sha256=proof['outputSha256']),samples=tracks,cameraTrackingReviewed=False,worldGeometryMeasured=False))
 records.append(dict(id=c['id'],source=c['output'],sourceSha256=proof['outputSha256'],fromFrame=c['fromFrame'],toFrame=c['toFrame'],frames=c['frames'],annotations=m.rel(ass_path),annotationsSha256=m.sha(ass_path),tracking=m.rel(track_path),trackingSha256=m.sha(track_path),narratedCueIds=[76,77],semanticRoles=dict(red='visible light location',teal='visible occluding cube silhouette'),classification='action-led-actual',output=m.rel(out/(c['id']+'.annotated.mp4'))))
 c=next(x for x in plan['inputs'] if x['id']=='original-31-repair-01');proof=m.read(m.ROOT/c['verification']);assert m.sha(m.ROOT/c['output'])==proof['outputSha256']
 ass=head+event(80,510,vector([(1104,266),(1505,266)],'5265FF',3))+event(180,510,vector([(1104,558),(1505,558)],'C8C850',3))
 ass+=event(80,510,label(1110,630,'복원 모드 / 입력 해상도 설정','FFFFFF'),2)
 ass+=event(180,510,label(1110,675,'원본 설정 표기 · 레이 수 / FPS 측정 아님','FFFFFF'),2)
 ass_path=out/(c['id']+'.annotations.ass');ass_path.write_text(ass,'utf-8')
 records.append(dict(id=c['id'],source=c['output'],sourceSha256=proof['outputSha256'],fromFrame=c['fromFrame'],toFrame=c['toFrame'],frames=c['frames'],annotations=m.rel(ass_path),annotationsSha256=m.sha(ass_path),narratedCueIds=[115,116,117],semanticRoles=dict(red='upscaling mode row',teal='internal screen percentage row'),tracking='Stationary editor panel coordinates; only enabled during visible DLSS panel',classification='action-led-actual',output=m.rel(out/(c['id']+'.annotated.mp4'))))
 plan_out=m.PROD/'native-annotation-plan-v19b.json'
 m.save(plan_out,dict(preparedAt=m.stamp(),inputPlan=dict(path=m.rel(plan_path),sha256=m.sha(plan_path)),cuts=records,style='red observed input / teal observed surface or resolution',pcmUnchanged=True,fixedCaptionsUnchanged=True,chaptersUnchanged=True,mathLimits='Projected observed positions/settings only; no unobserved world measurements, BVH or light-sampling internals.',fullAnimatedPlaybackReviewed=False,allFinalPixelsReviewed=False,qaApproved=False,collected=False,uploaded=False,newGitImages=0))
 state.update(status='complete',exitCode=0,completedAt=m.stamp(),active=None,preparedPlan=m.rel(plan_out));m.save(state_path,state)
 print(m.json.dumps(dict(trackedFrames=len(tracks),preparedCuts=len(records),mediaEncoded=0,movingPixelsApproved=False)),flush=True)
except BaseException as e:
 state.update(status='failed',exitCode=1,failedAt=m.stamp(),error=str(e));m.save(state_path,state);raise
