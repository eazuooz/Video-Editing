from common import *
P=R/'projects/game-math-plane-distances-v2';H=P/'production/concept-fit-v2'
SOURCES={'polybridge3':dict(path='shared/output/private-math-concept-fit-20261023/sources/polybridge-official/release-trailer.mp4',url='https://store.steampowered.com/app/1850160/Poly_Bridge_3/',game='Poly Bridge 3',minimumHeight=1080)}
SHOTS={
 '02':dict(source='polybridge3',start=8,seconds=3.5,title='차량이 놓인 다리의 표면',phases=[(0,3.5,'초록 선: 유한한 다리 표면의 앞쪽 경계')],model='유한한 표면 / 계산용 평면',track=[],track2=[],contours=[[(.2,[(771,590),(1219,559)]),(.5,[(775,590),(1220,552)]),(1.5,[(755,582),(1210,562)]),(2.5,[(741,574),(1205,577)]),(3.4,[(738,568),(1200,585)])]]),
 'PG02':dict(source='polybridge3',start=17,seconds=2.8,title='다리가 열리며 표면이 기울어짐',phases=[(0,2.8,'초록 선: 왼쪽 다리 표면의 앞쪽 경계')],model='면의 회전 / 함께 변하는 법선',track=[],track2=[],contours=[[(.8,[(716,726),(798,729),(965,687)]),(1,[(716,726),(798,731),(948,675)]),(1.5,[(713,724),(794,727),(903,673)]),(2,[(709,718),(786,725),(868,683)]),(2.5,[(708,710),(780,721),(855,686)]),(2.75,[(706,704),(776,715),(853,683)])]]),
 '08':dict(source='polybridge3',start=5.8,seconds=2.1,title='연결점 세 개로 삼각형 만들기',phases=[(0,1.5,'연결점을 놓고 선으로 이어 붙이기'),(1.5,2.1,'초록 윤곽: 완성된 삼각형 한 개')],model='직접 정한 A · B · C / 둘레 순서',track=[],track2=[],contours=[[(1.5,[(773,688),(861,556),(949,688),(773,688)]),(2.09,[(773,688),(861,556),(949,688),(773,688)])]])}
def adapt(s):return s.replace('M10','M11').replace('m10','m11').replace('game-math-bounds-transform-v2',P.name)
s=adapt((B/'compose-m10.py').read_text(encoding='utf8'));a=s.index('SOURCES={');z=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[z:]
s=s.replace('len(records)==25','len(records)==19').replace('25 exact-frame','19 exact-frame').replace('게임 내부 경계의 측정값 아님','게임 내부 좌표의 측정값 아님')
insertion=r'''
 # Inspectable surface contours, interpolated between observed source pixels.
 for keys in s.get('contours',[]):
  for (a,points),(b,nextpoints) in zip(keys,keys[1:]):
   steps=max(1,round((b-a)*60))
   for frame in range(steps):
    u=(frame+.5)/steps;t0=a+(b-a)*frame/steps;t1=a+(b-a)*(frame+1)/steps
    pts=[((p[0]*(1-u)+q[0]*u)*2/3,130+(p[1]*(1-u)+q[1]*u)*2/3) for p,q in zip(points,nextpoints)]
    for p,q in zip(pts,pts[1:]):
     x=min(p[0],q[0]);y=min(p[1],q[1]);shape=f'm {p[0]-x:.2f} {p[1]-y:.2f} l {q[0]-x:.2f} {q[1]-y:.2f}'
     event(t0,t1,'{\\an7\\pos('+f'{x:.2f},{y:.2f}'+')\\p1\\bord3\\shad0\\1a&HFF&\\3c&HA2D380&}'+shape,1)
'''
# Raw insertion contains ASS escapes as Python source, exactly like the surrounding drawing code.
s=s.replace(" path=C/f'{sid}.guides.ass'",insertion+" path=C/f'{sid}.guides.ass'")
(B/'compose-m11.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m10.py').read_text(encoding='utf8')).replace('len(levels)==18','len(levels)==17').replace('Matched18','Matched17').replace("['타이니 글레이드','반크기'","['폴리 브리지 쓰리','법선'");(B/'mix-m11.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m10.py').read_text(encoding='utf8')).replace('직선과 경계 ② 물체의 범위와 회전 뒤 경계','평면과 삼각형 ① 표면까지의 거리').replace('건물 배치·높이 변경과 계산용 경계 비교로','다리 표면·기울기·삼각형 조립과 계산용 평면 비교로');(B/'assemble-m11.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m10.py').read_text(encoding='utf8')).replace("['10','LG04','11','12','13','LG05','16','LG06','19','20','LG07','21']","['02','PG01','03','PG02','05','06','08','PG03','09','PF02']");(B/'qa-m11.py').write_text(s,encoding='utf8')
save(H/'scene-visual-plan.json',dict(sourceShots=SHOTS,renderer='Preserve13 original mathematical clips; six independently editable Manim plane/triangle models using explicit orthographic projection. Reuse existing math renderer without duplicating game physics in Unity.',coordinateConvention='Own RH columns, Y up; plane n dot X=d. Ordered XZ perimeter gives negativeY normal. Game marks are screen-space editorial contours, not reconstructed game coordinates.',models=dict(finite='Finite deck compared with infinite plane; point can be coplanar yet outside panel.',distance='Normal projection P-n(n dot P) for a unit normal and origin plane; general n dot X=d signed formula is shown separately.',camera='Fixed model point and surface; view azimuth changes without claiming world height changes.',triangle='Vertex order reversal negates cross product; side-view trusses do not establish a rendering mesh.',polygon='Tilted pentagon with explicit raised occluding strip; hidden contour dashed, then perimeter traced in order.'),unchangedParagraphs=56,changedSourceDependentParagraphs=17,sourceReuseReason='Three different operations in one construction game directly match finite surface, inclination and constructing triangular connections; no repeated traversal filler.',preflight='12 frames in2 sheets inspected; edge-on pentagon view corrected and its perimeter-normal sign matched. Corrected PG03 check pending.',actualVisualQa='pending',actualListening=False))
for n in ['compose','mix','assemble','qa']:compile((B/f'{n}-m11.py').read_text(encoding='utf8'),n,'exec')
print('M11 finishing prepared')
