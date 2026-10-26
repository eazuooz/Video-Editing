from pathlib import Path
import json
R=Path('D:/Github/VideoEditing')
# Each fraction is only a semantic placement preference, never an invented clock.
D25={
'01-p01':('puyo',.95,.9,1,'flow',['돌리고 옮기기','같은 색 4개','연결된 뿌요 제거'],'같은 색을 네 개 이상 연결합니다'),
'01-p02':('puyo',.75,.4,1,'color',['종류 A','종류 B','같은 모양'],'색 차이가 줄면, 종류를 알려 주던 단서도 줄어듭니다'),
'01-p03':('puyo',.85,.5,1,'flow',['구분할 단서','중요 대상','흑백 확인'],'정보 → 대상 → 시선의 순서로 살펴봅니다'),
'02-p01':(None,0,0,0,'color',['종류 A','종류 B','같은 모양'],'색 차이만 줄인 설명 그림'),
'02-p02':('puyo',.8,.5,1,'theme',['테마 A','테마 B','배경'],'블록과 배경의 조합을 함께 확인합니다'),
'03-p01':('puyo',.8,.5,1,'flow',['색 차이 감소','블록끼리 비교','배경과 비교'],'색각 시뮬레이션 · 색 구분의 문제를 미리 살핍니다'),
'03-p02':(None,0,0,0,'flow',['Protanopia-type','Deuteranopia-type','둘 다 확인'],'포토샵 · 보기 → 교정 설정 → 색맹 유형'),
'03-p03':('puyo',.4,0,.6,'setting',['색 조정 설정','색각별 필터','플레이어의 선택'],'뿌요뿌요 테트리스 2 · 실제 색 조정 설정'),
'04-p01':('puyo',.8,.5,1,'lightness',['어두움','밝음','배경'],'명도 차이가 남으면 경계를 찾기 쉽습니다'),
'04-p02':('puyo',.75,.4,1,'lightness',['어두운 블록','밝은 블록','어두운 배경'],'블록끼리 + 배경에서의 분리를 함께 봅니다'),
'04-p03':('puyo',.8,.5,1,'patterns',['동그라미','세모','줄무늬'],'색과 모양이 같은 정보를 함께 전달합니다'),
'05-p01':('mario',1,.8,1,'photo',['윤곽','물음표 표시','색 외의 단서'],'꽃과 블록은 윤곽과 표시도 다릅니다'),
'05-p02':('mario',1,.8,1,'flow',['눈에 보이는 단서','직접 행동','역할 이해'],'꽃에 닿기 · 블록 두드리기 → 실제 결과'),
'06-p01':('mario',.55,.2,.8,'grayscale',['같은 화면','색을 빼기','명도 배치'],'같은 화면에서 색만 뺀 비교입니다'),
'06-p02':('mario',1,.8,1,'photo',['앞쪽 길','다음 장애물','뒤쪽 풍경'],'진행에 필요한 대상부터 보이나요?'),
'06-p03':('mario',.8,.5,1,'photo',['배경 대비','중요 경계','판단 순서'],'시각적 위계 · 필요한 순서대로 시선을 이끕니다'),
'07-p01':('puyo',.8,.5,1,'flow',['색각 시뮬레이션','흑백 확인','서로 다른 질문'],'색 정보와 명도 위계를 나누어 검사합니다'),
'07-p02':('puyo',.7,.4,1,'flow',['익숙함 벗어나기','다르게 보기','실제 플레이어 검사'],'미리 보기 + 다양한 플레이어의 실제 경험'),
'08-p01':('puyo',.95,.85,1,'patterns',['종류를 찾기','배경에서 구별','행동 고르기'],'색은 정보를 전달하는 여러 단서 중 하나입니다')}
D26={
'01-p01':('moves',.9,.7,1,'range',['공격 거리','상대 위치','대응할 여지'],'움직임을 읽을 시간과 빈틈이 필요합니다'),
'01-p02':('cpu',.9,.6,1,'flow',['정보와 판단','공정함의 느낌','공략할 상대'],'판단 → 공정함 → 공략의 순서로 살펴봅니다'),
'02-p01':(None,0,0,0,'priority',['상황 없는 공격','위험으로 이동','상황을 읽는 판단'],'움직이는 것과, 상황을 읽는 것은 다릅니다'),
'02-p02':('cpu',1,.85,1,'flow',['CP / CPU','행동의 자유','반응 시간'],'컴퓨터가 조작하는 플레이어'),
'03-p01':('dice',.45,.3,.5,'photo',['주사위 눈','사용할 장비','상대의 행동'],'좋은 눈이 나왔다는 사실과 조작했다는 주장은 다릅니다'),
'03-p02':('dice',.3,.1,.45,'flow',['주사위 처리','행동 선택','공정함의 느낌'],'규칙의 공정함 + 체감하는 공정함'),
'04-p01':('cpu',1,.9,1,'photo',['이동','공격','혼자 하는 대전'],'스매시브라더스 얼티밋 · 실제 CP 대전'),
'04-p02':('cpu',1,.95,1,'flow',['공격','누적 대미지 %','멀리 날리기'],'퍼센트는 남은 체력이 아니라 쌓인 대미지입니다'),
'04-p03':('cpu',.8,.6,1,'flow',['위치·상태 데이터','행동 판단','다음 움직임'],'컴퓨터는 전달된 정보를 바탕으로 행동을 고릅니다'),
'04-p04':('cpu',1,.8,1,'range',['기술의 거리','발생 시점','이동 범위'],'내 기술과 상대 기술의 조건을 함께 비교합니다'),
'05-p01':(None,0,0,0,'range',['공격 2칸','상대 3칸','한 칸 접근'],'한 칸 접근 → 공격이 닿는 거리'),
'05-p02':('cpu',.95,.8,1,'flow',['다가오는 상대','기술 사용 중','조건에 맞는 선택'],'상대의 현재 상태가 선택을 바꿉니다'),
'06-p01':('cpu',.95,.8,1,'flow',['경기 흐름','유리한 거리','이동 특성'],'상태에 따른 행동 경향 · 일반 설계 원리'),
'06-p02':('cpu',.7,.4,.9,'flow',['경기 조건','강도 조절','판단 충돌'],'조건이 많아질수록 판단의 연결이 중요해집니다'),
'06-p03':(None,0,0,0,'priority',['다가가 공격','위험해 후퇴','우선순위 선택'],'언제 행동을 바꿀지도 정합니다'),
'07-p01':('cpu',1,.85,1,'flow',['상황을 알아챔','반응 간격','행동 시작'],'얼티밋 CP · 즉시 반응을 피하는 설계'),
'07-p02':(None,0,0,0,'delay',['알아챈 시점','행동 시점','12 ÷ 60 = 0.2초'],'설명 모형의 수치 · 실제 CP 지연 측정값이 아닙니다'),
'07-p03':(None,0,0,0,'flow',['조작 방향 반전','잠깐의 혼란','상태에 적응'],'짧은 혼란 뒤 회복 · 끝없는 추락으로 이어지지 않게'),
'08-p01':('cpu',1,.95,1,'flow',['공격에 나섬','행동이 드러남','대응할 기회'],'공격적인 상대는 읽고 대응할 기회도 줍니다'),
'08-p02':('cpu',1,.95,1,'flow',['상대의 공격','헛친 뒤 빈틈','다가가 반격'],'공격의 전후를 보고 공략합니다'),
'09-p01':('cpu',1,.85,1,'photo',['완벽한 방어?','공략할 여지','좋은 대결'],'완벽하게 막는 상대만으로 재미가 완성되지는 않습니다'),
'09-p02':('cpu',.95,.85,1,'flow',['정보','일관된 판단','시간·빈틈'],'컴퓨터 상대의 목적은 좋은 대결입니다')}
for slug,rows in [('limited-color-world',D25),('computer-controlled-players',D26)]:
 p=R/'projects'/slug/'planning/scene-layout.json'
 out={'schemaVersion':1,'slug':slug,'revision':'batch-v1','note':'Fractions are semantic placement preferences. Final clocks must be actual paid voice timings;60:40 measured globally. No source interval repeats.','paragraphs':{k:dict(zip(['pool','preferredActualShare','minActualShare','maxActualShare','mode','labels','summary'],v)) for k,v in rows.items()}}
 out['pools']={'puyo':[{'source':'puyo-pure','in':1070,'out':1216}], 'mario':[{'source':'wonder-before','in':.1,'out':36.4},{'source':'wonder-after','in':.1,'out':4.3},{'source':'wonder-after','in':4.3,'out':17.1},{'source':'wonder-after','in':18,'out':20.0},{'source':'wonder-after','in':21.0,'out':23.2},{'source':'wonder-after','in':24.2,'out':28.7},{'source':'wonder-after','in':30.1,'out':32.4}]} if slug=='limited-color-world' else {'moves':[{'source':'smash-mario','in':3.6,'out':6.0},{'source':'smash-mario','in':6.4,'out':8.6},{'source':'smash-samus','in':2.3,'out':4.0},{'source':'smash-samus','in':5.0,'out':8.0},{'source':'smash-samus','in':10.7,'out':13.9},{'source':'smash-samus','in':15.0,'out':17.0}], 'cpu':[{'source':'smash-cpu','in':118.4,'out':305.2}], 'dice':[{'source':'dicey-reunion','in':3.2,'out':5.15},{'source':'dicey-reunion','in':5.2,'out':7.35},{'source':'dicey-reunion','in':9.2,'out':11.45},{'source':'dicey-reunion','in':11.5,'out':13.4},{'source':'dicey-reunion','in':14.25,'out':15.4},{'source':'dicey-reunion','in':25.0,'out':27.3}]}
 p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(p)
