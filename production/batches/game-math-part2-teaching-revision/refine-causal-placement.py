"""Make a newly added prerequisite's promise match the immediate next lesson."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not any((ROOT/'shared/output/narration/game-math-quaternion-teaching-additions-v3').rglob('*scene.wav')),'Freeze narration script after synthesis starts'
p=B/'quaternion-additive-draft.json';d=read(p)
n=next(s for s in d['additions'] if s['id']=='N06');n['before']='15'
d['episodePlan']['first']['addedScenes']=[x for x in d['episodePlan']['first']['addedScenes'] if x!='N06']
d['episodePlan']['second']['addedScenes']=['N06','N07','N08']
d['causalPlacementReview']={'N06':'Dot/cross prerequisite immediately before original15 Hamilton product; its final promise matches the next explanation. Original06 same-axis composition remains early without premature general algebra. Original26 scenes unchanged.'}
write(p,d)
p=B/'quaternion-game-insertions.json';g=read(p)
for s in g['scenes']:
    s['ko']=[line.replace('이어지는 원래 장면','다음 주행 장면').replace('원래 장면','이어지는 장면') for line in s['ko']]
    s['en']=[line.replace('following original example','following example').replace('following original excerpt','following excerpt').replace('the original excerpt','the following excerpt') for line in s['en']]
g['scenes']=[s for s in g['scenes'] if s['id']!='GB06']+[{
 'id':'GB06','episode':2,'after':'14','title':'반대 기울기에서 두 회전의 합성으로','sourceId':'4Odvp_TIeQU','intervals':[[616,642]],'maximumSeconds':26,
 'ko':[
  '역회전은 적용한 회전을 상쇄하는 값이었습니다. 다른 주행 발췌에서 빨간 몸체 선과 파란 바퀴 윤곽을 함께 보겠습니다.',
  '커브에서는 몸이 기울면서 향하는 쪽도 바뀝니다. 이제 우리가 정한 두 회전을 하나의 자세값으로 이어 붙이려면, 네 성분끼리 단순히 더해도 될까요?',
  '다음 계산에는 같은 방향인지 비교하는 내적과, 두 방향에 수직인 벡터를 만드는 외적이 들어갑니다. 먼저 작은 숫자로 두 도구를 확인한 뒤 해밀턴 곱을 읽겠습니다.'
 ],
 'en':[
  'An inverse cancels an applied rotation. In this separate riding excerpt, follow the red torso direction and blue visible wheel contour together.',
  'A bend changes both the tilt and the facing direction. To compose our two defined rotations into one orientation, can we simply add the four components?',
  'The upcoming calculation uses a dot product to compare directions and a cross product to produce a perpendicular vector. We first verify these tools with small numbers, then read the Hamilton product.'
 ],
 'annotation':{'landmarks':'visible torso and fat rear-wheel contour; clear selected portion after initially occluding wheel jump','red':'projected torso direction','blue':'visible wheel contour','revealDuringLine':0}
}]
write(p,g)
print('N06 moved beside the operation requiring it; added a played-source composition question; no original narration changed')
