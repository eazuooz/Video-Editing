"""Reuse the validated exact-frame delivery path, with M04's independently reviewed cuts."""
from common import *
import re
def adapt(name):
 s=(B/(name+'-m03.py')).read_text(encoding='utf8')
 return s.replace('game-math-orientation-matrices','game-math-euler-axis-angle').replace('M03-original','M04').replace('M03','M04').replace('compose-m03.py','compose-m04.py')
s=adapt('compose')
start=s.index('SOURCES={');end=s.index('ENC=',start)
s=s[:start]+'''SOURCES={
 'totk':dict(path='projects/game-math-euler-axis-angle/production/local/revision-v3/sources/YNQ20CKbY8U-hls.mp4',url='https://www.youtube.com/watch?v=YNQ20CKbY8U',game='젤다의 전설: 왕국의 눈물',minimumHeight=1080),
 'dorf':dict(path='shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm',url='https://www.toukana.com/dorfromantik/presskit',game='Dorfromantik · 도르프로만틱',minimumHeight=1080)}
SHOTS={
 '02':dict(source='totk',start=280.,seconds=11.,title='고리의 열린 쪽을 따라가기',note='고리를 돌려 판에 붙이기',phases=[(0,3,'고리를 분리해 잡기'),(3,7.5,'물체의 열린 쪽을 관찰'),(7.5,9.3,'열린 방향을 돌리기'),(9.3,11,'판에 붙이기')],track=[(7.7,.48,.27,74),(8.3,.47,.27,74),(9,.47,.22,74)],model='고리의 앞과 위 · 자체 모형'),
 '14':dict(source='dorf',start=46.5,seconds=6.5,title='타일의 방향을 주변과 맞추기',note='정지한 지도에서 선택 타일 회전',phases=[(0,2.5,'주변은 고정 · 선택한 타일'),(2.5,5,'타일의 방향 바꾸기'),(5,6.5,'주변과 맞춰 배치')],track=[(2.5,.605,.51,90),(3.5,.605,.51,90),(4.5,.605,.51,90),(5,.605,.51,90)],model='경로 계산은 자체 예시'),
 '20':dict(source='totk',start=293.,seconds=11.,title='붙인 물체를 들어 레일에 걸기',note='위치 이동과 회전량을 구분',phases=[(0,3,'판과 고리를 함께 잡기'),(3,6,'들어 올려 레일 위로 옮기기'),(6,9.5,'고리를 레일에 맞춰 내리기'),(9.5,11,'손을 놓아 걸린 결과 확인')],track=[(7,.52,.21,68),(8,.53,.21,68),(9,.53,.21,68),(10,.54,.22,68)],model='자세 변화와 이동은 별도 정보')}
''' +s[end:]
s=re.sub(r"SHOTS\['02'\]\['offset'\].*?\ndef ff",'\ndef ff',s,flags=re.S)
s=s.replace('len(records)==24','len(records)==26').replace("'24 exact-frame","'26 exact-frame")
# Diagram14 is a screen-space tile/path comparison, not a claimed measured game rotation.
s=s.replace("label(0,d,1320,818,'X   Y   Z = 물체의 축',28,'A7B0BC')", "label(0,d,1320,818,'각도는 자체 계산 예시' if sid=='14' else 'X   Y   Z = 물체의 축',28,'A7B0BC')")
(B/'compose-m04.py').write_text(s,encoding='utf8')
s=adapt('mix').replace('len(levels)==25','len(levels)==30').replace('Matched25','Matched30')
s=s.replace("source=A/'besiege-source.m4a' if s['source']=='besiege' else R/SOURCES[s['source']]['path']", "source=R/SOURCES[s['source']]['path']")
s=s.replace("['비시즈','기울기','replacement paragraph joins','game audio balance']","['도르프로만틱','고리','replacement paragraph joins','game audio balance']")
(B/'mix-m04.py').write_text(s,encoding='utf8')
s=adapt('assemble').replace('방향과 회전 행렬','오일러 각과 축·각')
s=s.replace('원래15분 강의의 수학 설명과 순서를 유지했습니다. 비행 예시를 물체 회전·조립으로 교체하고, 바뀐 게임 설명 사이의 자동 관찰 무음을 줄였습니다. 1080p60 · 12분49초.', '기존 강의의 수학 설명과 순서는 보존하고, 고리 회전·배치와 타일 회전으로 게임 예시를 수정했습니다. 1080p60 · {T["seconds"]/60:.1f}분.')
(B/'assemble-m04.py').write_text(s,encoding='utf8')
s=adapt('qa').replace("offset=2.5 if s['id']=='02' else 0","offset=0")
s=s.replace("['02','05','07','08','09','11','13','14','17','19','20','22']","['02','03','05','08','10','12','14','17','20','23','24','25']")
(B/'qa-m04.py').write_text(s,encoding='utf8')
for name in ['compose','mix','assemble','qa']:
 p=B/(name+'-m04.py');compile(p.read_text(encoding='utf8'),str(p),'exec')
print('Prepared M04 finishing scripts; execution awaits voice and render QA')
