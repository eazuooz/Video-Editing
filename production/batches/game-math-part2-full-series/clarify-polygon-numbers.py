"""Clarify audible counts and the fan anchor while preserving approved claims."""
from pathlib import Path
import datetime,hashlib,json,shutil
from production_control import require_current_authorization
R=Path(__file__).resolve().parents[3];slug='game-math-polygons-triangulation'
require_current_authorization(slug,'spoken polygon value clarification')
lease=R/'shared/output/GPU_HANDOFF.json'
if lease.exists() and json.loads(lease.read_text(encoding='utf-8-sig')).get('project')==slug:
 raise SystemExit('Finish the current full TTS batch before changing its script.')
P=R/f'projects/{slug}';lp=Path(__file__).parent/f'lessons/{slug}.json';kp=P/'script/narration.ko.json';ap=Path(__file__).parent/'author-geometry-polygons.py'
lesson=json.loads(lp.read_text(encoding='utf8'));ko=json.loads(kp.read_text(encoding='utf8'));author=ap.read_text(encoding='utf8')
edits=[
 ('12','경계를 반시계 방향으로 정했다면 볼록한 곳은 왼쪽으로 돕니다.','경계를 시계 반대 방향으로 정했다면, 볼록한 곳은 왼쪽으로 돕니다.'),
 ('12','단순한 다각형의 내각 합은 꼭짓점 수에서 이를 뺀 뒤 백팔십 도를 곱합니다.','단순한 다각형의 내각 합은 꼭짓점의 개수에서 두 개를 뺀 뒤, 백팔십 도를 곱합니다.'),
 ('13','일반적으로 꼭짓점 수에서 이를 뺀 개수입니다.','일반적으로 꼭짓점의 개수에서 두 개를 뺀 개수입니다.'),
 ('15','엘자의 사, 일을 부채꼴의 기준 꼭짓점으로 골라 보겠습니다.','엘자의 한 꼭짓점을 부채꼴의 기준으로 고릅니다. 이 점의 엑스 좌표는 사이고, 와이 좌표는 숫자 일입니다.'),
 ('15','경계 순서를 따라 네 삼각형을 만듭니다.','경계 순서를 따라 네 개의 삼각형을 만듭니다.'),
 ('22','유효한 네 삼각형의 넓이 이, 일 점 오, 일 점 오, 이를 더하면 칠입니다.','유효한 삼각형은 네 개입니다. 첫째와 마지막 삼각형의 넓이는 각각 숫자 이입니다. 둘째와 셋째의 넓이는 각각 일 점 오입니다. 네 넓이를 더하면 칠입니다.')
]
records=[]
for sid,old,new in edits:
 s=next(s for s in lesson['scenes'] if s['id']==sid);indices=[i for i,x in enumerate(s['ko']) if old in x];assert len(indices)==1,'Do not apply twice';i=indices[0];before=s['ko'][i];after=before.replace(old,new)
 assert author.count(old)==1;author=author.replace(old,new);s['ko'][i]=after
 target=next(s for s in ko['scenes'] if s['id']==sid);assert target['lines'][i]==before;target['lines'][i]=after
 records.append({'scene':sid,'line':i+1,'beforeKo':before,'afterKo':after,'matchingEnPreserved':s['en'][i],'reason':'Avoid ambiguous audible 이/일, coordinate(4,1), counts and counterclockwise phrase; preserve n−2,720degrees, four triangles and the same bad fan anchor.'})
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup=R/f'shared/output/{slug}/spoken-clarity/{stamp}';backup.mkdir(parents=True)
manifest=json.loads((P/'project.json').read_text(encoding='utf8'));out=R/manifest['tts']['outputDir']
for f in [lp,kp,ap,P/'production/script-review.json']:shutil.copy2(f,backup/f.name)
for sid in ['12','13','15','22']:
 for f in [out/f'chunks/{sid}-scene.wav',out/f'asr/{sid}.json']:
  if f.exists():shutil.copy2(f,backup/f.name)
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
write(lp,lesson);write(kp,ko);ap.write_text(author,encoding='utf8');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((P/'production/script-review.json').read_text(encoding='utf8'));review.update(status='reviewed-before-spoken-count-clarification-TTS',reviewedAt=stamp,lessonSha256=sha(lp),koChars=sum(len(x) for s in lesson['scenes'] for x in s['ko']),mathematicalClaimsUnchanged=True,spokenCountClarification=records);write(P/'production/script-review.json',review)
write(P/'production/spoken-value-clarification.json',{'status':'script-reviewed-current-voice-pending','edits':records,'preservedBaseline':backup.relative_to(R).as_posix(),'lessonSha256':sha(lp),'koScriptSha256':sha(kp),'currentVoiceReview':'pending','humanListening':'pending'})
print('Clarified12/13/15/22; current retakes and raw meaning review required; baseline preserved.')
