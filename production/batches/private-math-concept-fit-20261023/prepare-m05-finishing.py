"""Create episode-specific finite delivery scripts; shared caption/ASR helpers retained."""
from common import *
SOURCES={
 'totk':dict(path='projects/game-math-euler-axis-angle/production/local/revision-v3/sources/YNQ20CKbY8U-hls.mp4',url='https://www.youtube.com/watch?v=YNQ20CKbY8U',game='젤다의 전설: 왕국의 눈물',minimumHeight=1080),
 'se2':dict(path='shared/output/private-math-concept-fit-20261023/sources/se2-official/vs1.2.mp4',url='https://mirror.keenswh.com/PressKits/SE2%20Press%20Kit.zip',game='Space Engineers 2',minimumHeight=2160),
 'dorf':dict(path='shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm',url='https://www.toukana.com/dorfromantik/presskit',game='Dorfromantik',minimumHeight=1080)}
SHOTS={
 '02':dict(source='totk',start=418.,seconds=18.,title='통나무를 돌려 다리로 놓기',note='움직이는 위치와 긴 방향을 구분',phases=[(0,5,'통나무를 잡아 들어 올리기'),(5,13,'건너편으로 옮겨 위치 조절'),(13,16,'긴 방향을 돌려 다리와 맞추기'),(16,18,'통나무를 내려 다리로 배치')],track=[(15,.41,.39,82),(16,.41,.39,82)],model='앞쪽과 위쪽 · 자체 모형'),
 'GA01':dict(source='se2',start=101.,seconds=11.,title='부품을 복사해 배치하기',note='위치와 면의 방향을 구분',phases=[(0,3,'복사할 부품을 선택'),(3,6,'배치 미리보기의 앞면·옆면'),(6,11,'다른 위치로 옮겨 배치')],track=[(4,.57,.42,103),(5,.58,.42,103),(6,.59,.42,103),(7,.60,.42,103)],model='위치 이동 / 축 방향'),
 'QF30':dict(source='dorf',start=35.,seconds=9.,title='타일을 돌려 주변 지도에 배치',note='타일의 집 방향을 관찰',phases=[(0,5,'선택한 타일을 놓을 곳 찾기'),(5,7,'집이 있는 타일의 방향 바꾸기'),(7,9,'주변 타일과 맞춰 배치')],track=[(5,.51,.61,91),(6,.53,.60,91),(7,.42,.56,91)],model='타일 회전 · 자체 모형')}
def adapt(s):return s.replace('game-math-euler-axis-angle','game-math-quaternion-foundations-v3').replace('M04','M05').replace('m04','m05')
s=adapt((B/'compose-m04.py').read_text(encoding='utf8'));a=s.index('SOURCES={');b=s.index('ENC=',a)
s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[b:]
s=s.replace("SHOTS['14']['offset']=1.0",'').replace("if sid=='14'","if sid=='QF30'").replace('len(records)==26','len(records)==50').replace('26 exact-frame','50 exact-frame')
s=s.replace("'X   Y   Z = 물체의 축'","'X 앞 / Y 날개 / Z 위'")
(B/'compose-m05.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m04.py').read_text(encoding='utf8')).replace('len(levels)==30','len(levels)==46').replace('Matched30','Matched46').replace("['도르프로만틱','고리'","['도르프로만티크','스페이스 엔지니어스 투'")
(B/'mix-m05.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m04.py').read_text(encoding='utf8')).replace('오일러 각과 축·각','쿼터니언 ① 허수에서 회전과 역원까지').replace('고리 회전·배치와 타일 회전으로','통나무 다리·부품 복사 배치·타일 회전으로')
(B/'assemble-m05.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m04.py').read_text(encoding='utf8')).replace("offset=1.0 if s['id']=='14' else 0","offset=0").replace("['02','03','05','08','10','12','14','17','20','23','24','25']","['02','N01','N03','GA01','QF10','QF11','QF30','GA05','GA04','N05','11','13']")
(B/'qa-m05.py').write_text(s,encoding='utf8')
s=adapt((B/'preflight-m04.py').read_text(encoding='utf8')).replace("!='revised concept-matched demonstration'","!='concept-matched own model'").replace('18 changed-scene','Changed-scene')
(B/'preflight-m05.py').write_text(s,encoding='utf8')
for name in ['compose','mix','assemble','qa','preflight']:
 p=B/(name+'-m05.py');compile(p.read_text(encoding='utf8'),str(p),'exec')
print('M05 delivery scripts prepared; source actions require final timed playback checks')
