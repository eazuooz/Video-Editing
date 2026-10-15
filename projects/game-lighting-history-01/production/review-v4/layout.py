"""Editable, hand-reviewed screen-space contours. Coordinates authored at480x270."""
from probe import *

def build():
 d=rd(H/'annotations.json'); by={w['id']:w for w in d['windows']};d['authoringCanvas']=[480,270]
 def mark(id,a,b,label,kind,role,keys,labelAt=(30,58),reason=''):
  w=by[id];w.update(startFrame=round(a*60),endFrame=round(b*60),label=label,shape=kind,colorRole=role,
   keyframes=[dict(frame=round(t*60),points=pts) for t,pts in keys],labelAt=list(labelAt),
   tracking='manually-keyframed-screen-space; rendered-motion verification pending',
   targetEvidence=reason,clearAtCut=True,fill=False,editorialGuideOnly=True,status='geometry-designed')
 def box(id,a,b,label,role,keys,**kw):mark(id,a,b,label,'ellipse',role,keys,**kw)
 def line(id,a,b,label,role,keys,**kw):mark(id,a,b,label,'contour',role,keys,**kw)
 def omit(id,reason):by[id].update(status='omitted',reason=reason)
 # Camera slowly changes; outline the same left building facade before its rapid swing.
 line('visibility',44.7,47.7,'관찰 대상 · 카메라에 보이는 면','reference',[
  (44.7,[[6,40],[170,22],[158,130],[2,121]]),
  (45.7,[[6,45],[174,25],[164,144],[2,130]]),
  (46.7,[[6,45],[174,25],[164,144],[2,130]]),
  (47.7,[[5,40],[170,20],[162,148],[2,133]])],labelAt=(228,62),reason='Same left facade in triangle diagnostic; does not claim per-pixel measurement.')
 box('wall-edge',94.5,99.1,'옆에서 본 벽','reference',[(94.5,[[270,106],[310,186]]),(96,[[270,106],[310,186]]),(97,[[270,90],[314,204]]),(98.5,[[270,95],[314,199]]),(99,[[270,106],[310,186]])],labelAt=(130,87),reason='Isolated thin wall turns around its centre; empty space keeps label legible.')
 omit('surface','Rapid camera orbit/zoom and occlusion; do not leave an approximate box on cars.')
 by['diagnostic']['label']='관찰 모드 · Reflections'
 mark('diagnostic',199.1,200.25,'반사 진단 보기 · Reflections','rectangle','reference',[(199.1,[[58,69],[150,80]]),(200.25,[[58,69],[150,80]])],labelAt=(168,103),reason='Actual Reflections menu row; clear before menu closes.')
 omit('doom-sector','Sub-second internal trailer cuts; persistent diagram already teaches sector brightness. Do not invent sector boundaries from texture alone.')
 omit('quake-texture','Multiple internal cuts in3seconds; retained independent explanation already distinguishes texture and lightmap.')
 line('seam',403.8,406.3,'구별해서 보기 · 이웃 면의 경계','distinction',[(403.8,[[343,135],[343,210]]),(406.3,[[343,135],[343,210]])],labelAt=(144,78),reason='Visible vertical brightness seam at adjoining wall sections; outline is offset so boundary remains visible; no asserted root cause.')
 mark('lm-resolution',437,439.8,'비교 조건 · 라이트맵 해상도','rectangle','reference',[(437,[[233,42],[451,72]]),(439.8,[[233,42],[451,72]])],labelAt=(155,99),reason='Visible LM Resolution128 label, clear before camera changes to another room.')
 box('lm-edge',454.3,457,'비교할 부분 · 글자 주변의 빛','result',[(454.3,[[126,165],[249,211]]),(457,[[126,165],[249,211]])],labelAt=(145,117),reason='Circle keeps the baked diffuse light around Games lettering visible; not the geometric room edge.')
 mark('uv',476,477.8,'UV · 그림의 어느 위치를 읽을까?','rectangle','reference',[(476,[[3,124],[149,212]]),(477.8,[[3,124],[149,212]])],labelAt=(172,72),reason='UV wire overlay becomes visible in lower left; actual visible address layout.')
 omit('quake2','Rapid trailer cuts; avoid suggesting a sampled screen area proves the underlying indirect-light algorithm.')
 line('baked-wall',539.4,540.5,'재료의 색을 가진 벽면','reference',[(539.4,[[228,121],[352,102],[347,211],[228,166]]),(540.5,[[229,120],[351,101],[347,211],[229,166]])],labelAt=(151,65),reason='Surface contour before camera passes through wall; end before occlusion.')
 line('editor-move',573.6,578.8,'편집 중인 물체 · 재계산 완료 아님','reference',[(573.6,[[213,138],[255,138],[255,179],[218,183],[213,138]]),(576.6,[[213,142],[255,142],[255,183],[218,187],[213,142]]),(577.1,[[213,151],[255,151],[255,191],[218,195],[213,151]]),(577.6,[[213,148],[255,148],[255,188],[218,192],[213,148]]),(578.8,[[213,146],[255,146],[255,186],[218,190],[213,146]])],labelAt=(135,79),reason='Selected left room object; right comparison room remains uncovered.')
 omit('floor','Selected camera interval shows building rather than road; do not label it as road. Find better current floor interval if needed.')
 box('mip',659.1,662.1,'결과 · 가는 무늬가 합쳐짐','result',[(659.1,[[22,66],[120,154]]),(662.1,[[22,66],[120,154]])],labelAt=(160,88),reason='Same rectangular material patch; visible mip-level detail change.')
 mark('mask',702.2,704.1,'RGB 색 ≠ 법선맵 · 패킹된 마스크','rectangle','distinction',[(702.2,[[78,72],[241,216]]),(704.1,[[78,72],[241,216]])],labelAt=(44,43),reason='Visible mask texture after zoom settles; end before channel menu appears.')
 omit('rail','Rapid foreground occlusion; use stable VR hand contour and magnified edge later for the same lesson.')
 box('triangles',813.5,814.7,'관찰 대상 · 삼각형으로 나뉜 면','reference',[(813.5,[[12,41],[178,159]]),(814.7,[[12,41],[178,159]])],labelAt=(217,70),reason='Same left facade during settled camera interval; no fabricated tile grid.')
 omit('doom3','Multiple crossfades within speech window; no persistent head outline over dissolving subjects.')
 omit('robot-inner','Rapid orbit/zoom makes this interval unsuitable for detailed tracing; clearer stable body surface is marked at1272s.')
 line('robot-outer',1019.8,1021.05,'실제 바깥 윤곽','distinction',[(1019.8,[[200,86],[239,82],[304,87],[331,111],[346,148],[347,173],[325,197]]),(1020.3,[[167,87],[197,77],[256,78],[294,89],[313,121],[315,150],[302,174]]),(1020.8,[[147,87],[175,78],[229,79],[264,87],[285,110],[288,143],[276,171]]),(1021.05,[[147,87],[175,78],[229,79],[264,87],[285,110],[288,143],[276,171]])],labelAt=(290,45),reason='Open contour outside curved torso plate; line leaves material interior uncovered and clears before rapid side orbit.')
 box('hl2',1054.5,1056.05,'관찰 · 인물과 주변 공간','reference',[(1054.5,[[199,87],[290,191]]),(1055,[[215,91],[277,189]]),(1055.5,[[219,92],[266,184]]),(1056.05,[[209,94],[265,183]])],labelAt=(32,65),reason='Hallway characters; clears before white crossfade. No claim this reveals RNM buffers.')
 line('robot-normal',1272,1278.4,'표면 안의 명암 · 면의 방향을 관찰','result',[(1272,[[260,122],[278,114],[311,114],[328,128],[334,166],[322,185],[274,186],[258,165],[260,122]]),(1278.4,[[260,122],[278,114],[311,114],[328,128],[334,166],[322,185],[274,186],[258,165],[260,122]])],labelAt=(213,55),reason='Stable torso front plate; contour encloses interior shading without labelling any particular detail as a measured normal-map effect.')
 box('probes',1445.6,1450.6,'공간 표본 · 전구가 아닌 조회 위치','reference',[(1445.6,[[166,116],[290,166]]),(1450.6,[[166,116],[290,166]])],labelAt=(71,58),reason='Floating rows of sample points above left room; points not emitters.')
 box('character',1540.1,1545.4,'결과 관찰 · 이동하는 몸체의 밝기','result',[(1540.1,[[144,79],[215,191]]),(1540.6,[[119,87],[184,205]]),(1541.1,[[163,76],[225,190]]),(1541.6,[[224,50],[289,158]]),(1542.1,[[241,51],[305,156]]),(1542.6,[[169,75],[237,192]]),(1543.1,[[151,73],[221,190]]),(1543.6,[[151,73],[221,190]]),(1544.1,[[151,73],[221,190]]),(1544.6,[[157,76],[229,194]]),(1545.1,[[241,49],[307,157]]),(1545.4,[[241,49],[307,157]])],labelAt=(50,44),reason='Selected mannequin translated in fixed room; reviewed yellow selection provides observed anchor, not a simulated path.')
 box('probe-depth',1613.1,1616.7,'공간 표본 · 벽이 아닌 공간에 배치','reference',[(1613.1,[[152,112],[283,204]]),(1616.7,[[152,112],[283,204]])],labelAt=(48,63),reason='Rows of blue sample markers, before further camera move; visible3D arrangement.')
 box('shadow-stairs',1909.8,1911.12,'발밑 비교 · 계단에는 그림자 없음','distinction',[(1909.8,[[192,153],[275,217]]),(1910.4,[[201,151],[263,212]]),(1910.9,[[203,159],[273,211]]),(1911.12,[[205,159],[278,211]])],labelAt=(38,62),reason='Observed stair/platform receiver under feet. Clear before return to shadow-casting ground; no detector claim.')
 box('csm-area',1942.1,1944.15,'색 경계 · 그림자를 기록할 영역','reference',[(1942.1,[[208,112],[446,195]]),(1943.1,[[208,112],[446,195]]),(1943.6,[[221,135],[414,202]]),(1944.15,[[226,155],[385,211]])],labelAt=(119,74),reason='Projection boundary region shrinks with settings. Clear before zero-distance hides lines.')
 mark('csm-setting',1957.6,1962.7,'조작 · 캐스케이드 개수','rectangle','reference',[(1957.6,[[280,74],[423,87]]),(1962.7,[[280,74],[423,87]])],labelAt=(265,127),reason='Actual Num Dynamic Shadow Cascades row shows4→0→1→3; label does not imply other settings fixed.')
 line('csm-far',1995,1998.4,'관찰 범위 · 먼 지형','result',[(1995,[[193,130],[221,156],[245,173],[271,176],[298,149],[338,135],[370,119],[402,133],[443,151]]),(1998.4,[[193,130],[221,156],[245,173],[271,176],[298,149],[338,135],[370,119],[402,133],[443,151]])],labelAt=(157,50),reason='Open guide follows terrain region below skyline, offset from visible shadow detail; not an exact cascade boundary.')
 line('book',2098.8,2100.9,'기본색 · 재료 자체의 색','reference',[(2098.8,[[205,169],[352,124],[419,171],[302,212]]),(2100.9,[[205,169],[352,124],[419,171],[302,212]])],labelAt=(198,79),reason='Unfolded brown cover in material export demonstration; clear before new play window opens.')
 line('vr',2244,2246.5,'관찰 · 손의 가는 윤곽','reference',[(2244,[[140,184],[146,171],[161,153],[176,143],[189,143],[191,150],[176,161],[168,177],[156,195],[148,198],[140,190]]),(2246.5,[[140,184],[146,171],[161,153],[176,143],[189,143],[191,150],[176,161],[168,177],[156,195],[148,198],[140,190]])],labelAt=(120,86),reason='Left VR hand held steady before approaching robot; trace offset outside silhouette.')
 box('msaa',2289,2291.1,'확대창 · 가장자리의 계단 현상','distinction',[(2289,[[241,42],[353,113]]),(2290,[[247,40],[360,108]]),(2291.1,[[241,37],[357,110]])],labelAt=(45,164),reason='Magnified diagonal edge; oval surrounds but does not cover edge. Clear before magnifier jumps.')
 line('reflection',2350,2354.6,'진단 결과 · 표면이 다르게 보임','result',[(2350,[[61,119],[119,110],[196,123],[268,117],[320,138],[320,203],[252,210],[155,193],[65,205]]),(2354.6,[[61,119],[119,110],[196,123],[268,117],[320,138],[320,203],[252,210],[155,193],[65,205]])],labelAt=(32,70),reason='Free open contour around reflection-debug road; no SSR implementation claim.')
 box('ao-gap',2388.3,2389.8,'틈 · 여러 방향의 빛을 받기 어려움','result',[(2388.3,[[109,129],[210,191]]),(2389.3,[[107,130],[209,194]]),(2389.8,[[107,130],[209,194]])],labelAt=(20,65),reason='Recess contact region on stacked cubes, empty ellipse preserves dark interior.')
 mark('ao-setting',2460.1,2461.25,'조작 · Power / Bias','rectangle','reference',[(2460.1,[[316,130],[440,153]]),(2461.25,[[316,130],[440,153]])],labelAt=(271,171),reason='Actual AO power and bias rows; no inferred numerical output.')
 box('ao-contact',2461.35,2462.9,'결과 관찰 · 큐브가 맞닿는 틈','result',[(2461.35,[[105,145],[196,190]]),(2462.9,[[105,145],[196,190]])],labelAt=(20,65),reason='Same recess after parameter edit; clear before camera pans to distant example.')
 d['revisionIntent']='Standalone general-viewer understanding: each visible mark names a narrated observation, not inferred engine data.'
 d['userReferenceImages']=['C:/Users/1/.codex/codex-remote-attachments/01a1382b-9f87-7b82-942b-ba38e671a085/9BB0F3B9-24B9-4F11-A092-BBB69378BAB7/1-사진-1.jpg','C:/Users/1/.codex/codex-remote-attachments/01a1382b-9f87-7b82-942b-ba38e671a085/9BB0F3B9-24B9-4F11-A092-BBB69378BAB7/2-사진-2.jpg']
 d['referenceUse']='Observed supplied screenshots: character silhouette/path linkage, not source footage/assets/measurements.'
 d['baselinePreservation']={'audio':'exactAAC','captions':'same KO/EN bytes and timing','duration':'same153402frames','actualExplanationRatio':'same57:43','priorMaster':'preserved'}
 d['unmarkedGroups']=[g for g in range(48) if g not in {w['group'] for w in d['windows'] if w['status']=='geometry-designed'}]
 d['unmarkedGroupReason']='Unmarked montages/short transitions/general statements have no additional reliably visible object-specific claim; avoid redundant or invented annotations.'
 wr(H/'annotations.json',d)
if __name__=='__main__':build()
