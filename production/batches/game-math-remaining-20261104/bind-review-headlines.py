"""Keep curriculum titles intact; add the actual opening question to local review."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
questions=[
 '전조등을 돌리자 바위의 굴곡이 보인다. 게임은 어느 면을 밝힐까?',
 '마리오가 착지할 때 팔과 다리는 어떻게 함께 움직일까?',
 '화면을 돌리면 어떤 지붕이 앞에 보일지 어떻게 정할까?',
 '마리오가 제자리로 돌아왔다면, 달린 거리는 얼마일까?',
 '게임 점프의 높이와 체공 시간은 어떻게 맞출까?',
 '속도계 숫자가 같아도 커브에서는 왜 가속도가 생길까?',
 '경사면 위 상자는 어느 순간부터 미끄러질까?',
 '요철을 넘은 바퀴는 왜 몇 번 흔들리다가 멈출까?',
 '부딪힌 뒤 물체가 어디로 튈지 어떻게 계산할까?',
 '대포를 쏘면 왜 차체가 밀리면서 뒤집힐까?',
 '출발점과 도착 방향을 정하면 그사이 경로는 어떻게 그릴까?',
 '곡선 밖의 점을 옮기면 왜 길의 모양이 바뀔까?',
 '이어 붙인 길에서 움직임이 꺾이지 않으려면 무엇이 같아야 할까?',
]
c=read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104'];assert c['productionAllowedNow']
for ep,title in zip(read(B/'batch.json')['items'],questions,strict=True):
 p=R/'projects'/ep['slug'];assert p.name in c['projectSlugs']
 f=p/'project.json';project=read(f);assert project['titles']['ko']==ep['title']
 project['localReviewHeading']=title
 f.write_text(json.dumps(project,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('13 source-matched local headings; curricular titles and platform untouched')
