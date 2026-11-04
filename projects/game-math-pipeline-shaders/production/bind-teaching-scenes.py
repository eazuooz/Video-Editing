"""Map source speech to actual pipeline states; no estimated audio approval."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Ordered state transitions. Continuous demonstrations retain their one-variable
# animation between these anchors; actual PCM alignment supplies every clock.
A={
1:[('정점과 텍스처가',0),('삼각형을 화면에',1/3),('각 단계가',2/3)],
2:[('카메라의 위치와 방향',0),('보일 가능성이 있는',1)],
3:[('재질을 고릅니다',0),('이어서 정점과 삼각형',1/3),('더 단순한 메시를',2/3)],
4:[('정점 셰이더는',0),('다음에는 화면 밖',1/3),('픽셀 셰이더는',2/3)],
5:[('색을 계산했다고',2/3),('살아남은 결과를',.95)],
6:[('게임은 데이터와',0),('API를 통해',1/3),('개발자는 셰이더로',2/3)],
8:[('프런트 버퍼에는',0),('다 그린 뒤',.5)],
9:[('기존 깊이가',0),('새 값이 영 점 삼이면',1/3),('영 점 팔이 들어오면',2/3)],
10:[('가까운 곳이 영',0),('반대로 먼 곳을',.5)],
16:[('구조체의 배열',0),('배열의 구조체',.5)],
17:[('클립 위치와',0),('위치 변환과',.25),('법선을 다른 공간으로',.5),('그대로 전달하면',.75)],
18:[('모델 좌표의 점을',0),('월드에 놓고',.25),('카메라 기준으로',.5),('클립 좌표로',.75)],
20:[('둘 다 안이면',0),('둘 다 밖이면',.25),('밖에서 안으로',.5),('안에서 밖으로',.75)],
24:[('시계 방향, 반시계 방향',0),('물체를 거울처럼',.5)],
25:[('카메라도 오른쪽에',0),('법선의 제트 성분만',.5)],
27:[('단순 평균과',0),('원근 보정 보간이',.5)],
28:[('알파 테스트는',0),('알파 블렌딩은',1/3),('깊이 쓰기와 정렬도',2/3)],
34:[('텍스처만 보이던',0),('이제 빛을 더해',.5)],
38:[('정점에서 계산한 뒤',0),('결과도 완전히 같지는',.5)],
39:[('먼저 보간한 가운데',0),('반면 끝점을 먼저',.5)],
42:[('구로 셰이딩이 됩니다',0),('작은 하이라이트를',.5)],
43:[('한 개 계산했는지',0),('세 개 계산했는지',.5)],
44:[('방향광 세 개를',.5)],
50:[('텍스처 한 장에서',0),('빛을 더하고',.25),('노멀 맵을 더하고',.5),('뼈의 움직임까지',.75)],
51:[('펀더멘털스',0),('프린서플스',.2),('피비알티',.4),('리얼타임 렌더링',.6),('API의 공식 문서',.8)],
52:[('사 대 삼 화면에',0),('십육 대 구 화면에',.5)],
55:[('기본 오픈지엘',0),('전통적인 다이렉트삼디',.5)],
56:[('오픈지엘 쪽에',0),('다이렉트삼디 쪽은',.5)],
59:[('에이는 가로',0),('비는 정수만큼',1/6),('씨는 축이',2/6),('디는 사선으로',3/6),('이는 가로 진행이',4/6),('에프는 훨씬',5/6)],
60:[('정반사 색이 영이면',0),('지수가 작으면',1/3),('크면 좁게',2/3)],
61:[('에이와',0),('에프는',.1),('에이치는',.2),('아이는',.3),('제이는',.4),('비의 붉은',.5),('씨와 이보다',.6),('디는 더',.8),('지는 난반사',.9)],
62:[('마이너스 일, 영, 영은',0),('영, 영, 일은',.5)],
63:[('영 점 이육칠',0),('영, 영 점 팔오칠',.5)],
66:[('나머지 에이',0),('씨, 디도',1/3),('화면의 네 화살표를',2/3)],
67:[('정점 셰이더가',0),('래스터화가',1/3),('픽셀 셰이더와',2/3)],
}
def main():
 plan=read(P/'planning/production-plan.json');script=read(P/'script/narration.ko.json');module=read(P/'production/unity-staging/module-plan.json');models={b['sceneId']:b for b in module['beats']};games={g['sceneId']:g for g in plan['nativeGameCueBindings']};learning={b['id']:b for b in plan['learningSteps']};rows=[]
 for scene in script['scenes']:
  sid=scene['id'];n=int(sid);speech=' '.join(scene['lines']);shot=copy.deepcopy(models['001' if n==0 else sid]['shot']);shot.update(beatId=scene['sourceBeatId'],phaseSeconds=[],phasePositions=[])
  if n==61:shot['stepOrder']=[0,5,7,8,9,1,2,4,3,6]
  if n==60:shot['stepOrder']=[0,8,7]
  if n==66:shot['stepOrder']=[0,2,3]
  points=[]
  for phrase,pos in A.get(n,[]):
   assert speech.count(phrase)==1,(n,phrase,speech.count(phrase))
   points.append(dict(phrase=phrase,position=pos,character=speech.index(phrase)))
  assert all(a['character']<b['character'] and a['position']<=b['position'] for a,b in zip(points,points[1:])),n
  row=dict(id=sid,sourceBeatId=scene['sourceBeatId'],speech=speech,sourceParagraphs=learning[scene['sourceBeatId']]['sourceParagraphs'],renderer='Unity',classification='our-implementation',shot=shot,speechPhaseAnchors=points,hold=0,independentEditableSceneRequired=True,status='source-implemented-final-audio-and-layout-QA-pending',timing='Actual word timestamps pending; no guessed observation pauses')
  if sid in games:row['actualGamePart']=copy.deepcopy(games[sid])
  if n==0:row['classification']='actual-game-thesis-abstract-with-explanation-handoff'
  rows.append(row)
 assert len(rows)==68
 save(P/'planning/scene-bindings.json',dict(schemaVersion=1,updatedAt=datetime.now(timezone.utc).isoformat(),status='complete-design-awaiting-actual-speech-and-visual-QA',sourceNarrationSha256=hashlib.sha256((P/'script/narration.ko.json').read_bytes()).hexdigest(),allBodyParagraphsRetained=True,pendingImplementationBeatCount=0,actualNativeGameParts=len(games),humanViewed=False,scenes=rows))
 print('68 unchanged paragraphs / 67 model modes /',len(games),'native-game cuts /',sum(len(r['speechPhaseAnchors']) for r in rows),'verified visual-transition anchors')
if __name__=='__main__':main()
