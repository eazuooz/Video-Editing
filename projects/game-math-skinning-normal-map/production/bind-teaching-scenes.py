"""Bind the unchanged 36 paragraphs to observed games and existing Unity modes.

Phase positions describe semantic states, not seconds. Actual word timestamps
must supply the clock after the approved voice has been generated.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json

P=Path(__file__).resolve().parents[1];R=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# A repeated phase is a narrated explanation of a visible state, never an
# automatic silent observation hold or a slowed/looped commercial game clip.
anchors={
 1:[('조각상처럼',.15),('팔꿈치를 굽히려면',.5),('자연스럽게 이어지지는',.95)],
 2:[('관절마다 작은 좌표계를',0),('정점을 본에 연결해',.4),('여러 본에 연결되면',1)],
 3:[('그 비율이',0),('위팔과 아래팔의',.35),('극단적인 자세',1)],
 4:[('먼저 위팔에',0),('다음에는 아래팔에',1/3),('실제 정점은',2/3),('이것이 선형',1)],
 5:[('위팔 육십 퍼센트',0),('영점팔, 일점이',.45),('손 쪽 정점처럼',.5),('일점육, 영점사가',1)],
 6:[('본 번호와 각 가중치',0),('합이 일이',.5),('수학적인 한계는',1)],
 7:[('결과를 영으로',0),('본 목록을 순회',.25),('본 공간의 위치를',.5),('가중치를 곱해',.75),('다음 정점으로',1)],
 8:[('법선도 본의',0),('평행이동은 적용하지',.3),('비균일 크기 변환',.7),('역전치 변환',1)],
 9:[('바인드 포즈입니다',0),('그 본의 공간으로',1)],
 10:[('그 역행렬은',0),('그다음 현재 본의',.5),('현재 자세를 다시',1)],
 11:[('본의 원점이 가로 일',0),('본 공간에서는',.5),('정점은 사로',1)],
 12:[('본마다 정점 위치를',0),('바인드 역변환과 현재 변환',.5),('혼합 행렬로',1)],
 13:[('분배법칙으로 같습니다',0),('하지만 회전 행렬끼리',0),('부피가 줄어드는',.98)],
 14:[('관절을 여러 각도로',0),('추가 변형도',.85),('작은 요철은',1)],
 15:[('우리가 만든 같은 면',0),('높이 맵은',.1),('노멀 맵은',.5),('실제 정점이나 외곽선',1)],
 16:[('빨강, 초록, 파랑',0),('절반을 곱하고',.3),('두 배로 만든 뒤',.65),('푸른색 계열',1)],
 17:[('방향 숫자를 담은',0),('복원 후 정규화를',.4),('세밀한 고해상도 모델의',.5),('낮은 해상도 모델용',.7),('구워 넣는 제작',1)],
 18:[('상자의 윗면과 아랫면',0),('아랫면까지 위쪽',.45),('각 면에서 바깥쪽',.5),('기준축이 함께',1)],
 19:[('그 기준이 접선 공간',0),('티비엔 기저',.7),('함께 맞춰야',1)],
 20:[('여덟 비트 색이',0),('결과는 대략',.4),('이를 정규화하면',.7),('양자화 오차',1)],
 21:[('마이너스 엑스는',0),('각 성분에 해당 축',.5),('면이 돌아가도',1)],
 22:[('곡면에서는 법선이',0),('유브이를 비틀면',.4),('정규직교 기저로',1)],
 23:[('어느 쪽이든',0),('기저가 정규직교라면',0),('축들이 비스듬한데도',1)],
 24:[('법선 엔과 접선 티의 외적',0),('텍스처를 거울 대칭하면',.5),('비는 그 부호에',.8),('넣는 형식도',1)],
 25:[('삼각형의 세 정점',0),('큐 일과 큐 이',.35),('유의 차이는',.7),('집중하는 겁니다',1)],
 26:[('첫 번째 변은',0),('두 번째 변도',.5),('연립방정식인 셈',1)],
 27:[('이차 행렬의 역행렬',0),('접선은 티 이',.3),('비탄젠트는 마이너스',.65),('길이가 일인 벡터는',1)],
 28:[('숫자로 확인해',0),('행렬식은 일',.3),('접선의 길이를 일로',.7),('연결되었습니다',1)],
 29:[('음수 부호는 버리면',0),('유 방향만 반대로',.4),('부호를 보존합니다',1)],
 30:[('한 줄로 겹쳐',.8),('행렬식이 영이라면',1),('수치적으로 불안정',1)],
 31:[('정점 단위 값을',0),('누적값을 영으로',.4),('목록에 더해',.7),('법선은 별도로',1)],
 32:[('법선 방향 성분이',0),('이를 빼고 정규화',.5),('부호를 저장',1)],
 33:[('무조건 평균내면',0),('둘을 더하면 상쇄',.45),('정점을 분리해',.6),('방향을 보존합니다',1)],
 34:[('유브이, 접선, 부호를',0),('노멀 맵을 읽고',.25),('좌표를 바꿔',.5),('조명하는 과정',.75),('같은 약속으로',1)],
 35:[('큰 움직임과 작은 요철',0),('스키닝은',.3),('노멀 매핑은',.6),('함께 맞아야',1)]}

def main():
 plan=read(P/'planning/production-plan.json');script=read(P/'script/narration.ko.json')
 module=read(P/'production/unity-staging/module-plan.json');lookup={x['sceneId']:x for x in module['shots']}
 games={x['sceneId']:x for x in plan['nativeGameCueBindings']};steps={x['id']:x for x in plan['learningSteps']}
 rows=[]
 for scene in script['scenes']:
  sid=scene['id'];speech=' '.join(scene['lines']);m=lookup[sid];shot=copy.deepcopy(m['shot'])
  points=[]
  for phrase,position in anchors.get(int(sid),[]):
   assert speech.count(phrase)==1,(sid,phrase)
   assert 0<=position<=1
   points.append(dict(phrase=phrase,position=position,character=speech.index(phrase)))
  assert all(points[i]['character']<points[i+1]['character'] and points[i]['position']<=points[i+1]['position'] for i in range(len(points)-1))
  if sid=='000':
   shot=copy.deepcopy(lookup['001']['shot']);shot.update(beatId=scene['sourceBeatId'],englishTerm='Skinning and Normal Mapping',koreanTerm='스키닝과 노멀 매핑',meaning='큰 움직임에서 표면 방향까지')
  row=dict(id=sid,sourceBeatId=scene['sourceBeatId'],speech=speech,sourceParagraphs=steps[scene['sourceBeatId']]['sourceParagraphs'],renderer='Unity',classification='our-implementation',shot=shot,speechPhaseAnchors=points,hold=0,independentEditableSceneRequired=True,status='source-implemented-final-audio-and-layout-QA-pending',timing='Bind actual word timestamps before capture; no estimated narration pauses')
  if sid in games:
   game=copy.deepcopy(games[sid]);game['duration']=game['sourceOut']-game['sourceIn'];row['actualGamePart']=game
   if sid=='000':row['classification']='actual-game-thesis-abstract-with-explanation-handoff'
  rows.append(row)
 assert len(rows)==36 and len(games)==3
 save(P/'planning/scene-bindings.json',dict(schemaVersion=1,updatedAt=datetime.now(timezone.utc).isoformat(),status='complete-design-awaiting-actual-speech-timing-and-visual-QA',sourceNarrationSha256=sha(P/'script/narration.ko.json'),allBodyParagraphsRetained=True,pendingImplementationBeatCount=0,actualNativeGameParts=3,humanViewed=False,scenes=rows))
 print('Bound36 unchanged paragraphs,35 explanation modes and3 observed native games; no audio or final QA claim.')
if __name__=='__main__':main()
