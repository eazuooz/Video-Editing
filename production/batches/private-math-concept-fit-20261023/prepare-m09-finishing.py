from common import *
P=R/'projects/game-math-lines-circles-v2';H=P/'production/concept-fit-v2'
SOURCES={
'grapple':dict(path='shared/output/private-game-math-polish-20261022/fhd-candidates/5u3sUKuncSU.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/uncle-5u3sUKuncSU-audio.m4a',url='https://www.youtube.com/watch?v=5u3sUKuncSU',game='A Story About My Uncle',minimumHeight=1080),
'factory':dict(path='shared/output/private-math-concept-fit-20261023/sources/satisfactory-official/SATISFACTORY_1.2_LAUNCHTRAILER_MASTER.mp4',url='https://www.satisfactorygame.com/press/',game='Satisfactory',minimumHeight=1440)}
SHOTS={
'02':dict(source='grapple',start=407,seconds=12.5,title='보이는 연결의 두 끝점',phases=[(0,5,'밝은 연결을 먼저 확인'),(5,11.2,'초록: 손 쪽 시작 · 파랑: 반대쪽 끝'),(11.2,12.5,'연결을 끊으면 표식도 제거')],model='두 점의 관계 · 계산용 선분',track=[(5,.69,.66,44),(5.5,.68,.60,44),(6,.68,.62,44),(6.5,.68,.65,44),(7,.67,.61,44),(7.5,.68,.62,44),(8,.68,.66,44),(8.5,.68,.64,44),(9,.68,.63,44),(9.5,.68,.64,44),(10,.69,.66,44),(10.5,.69,.66,44),(11,.67,.62,44)],track2=[(5,.597,.288,32),(5.5,.51,.386,32),(6,.54,.27,32),(6.5,.565,.19,32),(7,.547,.195,32),(7.5,.467,.20,32),(8,.472,.28,32),(8.5,.495,.29,32),(9,.508,.23,32),(9.5,.435,.145,32),(10,.432,.26,32),(10.5,.44,.38,32),(11,.24,.44,32)]),
'LG01':dict(source='factory',start=71.5,seconds=4.3,title='배선은 연결되는 두 지점부터',phases=[(0,1.5,'배선할 장치와 접점 선택'),(1.5,3.9,'연결할 접점과 케이블 미리보기'),(3.9,4.3,'연결 결과 → 계산용 선분과 비교')],model='곡선 모양 · 직선 연결은 별개',track=[(2,.5,.10,34),(2.2,.5,.10,34)],track2=[])}
def adapt(s):return s.replace('M08','M09').replace('m08','m09').replace('game-math-rotation-conversions-v2',P.name)
s=adapt((B/'compose-m08.py').read_text(encoding='utf8'));a=s.index('SOURCES={');z=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[z:]
s=s.replace('len(records)==26','len(records)==18').replace('26 exact-frame','18 exact-frame').replace('게임 축·각도의 측정값 아님','게임 거리·힘의 측정값 아님')
s=s.replace("for track in [s.get('track',[]),s.get('track2',[])]:","for ti,track in enumerate([s.get('track',[]),s.get('track2',[])]):")
s=s.replace("+'}'+shape,1)","+'}'+shape,1)")
s=s.replace("&HA2D380&}'+shape,1)","&H'+('A2D380' if ti==0 else 'FFB778')+'&}'+shape,1)")
(B/'compose-m09.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m08.py').read_text(encoding='utf8')).replace('len(levels)==25','len(levels)==16').replace('Matched25','Matched16').replace("['비시즈','쿼터니언'","['새티스팩토리','매개변수'");(B/'mix-m09.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m08.py').read_text(encoding='utf8')).replace('회전 보간 ② 같은 자세를 다른 표현으로 옮기기','직선과 경계 ① 두 점으로 연결선을 계산하기').replace('조립 화면과 고정된 부품의 표현 비교로','그래플의 두 끝점·배선과 계산용 선분 비교로');(B/'assemble-m09.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m08.py').read_text(encoding='utf8')).replace("['17','IG03','IG04','20','IG11','IG05','IG08','23','IG09','IG06']","['02','03','04','LG01','05','LG02','06','07','LP01','LG03','08','09']");(B/'qa-m09.py').write_text(s,encoding='utf8')
save(H/'scene-visual-plan.json',dict(sourceShots=SHOTS,renderer='Reuse all12 unchanged math clips; six Manim2D endpoint/path diagrams for revised game-dependent passages.',coordinateConvention='Authored2D A=(1,1), initial B=(5,3). Screen-space game marks are not engine coordinates.',models=dict(direction='A fixed; B=(3,2) then(5,3), differences(2,1)/(4,2), same unit direction and lengths√5/2√5.',path='Straight connection alongside an explicitly illustrative curved motion path; no physics claim.',fraction='New B=(4,5), difference(3,4), midpoint(2.5,3).',vertical='A=(1,1), B=(1,5), Δx0 and normal(1,0).'),tracking='Only visually observable endpoints highlighted; stop at beam release/occlusion, clear source cuts.',originalTeachingOrderPreserved=True,actualVisualQa='pending',actualListening=False))
for name in ['compose','mix','assemble','qa']:compile((B/f'{name}-m09.py').read_text(encoding='utf8'),name,'exec')
print('M09 finishing and source-coordinate plan prepared')
