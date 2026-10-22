"""Prepare finite M06 finishing scripts with inspected, non-repeated source windows."""
from common import *
P=R/'projects/game-math-quaternion-calculations-v3'
count=len(read(P/'production/timeline.json')['scenes'])
SOURCES={'se2':dict(path='shared/output/private-math-concept-fit-20261023/sources/se2-official/launch.mp4',url='https://mirror.keenswh.com/PressKits/SE2%20Press%20Kit.zip',game='Space Engineers 2',minimumHeight=2160)}
SHOTS={
 '14':dict(source='se2',start=46.7,seconds=6.9,title='부품의 방향을 맞추고 배치하기',note='앞면과 긴 몸체의 방향을 관찰',phases=[(0,1.8,'두 둥근 면의 방향을 관찰'),(1.8,4.5,'긴 몸체를 붙일 방향과 위치로'),(4.5,6.9,'붙일 곳에 맞춰 부품 배치')],track=[(.3,.50,.49,65),(1.3,.49,.39,65)],track2=[(2.3,.50,.66,145),(3.3,.49,.66,145),(4.3,.48,.62,145),(5.3,.49,.62,145)],model='회전과 이동 · 자체 모형'),
 'QC20':dict(source='se2',start=95.5,seconds=4.,title='부품의 앞면을 원하는 방향으로',note='배치 미리보기의 앞면을 관찰',phases=[(0,1.3,'부품 미리보기의 앞면'),(1.3,2.8,'앞면 방향을 돌려 맞추기'),(2.8,4.,'원하는 방향으로 부품 배치')],track=[(.5,.53,.53,115),(1.5,.51,.54,115),(2.5,.50,.56,115)],model='현재 방향 → 목표 방향')}
def adapt(s):return s.replace('game-math-quaternion-foundations-v3','game-math-quaternion-calculations-v3').replace('M05','M06').replace('m05','m06')
s=adapt((B/'compose-m05.py').read_text(encoding='utf8'));a=s.index('SOURCES={');z=s.index('ENC=',a)
s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[z:]
s=s.replace('len(records)==50',f'len(records)=={count}').replace('50 exact-frame',f'{count} exact-frame')
a=s.index('  # Enlarging only');z=s.index('  if sid in SHOTS:',a)
s=s[:a]+"  prep='[0:v]null[prepared];'\n"+s[z:]
s=s.replace("'각도는 자체 계산 예시' if sid=='QF30' else 'X 앞 / Y 옆 / Z 위'","'게임 축·각도의 측정값 아님'")
(B/'compose-m06.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m05.py').read_text(encoding='utf8')).replace('len(levels)==46','len(levels)==37').replace('Matched46','Matched37').replace("['도르프로만티크','스페이스 엔지니어스 투'","['스페이스 엔지니어스 투','역원'")
(B/'mix-m06.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m05.py').read_text(encoding='utf8')).replace('쿼터니언 ① 허수에서 회전과 역원까지','쿼터니언 ② 합성·목표 자세·벡터 회전').replace('통나무 다리·부품 복사 배치·타일 회전으로','조립 부품의 회전·배치와 고정 모형의 순서 비교로')
(B/'assemble-m06.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m05.py').read_text(encoding='utf8')).replace("['02','N01','N03','GA01','QF10','QF11','QF30','GA05','GA04','N05','11','13']","['14','GB01','QC10','17','QC20','GB03','20','GB04','QC31','23']")
(B/'qa-m06.py').write_text(s,encoding='utf8')
for n in ['compose','mix','assemble','qa']:
 p=B/(n+'-m06.py');compile(p.read_text(encoding='utf8'),str(p),'exec')
save(P/'production/concept-fit-v2/scene-visual-plan.json',dict(coordinates='RH column vector X-front Y-side Z-up; preserve original quaternion lesson.',renderer='Reuse Manim mathematical renderer, authored twin-tube assembly module and fixed-coordinate airplane; no duplicate engine demo.',sourceShots=SHOTS,sourceMeaning='Editorial circles identify the visible front/module. Exact game quaternion, axes or angle not measured.',models=dict(order='Two identical fixed-position parts, intrinsic Z→X versus X→Z: Rz Rx versus Rx Rz.',inverse='Undo the defined tilt while leaving translated position unchanged.',referenceFrame='World axis stays fixed; body axis follows part.',history='90 and450 degrees end at the same pose; history is separate.',power='90 versus45 degrees about the same fixed Z axis.',vector='(1,0,1) under Rz90 becomes(0,1,1), norm sqrt2.',camera='Object remains fixed while viewing camera changes.'),reuse='Original unchanged math clips, global composition and spacing overlays retimed; original script/order/voice retained outside37 game-specific paragraphs.',actualVisualQa='pending rendered output',actualListening=False))
print('M06 finishing scripts prepared; source cuts10.9s; original scene count',count)
