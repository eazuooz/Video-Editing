"""Finish visual speech anchors without changing frozen narration or audio inputs."""
from pathlib import Path
from datetime import datetime,timezone
import json
P=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=read(P/'planning/scene-bindings.json')
anchors={
23:['전통적인 색 기반 식','물리적인 단위를','빛이 얼마나 오는지','재질이 어떻게 반사하는지','얼마나 정면으로'],
24:['직접광을 계산하니','벽이나 바닥에 튕긴 빛','환경광 값으로'],
32:['이렇게 각 항을','같은 시간에 더 많은','재질 입력과 결과의','네 성분이 현실의'],
35:['비스듬히 볼 때','또 재귀반사는'],
36:['표면의 결도','등방성 재질은','법선은 유지하고','결이 있는 금속이나','비등방성 반사입니다'],
43:['색이 텍스처에','정점 몇 개에서만','조명과 재질 색을','어떤 광원을 계산하든','합 바깥으로'],
46:['월드 공간에서','같은 공간으로','월드 법선과 물체 공간','같은 방향끼리','정규화를 확인해야'],
57:['두 문제가','거리가 영에 가까워지면','정확히 영이 되지는','최대값을 제한하거나','부드럽게 끊는'],
62:['동차 좌표와 행렬','엑스, 와이, 제트, 더블유','고보는','감쇠 맵은','빛의 그림 위에'],
69:['직접광의 계산 범위를','벽에 한 번 튕겨','미리 해 두고'],
72:['라이트맵에 무엇을','한 지점에 색 하나만','어느 쪽에서','복사조도라고','라디오시티는'],
73:['방향 차이를 남기려면','기본 모양으로','기본 함수들의 조합','계수를 적게 쓰면'],
77:['난반사용 정보는','날카로운 반사에는','거친 반사에는'],
78:['표면의 방향과 재질로','계산하는 위치를','라이트맵과','프로브는'],
}
# These adjacent passages introduce a relationship before the following
# numerical example. Do not reveal unspoken arithmetic early.
custom={
23:['전통 색 모델: 배율이 계수에 포함될 수 있음','물리 단위: 각 항의 의미를 구분','입사광: 얼마나 오는가','BRDF: 어떻게 반사하는가','코사인: 얼마나 정면으로 받는가'],
32:['성분별 계산과 조절','정확도와 처리할 픽셀·광원 수','재질 입력 → 결과를 예측','현실의 모든 빛을 그대로 나눈 것은 아님'],
43:['텍스처에 저장된 표면색','정점만으로는 내부 무늬를 읽지 못함','조명과 재질색의 항을 분리','같은 표면점에서는 공통인 재질색','재질색 × 광원 기여의 합'],
57:['역제곱 식의 두 구현 문제','d → 0: 값이 매우 커짐','유한 거리에서 정확히 0이 아님','중심 부근의 최대값 제한','영향 범위의 끝에서 부드럽게 0'],
62:['표면 위치 → 광원 동차 좌표','행렬 결과: (x, y, z, w)','고보: (x/w, y/w)에서 조회','깊이 감쇠: z 좌표에서 조회','표면의 점 → 빛의 무늬 위 위치'],
72:['저장한 물리량부터 확인','색 하나: 방향 기여의 합','어느 방향이 강했는지는 사라짐','복사조도 E: 면적당 입사량','라디오시티 B: 표면에서 나가는 양'],
}
values={
1:[('같은 계산식을 쓰더라도',0),('서로 다른 모습이',1)],
7:[('카메라만 움직여',-20),('반짝임이 나타났다 사라지죠',20)],
12:[('제곱하면',2),('여덟 제곱하면',8),('지수가 클수록',32)],
13:[('지수를 그대로 두고',.1),('하이라이트가 강해져요',1)],
18:[('카메라를 조금 옮겨도',-20),('기본 밝기가 크게 바뀌지',20)],
19:[('정면으로 받으면',0),('종이를 기울이면',25),('작은 칸 하나가',60)],
20:[('방향이 같으면',0),('육십 도',60),('구십 도면',90),('내적이 음수인 뒷면',120)],
24:[('직접광을 계산하니',0),('환경광 값으로',1)],
25:[('계산은 간단합니다',0),('같은 채널끼리 곱합니다',1)],
26:[('발광은',0),('조명을 꺼도',1)],
30:[('내적에 영점오',0),('내적이 영인 옆면',90)],
31:[('한 광원의 결과',0),('광원을 하나 더 켜',1)],
41:[('각 픽셀에서',-25),('반짝임도 잡을 수',25)],
51:[('아이콘을 옮겨도',-1),('조명은 같고',2)],
53:[('점 광원에서 멀어지는',1),('거리가 두 배면',2)],
55:[('카메라만 멀어지면',7),('물체는 화면에서 작아지죠',12)],
58:[('안쪽 거리까지는',2),('바깥 거리부터는',6),('사 미터에서',4)],
}
for row in data['scenes']:
    n=int(row['id'])
    if n in anchors:
        for phrase in anchors[n]:assert phrase in row['speech'],(n,phrase)
        row['speechAnchorPhrases']=anchors[n]
    if n in custom:
        row['cue']['diagram']='math:custom';row['cue']['explanationSteps']=custom[n]
    if n in values:
        for phrase,_ in values[n]:assert phrase in row['speech'],(n,phrase)
        row['valueAnchorPhrases']=[{'phrase':p,'value':v} for p,v in values[n]]
    row['timing']='Actual full-voice word ASR required before production capture; no estimated observation silence.'
data['updatedAt']=datetime.now(timezone.utc).isoformat()
save(P/'planning/scene-bindings.json',data)
print('Added literal speech anchors and deferred premature numeric reveals; narration unchanged.')
