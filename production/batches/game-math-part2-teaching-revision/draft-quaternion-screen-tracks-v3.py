"""Observed screen landmarks; KLT proposes motion, final moving review stays pending."""
from pathlib import Path
import cv2,json,numpy as np,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
R=B/'cross-game-review-20261011/quaternion-four-game-v3';O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/action-drafts'
cv2.setNumThreads(2)
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Points below were read from the enlarged rendered source frames (640x360).
# Red is tail/body to nose; blue is one visible upper wing across the aircraft.
trail=[
 (0,[[175,209],[413,189],[260,143],[471,111]]),
 (1.5,[[189,211],[425,195],[272,121],[368,113]]),
 (2.3,[[174,217],[443,184],[185,115],[427,145]]),
 (2.7,[[197,218],[448,205],[205,135],[438,162]]),
 (3.2,[[347,224],[324,165],[201,151],[433,149]]),
 (3.8,[[337,226],[320,172],[203,152],[435,139]]),
 (4.4,[[317,257],[314,160],[204,158],[431,143]]),
 (5,[[295,292],[337,176],[209,172],[426,140]]),
 (5.6,[[278,286],[327,168],[227,176],[409,112]]),
 (5.8,[[278,267],[343,146],[244,179],[370,99]]),
 (6,[[267,245],[331,126],[258,168],[365,80]]),
 (7,[[252,238],[363,129],[283,138],[276,76]]),
 (8,[[272,274],[342,130],[279,173],[301,60]]),
 (9,[[322,242],[330,174],[228,212],[369,106]]),
 (9.5,[[357,248],[333,171],[240,224],[383,102]]),
 (10,[[218,154],[419,197],[239,216],[385,96]]),
 (11,[[245,176],[391,171],[229,220],[379,90]]),
 (12,[[224,159],[414,197],[234,205],[384,88]]),
 (13,[[281,173],[394,165],[241,209],[370,80]]),
 (14,[[220,174],[412,188],[232,228],[393,91]]),
 (15,[[248,178],[391,179],[233,244],[370,91]]),
 (16,[[231,181],[403,182],[242,235],[351,82]]),
 (17,[[256,153],[387,197],[255,241],[374,80]]),
 (18,[[262,151],[366,184],[223,236],[377,74]]),
 (19,[[370,161],[283,190],[220,190],[372,81]]),
 (20,[[373,139],[273,178],[233,124],[409,153]]),
 (21,[[347,145],[304,169],[213,157],[410,102]]),
 (22,[[341,153],[327,168],[284,164],[440,89]]),
 (23,[[331,137],[311,207],[206,148],[417,118]]),
 (24,[[380,145],[273,212],[277,154],[361,259]]),
 (25,[[403,171],[267,178],[298,123],[343,165]]),
 (26,[[405,159],[285,181],[314,135],[386,189]]),
 (27,[[410,158],[277,182],[249,171],[330,112]]),
 (28,[[400,179],[309,157],[225,141],[405,130]]),
 (29,[[385,181],[316,155],[219,128],[402,126]]),
 (30,[[390,178],[317,151],[216,127],[410,134]]),
 (31,[[332,159],[328,193],[213,205],[379,105]]),
 (32,[[362,141],[329,188],[222,207],[379,79]]),
 (33,[[324,137],[315,193],[235,211],[377,84]]),
 (34,[[402,117],[283,174],[294,179],[324,81]]),
 (34.8,[[401,158],[273,167],[298,120],[339,88]]),
]
# Segment boundaries and discrete orientation changes reset the tracking.
# An upright long axis is explicitly not proof of identical full orientation.
gear=[
 (0,[[321,221],[336,119]]),(1.5,[[324,221],[337,119]]),
 (1.65,[[324,221],[337,119]]),
 (1.8,[[294,165],[381,194]]),(2,[[294,165],[381,194]]),
 (2.3,[[294,165],[381,194]]),(2.35,[[338,120],[347,223]]),(2.5,[[338,120],[347,223]]),
 (3,[[339,121],[347,223]]),
 (3.15,[[405,250],[413,145]]),
 (3.7,[[401,247],[414,148]]),(3.9,[[401,247],[414,148]]),
 (4.1,[[338,183],[459,176]]),(4.35,[[338,183],[459,176]]),
 (4.55,[[399,247],[418,151]]),(4.65,[[399,247],[418,151]]),
 (5.1,[[409,236],[422,127]]),(6,[[412,246],[428,132]]),
 (6.6,[[396,252],[416,142]]),(8,[[324,222],[335,135]]),
 (9.5,[[324,222],[335,135]])
]
# Two actual selected cannon directions. Hide during camera cut and during
# translation mode; never annotate the later translation arrows as rotation.
besiege=[
 (4.3,[[364,214],[254,241],[511,184],[432,205]]),
 (5.75,[[364,214],[254,241],[511,184],[432,205]]),
 (6,[[364,214],[254,241],[511,184],[432,205]]),
 (6.1,[[362,245],[255,216],[509,164],[440,232]]),
 (6.3,[[362,245],[255,217],[509,164],[440,232]]),
 (7.15,[[362,245],[255,217],[509,164],[440,232]])
]
jobs=[dict(stem='trail',keys=trail,hide=[[2.82,3.2],[9.5,10],[18.7,28],[30.8,31.4],[34,35]],redLabel='빨강: 기체 앞 방향',blueLabel='파랑: 날개 방향',note='화면 관찰선 · 월드 각도나 내부 구현의 실측값 아님'),
 dict(stem='gear-v3',keys=gear,hide=[[1.65,1.8],[2.3,2.35],[3,3.35],[3.9,4.1],[4.35,4.55],[5,5.3],[6.2,6.8]],redLabel='빨강: 부품의 두 끝을 잇는 방향',blueLabel=None,note='세워진 모습만으로 완전히 같은 자세라고 단정하지 않음'),
 dict(stem='besiege',keys=besiege,hide=[[0,4.3],[6,6.1],[7.15,10.9]],redLabel='빨강: 선택한 부품의 방향',blueLabel='파랑: 함께 선택한 다른 부품',note='선택 부품의 방향 비교 · 뒤의 이동 조작과 구분')]
