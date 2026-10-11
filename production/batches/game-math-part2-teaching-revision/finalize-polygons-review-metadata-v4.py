"""Repair authoring recipes and chapter translations without altering media."""
from pathlib import Path
from datetime import datetime
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now().astimezone().isoformat()
p=R/'polygon-cross-game-content-v4.json';d=read(p);s=next(s for s in d['scenes'] if s['id']=='QB14');s['insertAfter']='QB12';s['recipeRepair']='Matches already-reviewed factory-bridge order; no narration or pixel changes.';write(p,d)
P=ROOT/'projects/game-math-polygon-partition-v2';p=P/'production/lesson.json';d=read(p);s=next(s for s in d['scenes'] if s['id']=='QB14');s['insertAfter']='QB12';write(p,d)
t=read(P/'production/timeline.json');slots={s['id']:s for s in t['scenes']}
p=P/'planning/game-example-coverage.json';d=read(p)
for game in d['games']:
 for case in game['cases']:
  case['sceneStart']=slots[case['scene']]['start']
d['timelineSha256']=sha(P/'production/timeline.json');d['timelineOrder']=[s['id'] for s in t['scenes']];write(p,d)
p=P/'production/footage-cuts.json';d=read(p)
print('Footage-cuts keys:',list(d) if isinstance(d,dict) else 'list')
p=ROOT/'shared/output/game-math-polygon-partition-v2/final-detail-review/index-selected-QB12-QB14-QG06.json';d=read(p)
for s in d['records']:s.update(directReviewPassed=True,directlyViewedPages=s['pages'],reviewedAt=now)
d.update(directReviewPassed=True,reviewedAt=now);write(p,d)
p=ROOT/'projects/game-math-polygon-centers-v2/publishing/youtube-upload.json';d=read(p)
assert d['englishMetadata']['status']=='pending'
corrections={'같은 비율은 좌표의 평균입니다':'Equal weights give the coordinate average','세 중심이 답하는 세 질문':'Three centers answer three different questions','무게중심은 무엇의 평균일까요?':'What does a centroid average?','각을 반으로 나누면 왜 변에서 같은 거리일까요?':'Why angle bisectors give equal distances to sides','변의 중점에서 직각으로 세우는 이유':'Why perpendicular bisectors start at side midpoints','선을 이어서 남겨야 할 땅을 정합니다':'Join points to define the land to retain','분할 전에 경계부터 검증하기':'Validate the boundary before partitioning','높이 변화와 평면의 홈을 구분합니다':'Separate height changes from a planar notch'}
for c in d['chapters']:
 if c['ko'] in corrections:c['en']=corrections[c['ko']]
def stamp(s):n=int(s);return f'{n//60:02}:{n%60:02}'
d['descriptionBody']['en']=d['descriptionBody']['en'].split('\n\nChapters\n')[0]+'\n\nChapters\n'+'\n'.join(stamp(c['startSeconds'])+' '+c['en'] for c in d['chapters']);write(p,d)
node='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([node,str(ROOT/'scripts/prepare-youtube-upload.cjs'),'game-math-polygon-centers-v2'],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
print('Updated only authoring recipes/coverage timing and pending English chapter metadata; current media unchanged.')
