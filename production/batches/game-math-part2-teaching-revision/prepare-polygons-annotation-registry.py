"""Narration gates for editable observed annotations; approval stays pending."""
from pathlib import Path
import json
B=Path(__file__).parent
def scene(ids,red,note,blue=None,yellow=None):
 s={'landmarkSources':[f'production/batches/game-math-part2-teaching-revision/polygons-tracks/{i}.json' for i in ids],'revealAtLine':0,'redAtLine':0,'blueAtLine':0,'yellowAtLine':0,'redLabel':red,'mathNote':note,'mathNoteAtLine':0,'mathNotePosition':[390,42],'movingPixelApproval':False}
 if blue:s['blueLabel']=blue
 if yellow:s['yellowLabel']=yellow
 return s
scenes={
 '02':scene(['02'],'빨강: 화면에 보이는 다음 타일의 외곽','꼭짓점 평균: 같은 비중으로 섞은 기준점','파랑: 선택한 화면 관찰 기준점'),
 '05':scene(['05'],'빨강: 풀과 길 사이의 보이는 경계','중심 위치 ≠ 모든 가장자리까지의 거리'),
 '08':scene(['08'],'빨강: 빈 통로와 맞닿은 바위 외곽','세 꼭짓점까지 같은 거리: 외심의 조건'),
 '11':scene(['11'],'빨강: 빈 칸과 맞닿은 땅의 경계','경계 순서와 오목한 모서리부터 확인'),
 '14':scene(['14'],'빨강: 가리지 않은 바위 천장의 경계','임의의 연결은 빈 공간을 덮을 수 있음'),
 '17':scene(['17'],'빨강: 통로에 드러난 눈 지형의 경계','귀 조건: 볼록·교차 없음·다른 점 없음'),
 '19':scene(['19'],'빨강: 두 발판 사이에 드러난 윗변','가느다란 조각은 수치 오차에 민감'),
 '21':scene(['21'],'빨강: 발췌 화면의 밭 타일 외곽','분할 뒤에도 경계와 연결 정보를 유지'),
 'QG01':scene(['QG01-reference','QG01-rotate'],'빨강: 노출된 지붕 면의 바깥선','기준점 하나와 전체 바깥선의 역할 구분','파랑: 선택한 화면 관찰 기준점'),
 'QG02':scene(['QG02-arch','QG02-gameplay'],'빨강: 새로 열린 문의 보이는 가장자리','벽을 바꾸면 안과 밖의 경계도 바뀜'),
 'QG03':scene(['QG03-height','QG03-opening'],'빨강: 높이 기준·실제 통로의 노출된 경계','높이 변화와 평면의 오목함을 구분'),
 'QG04':scene(['QG04-notch'],'빨강: 발판의 노출된 경계','땅과 빈 공간을 경계 순서로 구분',yellow='노랑: 실제로 비어 보이는 통로 부분'),
 'QG05':scene(['QG05-opening'],'빨강: 인물이 지나는 바위 틈의 경계','분할해도 원래 빈틈을 막으면 안 됨'),
 'QG06':scene(['QG06-circle','QG06-square'],'빨강: 보이는 도형을 나누는 화면 기준선','입력 도형 → 나누기 → 출력 조각 확인'),
 'QG07':scene(['QG07-passage','QG07-return','QG07-path'],'빨강: 통로 경계·만들어지는 비교 경로','원래 순서를 지키며 다음 연결을 선택')
}
def gate(s,key,keyword,line):scenes[s][key+'Keyword']=keyword;scenes[s][key+'AtLine']=line
def track_gate(s,track,key,keyword,line):scenes[s].setdefault('trackReveal',{}).setdefault(track+'-observed-patch',{})[key]={'keyword':keyword,'line':line}
gate('QG01','red','기준점',0);gate('QG01','blue','파란',0)
track_gate('QG01','QG01-rotate','red','모양',1);track_gate('QG01','QG01-rotate','blue','가운데',1)
gate('QG02','red','빨간',0);track_gate('QG02','QG02-gameplay','red','벽',1)
gate('QG03','red','빨간',1);track_gate('QG03','QG03-height','red','높이',0)
gate('QG04','red','빨간',1);gate('QG04','yellow','노란',1)
gate('QG05','red','빨간',0)
gate('QG06','red','원',0);track_gate('QG06','QG06-square','red','사각형',1)
gate('QG07','red','복도',0);track_gate('QG07','QG07-return','red','빈틈',0);track_gate('QG07','QG07-path','red','꺾인',1)
record={'scope':'Narrated observations over real1x footage, no extrapolation or unverified engine inference; moving final pixels remain pending.','semanticColors':{'red':'visible edge or explicitly projected comparison route/divider','blue':'chosen observed screen reference, not a game pivot or measured centroid','yellow':'visibly empty passage, not measured world space'},'scenes':scenes}
for spec in scenes.values():spec['mathNotePosition']=[390,85]
scenes['QG07']['omitMathNote']=True # preserve the native right-hand editor tooltip
scenes['QG01']['omitMathNote']=True # keep the roof resizing/rotation controls visible throughout
(B/'polygons-annotation-tracks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(scenes),'actual scene annotation plans, final pixel approval pending')