write(R/'observed-screen-seeds.json',dict(referenceResolution=[640,360],jobs=jobs,sourceClaims='Observed projected directions only; no game-world angle or engine implementation assertion.',movingPixelApproval=False))
for job in jobs:
 path=O/(job['stem']+'-unannotated.mp4');cap=cv2.VideoCapture(str(path));gray=[]
 while True:
  ok,frame=cap.read()
  if not ok:break
  gray.append(cv2.cvtColor(cv2.resize(frame,(640,360)),cv2.COLOR_BGR2GRAY))
 cap.release();keys=[(round(t*60),np.array(points,dtype=np.float32)) for t,points in job['keys']]
 result=[None]*len(gray);reports=[]
 for (start,points),(end,target) in zip(keys,keys[1:]):
  if end-start>180:continue # Do not propagate through the camera orbit.
  end=min(end,len(gray)-1);current=points.reshape(-1,1,2);prop=[points.copy()];valid=[True]
  for n in range(start+1,end+1):
   moved,status,error=cv2.calcOpticalFlowPyrLK(gray[n-1],gray[n],current,None,winSize=(31,31),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,35,.02))
   back,back_status,_=cv2.calcOpticalFlowPyrLK(gray[n],gray[n-1],moved,None,winSize=(31,31),maxLevel=3)
   good=status.ravel().astype(bool)&back_status.ravel().astype(bool)&(np.linalg.norm(back-current,axis=2).ravel()<2)
   valid.append(bool(np.all(good)));current=moved;prop.append(moved.reshape(-1,2).copy())
  correction=target-prop[-1];drift=float(np.max(np.linalg.norm(correction,axis=1)))
  reports.append(dict(startFrame=start,endFrame=end,endpointCorrectionPixels=drift,unreliableFrames=sum(not x for x in valid)))
  for k,n in enumerate(range(start,end+1)):
   t=n/60
   fraction=k/max(1,end-start)
   manual_candidate=job['stem']=='trail' and end-start<=72 and drift>=35
   visible=((valid[k] and drift<35) or manual_candidate) and not any(a<=t<b for a,b in job['hide'])
   corrected=points+(target-points)*fraction if manual_candidate else prop[k]+correction*fraction
   result[n]=dict(frame=n,visible=visible,points=(corrected*3).round(2).tolist(),forwardBackwardFlowPassed=valid[k],manualInterpolationCandidate=manual_candidate)
 # Never silently extrapolate outside observed anchor ranges.
 data=dict(stem=job['stem'],video=path.relative_to(ROOT).as_posix(),videoSha256=hashlib.sha256(path.read_bytes()).hexdigest(),resolution=[1920,1080],fps=60,observedKeyframes=job['keys'],hide=job['hide'],semantics={k:job[k] for k in ['redLabel','blueLabel','note']},method='Per-landmark KLT with rejection and endpoint correction. Trail short-window manual interpolation is a separately flagged proposal requiring dense/moving review; no propagation across gaps longer than3s.',windows=reports,frames=result,movingPixelApproval=False)
 write(R/(job['stem']+'-screen-track.json'),data)
 print(job['stem'],len(gray),'frames',sum(bool(f and f['visible']) for f in result),'proposed visible; review pending',flush=True)
