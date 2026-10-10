"""Preserve observed v1 evidence and prepare only the five affected scenes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig')); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix(); now=lambda:datetime.now(timezone.utc).isoformat()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
source=ROOT/'motion-canvas/src/projects/character-parameters/spatial-character-explanation.tsx'
old=source.read_text('utf-8')
repairs=[
 ("tag('지상',-470,265);tag('높은 발판',40,-190,340);tag('바깥 공간',520,270);","tag('지상',-470,265);tag('높은 발판',40,-190,230);tag('바깥 공간',520,270);"),
 ("const obstacle=new Node({zIndex:()=>s.rotate(480,25)[1],opacity:()=>phase(3),children:s.solid(480,25,20,95,90,190,D.red)});world.add(obstacle);\n  const secondEnemy=new Node({zIndex:()=>s.rotate(620,25)[1],opacity:()=>phase(3),children:s.solid(620,25,20,80,85,155,D.red)});world.add(secondEnemy);","const obstacle=new Node({opacity:()=>phase(3),children:s.solid(480,25,20,95,90,120,D.red)});world.add(obstacle);"),
 ("tag('세 항목을 섞어 비교하지 않기',0,-185,330,30);","tag('세 항목을 섞어 비교하지 않기',0,-185,235,30);"),
 ("tag('현재 턴',-350,310,25);tag('다음 턴',360,100,25);","tag('현재 턴',-350,310,25);tag('다음 턴',360,-195,200);"),
 ("tag('STA 주사위 2개',360,-180,330,30,D.title);\n  const currentEffect=s.label('피해 / 현재 효과',-350,520,25,29,D.orange);\n  currentEffect.opacity(()=>1-phase(1));world.add(currentEffect);\n  const separateStrike=s.label('별도 STRIKE: 하트 감소',-350,520,25,27,D.orange);\n  separateStrike.opacity(()=>phase(1));world.add(separateStrike);","tag('STA 주사위 2개',360,-45,260,30,D.title);\n  world.add(<Node opacity={()=>1-phase(1)}>{s.label('피해 / 현재 효과',-350,190,125,29,D.orange)}</Node>);\n  world.add(<Node opacity={()=>phase(1)}>{s.label('별도 STRIKE: 하트 감소',-350,190,125,27,D.orange)}</Node>);"),
 ("tag('조건이 늘면 검사 경로도 늘어납니다',0,-235,300,28);","tag('조건이 늘면 검사 경로도 늘어납니다',0,-235,180,28);")]
for a,b in repairs:assert old.count(a)==1;old=old.replace(a,b)
oldbytes=old.encode('utf-8'); expected=next(x['sha256'] for x in read(BASE/'prepared-independent-mc-v1.json')['paths'] if x['path']==rel(source))
assert hashlib.sha256(oldbytes).hexdigest()==expected,'Historical source bytes must match the actual prepared v1 hash.'
(BASE/'spatial-character-explanation-preserved-v1.tsx').write_bytes(oldbytes)
qa=read(BASE/'black-structural-qa-v1.json')
assert len(qa['boards'])==13 and len(qa['samples'])==74 and all(sha(ROOT/x['path'])==x['sha256'] for x in qa['boards']+qa['samples'])
issues=[dict(scene='05-useful-strength',observation='Raised-platform label overlaps the moving orange token in p2 late and p3 samples.',repair='Raise the independent label above the maximum token height.'),dict(scene='06-role-and-limitation',observation='Enemy placement is not legible behind corridor walls in p4 samples.',repair='Give enemies actual world-depth order and sufficient projected height; add a second enemy to distinguish combination from a corridor alone.'),dict(scene='07-state-not-base',observation='The rising current-state token approaches the shared comparison label in p2 late.',repair='Raise the comparison label above the token motion envelope.'),dict(scene='09-condition-and-time',observation='Next-turn label, two-dice label and dice overlap. Current-effect text is obscured by its platform.',repair='Separate turn labels, dice label and current-effect note; render each text as a direct world sibling with its own opacity.'),dict(scene='11-cost-and-summary',observation='Moving tokens overlap the condition/test-path label around the middle node.',repair='Raise the independent summary label above the token envelope.')]
proof=dict(reviewedAt=now(),scope='All 74 planned prototype pixels/13 boards; not final voice timing or continuous whole animation.',videoPath=qa['videoPath'],videoSha256=qa['videoSha256'],allBoardsDirectlyRead=True,boards=qa['boards'],samples=qa['samples'],projectedFacesDepthOcclusionAndMotionObserved=True,unresolvedIssues=issues,prototypeStructuralPixelReviewApproved=False,captionReserveCounts=[x['captionReservePixelsAboveThreshold'] for x in qa['samples']],finalCuePixelsApproved=False,timingMeasured=False,humanListening='pending',localOnly=True,imagesGitAdded=0)
save(BASE/'black-structural-direct-review-v1.json',proof)
worker=(BASE/'extract-black-structural-qa-v1.py').read_text('utf-8').replace('v1','v2').replace("OUT=ROOT/'shared/output/character-parameters/black-structural-preview-v2'","OUT=ROOT/'shared/output/character-parameters/black-structural-preview-v1'").replace('8641','3601')
worker=worker.replace("scenes=read(BASE.parent/'script/narration.ko.json')['scenes']; samples=[]; groups=[]", "scenes=[s for s in read(BASE.parent/'script/narration.ko.json')['scenes'] if s['id'] in ['05-useful-strength','06-role-and-limitation','07-state-not-base','09-condition-and-time','11-cost-and-summary']]; samples=[]; groups=[]")
(BASE/'extract-black-structural-qa-v2.py').write_text(worker,'utf-8')
save(BASE/'prepared-structural-targeted-v2.json',dict(preparedAt=now(),review=rel(BASE/'black-structural-direct-review-v1.json'),targetScenes=[x['scene'] for x in issues],source=rel(source),sourceSha256=sha(source),scope='Only five changed prototype scenes, 12 seconds each; no voice/final timing/member rendering.',scopedTypecheckExitCode=0,foreignTypescriptApproval=False,rendered=False,allPixelsApproved=False))
print('Preserved exact v1 source and all74 reviewed samples; five targeted repairs prepared.')
