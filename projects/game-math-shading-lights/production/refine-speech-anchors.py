"""Resolve inspected repeated/obsolete anchor phrases without changing speech."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1]
path=P/'planning/scene-bindings.json'
data=json.loads(path.read_text(encoding='utf-8-sig'));rows={x['id']:x for x in data['scenes']}
revisions={
 '006':['광원의 색이','재질의 색이','같은 채널끼리 곱해','영점이, 영점영이','영점영이가'],
 '012':['반짝임의 폭','영점팔','제곱하면','여덟 제곱','딱 맞는 방향'],
 '021':['재질의 색을','정면에서는','육십 도','영점사, 영점이, 영점일로','절반'],
 '035':['비스듬히 볼 때','또 재귀반사는 거울처럼 반대편으로'],
 '048':['하나의 위치','표면의 위치','그 길이','전구나 불','범위'],
 '061':['표면 지점을 광원의 좌표로 바꾼 다음','가령 고보에서','감쇠 맵에서','그 지점의 비율은','영점사입니다'],
 '062':['동차 좌표와 행렬','엑스, 와이, 제트, 더블유','고보는 엑스 나누기 더블유와','감쇠 맵은','빛의 그림 위에'],
 '064':['가로 길이','중심의','왼쪽 끝','오른쪽 끝','월드 좌표'],
}
changes=[]
for sid,anchors in revisions.items():
    row=rows[sid]
    if row['speechAnchorPhrases']!=anchors:changes.append({'scene':sid,'before':row['speechAnchorPhrases'],'after':anchors})
    row['speechAnchorPhrases']=anchors
    if sid=='012':
        row['cue'].update(diagram='math:custom',explanationSteps=['반사 방향 R과 시선 V의 일치','R·V = 0.8','0.8² = 0.64','0.8⁸ ≈ 0.17','정렬: 1ⁿ = 1 / 큰 지수 → 좁은 폭'])
    if sid=='064':
        row['cue'].update(diagram='math:custom',explanationSteps=['u = x/4 + 0.5','중심 x = 0 → u = 0.5','왼쪽 x = −2 → u = 0','오른쪽 x = 2 → u = 1','월드 → 광원 로컬 → 텍스처'])
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=P/'production/local/edit-v1/anchor-refinement.json'
if changes:
    out.write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'changes':changes,'reason':'Actual timestamp transcript exposed repeated numeric phrases, an obsolete literal and two screen sequences that preceded their spoken explanation. Retarget to unambiguous context and follow the existing narration order.','audioChanged':False,'narrationChanged':False,'asrTextChanged':False,'bindingsSha256':hashlib.sha256(path.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Refined',len(changes),'scene anchors; original audio and scripts unchanged.')
