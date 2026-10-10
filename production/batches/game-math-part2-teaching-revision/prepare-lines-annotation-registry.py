from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
prefix=(B/'lines-tracks').relative_to(ROOT).as_posix()+'/'
scenes={}
def add(ident,tracks,note,red,blue='',redline=0,blueline=0,tealline=0):
 assert all((ROOT/(prefix+t+'.json')).exists() for t in tracks)
 scenes[ident]={'landmarkSources':[prefix+t+'.json' for t in tracks],'revealAtLine':0,'redAtLine':redline,'blueAtLine':blueline,'tealAtLine':tealline,'redLabel':red,'blueLabel':blue,'tealLabel':'청록: 머리의 둥근 모습 비교 · 판정 구 아님','mathNote':note,'mathNoteAtLine':0,'mathNotePosition':[390,42],'movingPixelApproval':False}
add('02',['02'],'계산 예: o=(2,1), δ=(6,3)','보이는 연결의 두 끝점 비교')
add('05',['05'],'δ는 방향+길이 / d=δ/‖δ‖','손 쪽에서 보이는 연결점으로')
add('08',['08'],'계산 예: Δx=0 → 기울기 나눗셈 불가','화면에서 관찰한 연결 방향')
add('LG01',['LG01-a','LG01-b'],'출발 → 방향 변경 → 수신 표시·길','빨강: 지금 보이는 직선 빛줄기 부분')
add('LG02',['LG02-1','LG02-2'],'두 점의 연결선 ≠ 몸의 이동 경로','빨강: 관찰한 연결의 직선 비교')
add('LG03',['LG03-1','LG03-2'],'정의한 선분: p(t)=o+tδ, 0≤t≤1','빨강: 새 구간의 보이는 연결')
add('10',['10'],'정의한 구: 거리2=r → 경계 / 거리3>r','빨강: 색으로 구분한 효과의 관찰 부분','파랑: 선택한 화면 부분의 비교 범위',blueline=1)
add('13',['13'],'관찰한 모양 → 어떤 부분을 감쌀까?','빨강: 선택한 보이는 몸 부분','파랑: 선택한 점들의 화면 범위',blueline=2)
add('16',['16'],'경계 겹침 → 후보 / 실제 접촉은 별도','빨강: 선택한 보이는 몸 부분','파랑: 선택한 부분의 화면 범위',blueline=1)
add('LG04',['LG04'],'중심·반지름은 다음 그림에서 직접 정의','빨강: 둥근 머리의 관찰 비교',tealline=1)
add('LG05',['LG05'],'빈 모서리도 감싼 범위에 포함','빨강: 선택한 보이는 큐브 면','파랑: 그 면의 화면 가로·세로 범위',blueline=1)
add('LG06',['LG06-gray','LG06-blue'],'화면 범위 변화 ≠ 측정한 월드 회전','빨강: 선택한 보이는 몸 부분','파랑: 같은 부분의 화면 범위')
add('19',['19'],'카메라 변화 / 고정 월드 기준축은 별도','빨강: 선택한 보이는 목재 부분','파랑: 그 부분의 화면 범위')
add('LG07',['LG07-a','LG07-c'],'고정 구조물 / 투영 범위에는 빈 곳 포함','빨강: 선택한 보이는 목재 부분','파랑: 그 부분의 화면 범위')
add('21',['21'],'감쌀 입력: 실제 점들 / 이미 만든 상자','빨강: 보이는 다리 난간의 선택 부분','파랑: 선택한 부분의 화면 범위')
write(B/'lines-annotation-tracks.json',{'scope':'Editable selected screen observations; independent moving/final review required','semanticColors':{'red':'observed meaningful connection or selected object portion','blue':'enclosure of the same selected screen points','teal':'explicitly illustrative round screen comparison, never engine collision sphere'},'scenes':scenes,'allWorldMeasurementsVerified':False,'finalPixelApproval':False})
# Discard specifically inspected false/clipped beam detections, not source video.
hide={'02':[[0,27.7],[29.6,45]],'05':[[0,10.6],[12.3,31.5],[32.7,33.8],[34.5,51.9]],'08':[[0,20.5],[35.5,37.9]]}
for ident,intervals in hide.items():
 p=B/'lines-tracks'/f'{ident}.json';d=read(p);d['manualHideIntervals']=intervals;d['manualHideReason']='Direct source/candidate comparisons rejected isolated cuff/rune glow and clipped connections; hide unobserved endpoint relations';write(p,d)
print(json.dumps({'actualScenesRegistered':len(scenes),'finalPixelApproval':False}))
