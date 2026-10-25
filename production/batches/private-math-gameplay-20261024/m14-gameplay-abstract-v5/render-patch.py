"""Selected M14: inspected native square-cut / rotator recording, no padding."""
from pathlib import Path
import importlib.util, json, math
R=Path(__file__).resolve().parents[4]; B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',B.parent/'render-patches.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=R/'projects/game-math-polygon-partition-v2'; H=P/'production/gameplay-abstract-v5'; O=P/'production/local/gameplay-abstract-v5'
def auth():
 a=m.read(R/'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['m14-gameplay-abstract-v5']
 assert a['status']=='active' and a['renderAuthorized'] and not a['uploadAuthorized']
auth();O.mkdir(parents=True,exist_ok=True)
src=R/'shared/output/private-math-gameplay-20261024/m14-v5/shapez-cc-ep01-native.mp4'
info=m.read(R/'shared/output/private-math-gameplay-20261024/motion-v4/source-review/shapez-candidates/dep-ep01.info.json')
assert 'Creative Commons' in info['license']
v=next(v for v in m.probe(src)['streams'] if v['codec_type']=='video');assert v['width']==1920 and v['height']==1080
timeline=m.read(P/'production/concept-fit-v2/timeline.json');slot=next(s for s in timeline['scenes'] if s['id']=='QG06')
modelrow=m.read(P/'production/concept-fit-v2/render-progress.json')['scenes']['QG06'];model=R/modelrow['path'];assert m.sha(model)==modelrow['sha256']
rows=[]
def event(a,b,s,layer=2): rows.append(f'Dialogue: {layer},{m.stamp(a)},{m.stamp(b)},Default,,0,0,0,,{s}')
def label(a,b,x,y,s,size=42,c='EFF5F5'):
 event(a,b,'{\\pos('+f'{x},{y}'+')\\fs'+str(size)+'\\1c&H'+c+'&}'+s)
label(0,13,36,22,'사각형을 자르고, 남은 조각을 회전',52,'73D7FF')
label(0,13,36,87,'Shapez 2 · 실제 플레이 확대',32,'BCC0A7')
label(0,13,1320,145,'원리 비교',48,'73D7FF');label(0,13,1320,205,'기존 설명 모형',34,'BCC0A7')
label(0,4.4,36,862,'① 사각형 입력 → 절단 → 작은 조각',39,'A2D380')
label(4.4,7.5,36,862,'② 남은 조각의 방향을 90° 회전',39,'73D7FF')
label(7.5,13,36,862,'③ 다시 잘라 목표 모양으로 가공',39,'A2D380')
# The rightmost existing column flows bottom-to-top. Offline source tracking
# was checked against the native frames; no detector scores enter the picture.
track=m.read(H/'annotation-track.json')['rows']
def shifts(t):
 if t<=track[0]['t']:return track[0]['dx'],track[0]['dy']
 for a,b in zip(track,track[1:]):
  if a['t']<=t<=b['t']:
   f=(t-a['t'])/(b['t']-a['t']);return a['dx']+(b['dx']-a['dx'])*f,a['dy']+(b['dy']-a['dy'])*f
 return track[-1]['dx'],track[-1]['dy']
def outline(a,b,cy,arc=False):
 for n in range(round(a*30),round(b*30)):
  t=n/30;dx,dy=shifts(t);yy=130+(cy+dy-300)*4/3;xx=(542+dx)*4/3;r=48
  ang=[-math.pi/2+i*math.pi/2/24 for i in range(25)] if arc else [i*2*math.pi/64 for i in range(65)]
  pts=[(xx+r*math.cos(vv),yy+r*math.sin(vv)) for vv in ang]
  if arc:
   e=pts[-1];vv=ang[-1]+math.pi/2
   pts.extend([(e[0]-20*math.cos(vv-.5),e[1]-20*math.sin(vv-.5)),e,(e[0]-20*math.cos(vv+.5),e[1]-20*math.sin(vv+.5))])
  draw=' '.join(f'm {a[0]:.1f} {a[1]:.1f} l {b[0]:.1f} {b[1]:.1f}' for a,b in zip(pts,pts[1:]))
  color='73D7FF' if arc else 'A2D380'
  event(t,min(b,t+1/30),'{\\an7\\pos(0,0)\\p1\\bord5\\shad0\\1a&HFF&\\3c&H'+color+'&}'+draw,1)
outline(.6,4.4,575);outline(4.4,7.5,482,True);outline(7.5,13,391)
event(.6,13,'{\\an7\\pos(0,0)\\p1\\bord0\\1c&H120D09&}m 830 295 l 1190 295 1190 375 830 375',1)
label(.6,4.4,850,310,'절단',48,'A2D380');label(4.4,7.5,850,310,'90° 회전',48,'73D7FF');label(7.5,13,850,310,'남는 조각',48,'A2D380')
(O/'patch-guides.ass').write_text(m.HEADER+'\n'.join(rows)+'\n',encoding='utf8')
dst=O/'square-cut-rotation.mp4'
graph='[0:v]crop=960:540:0:300,scale=1280:720:flags=lanczos,setsar=1,fps=60,setpts=N/(60*TB)[game];[1:v]crop=850:650:80:150,scale=620:474,setsar=1[model];color=c=0x090D12:s=1920x1080:r=60:d=13[bg];[bg][game]overlay=0:130[g];[g][model]overlay=1300:240,ass=patch-guides.ass[v]'
m.ff(['-ss',1115.6,'-i',src,'-i',model,'-filter_complex_threads',2,'-filter_complex',graph,'-map','[v]','-frames:v',780,'-an',*m.ENC,dst],O/'patch-render.log',O)
evidence=dict(source=m.rel(src),url=info['webpage_url'],title=info['title'],creator=info['uploader'],license=info['license'],sourceSha256=m.sha(src),dimensions=[v['width'],v['height']],nativeFPS=v['r_frame_rate'],inSeconds=1115.6,outSeconds=1128.6,crop=[0,300,960,540],classification='independent-gameplay',creditRequired=True,creditDestination='local review page and future upload description; no upload authorized',audio='Video-only selected. Creator commentary mixed with gameplay is excluded, no substitute music or fabricated game sound.',observed='Full four-cell square feeds the bottom half destroyer; vertical two-cell remainder turns horizontal in the middle 90-degree rotator; upper half destroyer outputs a single square quarter. Continuous 13 seconds, no still, retiming or repetition.',researchEvidence=['shared/output/private-math-gameplay-20261024/m14-v5/pipeline-sequence.png','shared/output/private-math-gameplay-20261024/m14-v5/cc-1117.png','shared/output/private-math-gameplay-20261024/m14-v5/cc-1125.png'],visualReview='source native-size frames and quarter-second action sequence inspected; final pending',gameInternalTriangulationEvidence=False)
m.save(H/'source-evidence.json',evidence)
m.save(H/'patch.json',dict(scene='QG06',oldStart=slot['start'],duration=13,frames=780,path=m.rel(dst),sha256=m.sha(dst),explanationSource=modelrow,sourceEvidence=m.rel(H/'source-evidence.json'),bodySpeech=slot.get('cues'),newSpeech=False))
print(json.dumps(dict(patch=m.rel(dst),oldStart=slot['start'],nativeSeconds=13),ensure_ascii=False))
